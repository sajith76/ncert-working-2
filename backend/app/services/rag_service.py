"""
RAG Service - Handles Retrieval-Augmented Generation using Pinecone + Gemini.
Production-grade implementation with strict RAG enforcement.
"""

from app.services.gemini_service import gemini_service
from app.db.mongo import pinecone_db
import logging
import re

logger = logging.getLogger(__name__)


# Greeting patterns and responses (NO Gemini call)
GREETINGS = {
    "hi": ["hi", "hello", "hey", "yo", "hii", "hiiii", "hey there", "hi buddy", "helo", "hellow"],
    "bye": ["bye", "good bye", "goodbye", "see you", "see you later", "see ya", "cya"],
    "thanks": ["thank you", "thanks", "thankyou", "thx", "thank u"],
    "ok": ["ok", "okay", "fine", "good", "alright", "cool"],
    "how_are_you": ["how are you", "how r u", "what's up", "sup", "whats up", "wassup"]
}

GREETING_RESPONSES = {
    "hi": "Hey there! What do you want to learn today?",
    "bye": "See you soon! Keep learning!",
    "thanks": "You're welcome! Happy learning!",
    "ok": "Great! Is there anything else you'd like to learn?",
    "how_are_you": "I'm here and ready to help you learn!"
}

# Similarity threshold for RAG results
SIMILARITY_THRESHOLD = 0.3  # Lowered for better recall


class RAGService:
    """Service for RAG-based retrieval and answer generation."""
    
    def __init__(self):
        self.gemini = gemini_service
        self.pinecone = pinecone_db
    
    @staticmethod
    def detect_greeting(text: str) -> str | None:
        """
        Detect if user input is a greeting.
        Returns response if greeting detected, None otherwise.
        
        Args:
            text: User input (normalized)
        
        Returns:
            Greeting response or None
        """
        text_lower = text.lower().strip()
        
        for greeting_type, patterns in GREETINGS.items():
            for pattern in patterns:
                if text_lower == pattern or text_lower.startswith(pattern + " "):
                    return GREETING_RESPONSES[greeting_type]
        
        return None
    
    def query_with_rag(
        self,
        query_text: str,
        class_level: int,
        subject: str,
        chapter: int,
        mode: str,
        top_k: int = 10  # Increased from 5 to 10 for better coverage
    ) -> tuple[str, list[str]]:
        """
        Query Pinecone with embeddings and generate answer using Gemini.
        Implements strict RAG enforcement with greeting detection.
        
        Args:
            query_text: Student's highlighted text/question
            class_level: Class (5-10)
            subject: Subject name
            chapter: Chapter number
            mode: Explanation mode
            top_k: Number of chunks to retrieve
        
        Returns:
            Tuple of (answer, source_chunks)
        """
        try:
            # Step 1: Normalize input
            query_normalized = query_text.strip()
            
            # Step 2: Check for greetings (NO Gemini call)
            greeting_response = self.detect_greeting(query_normalized)
            if greeting_response:
                logger.info("Greeting detected - returning canned response")
                return greeting_response, []
            
            # Step 3: Generate embedding for query
            logger.info(f"Generating embedding for: {query_text[:50]}...")
            query_embedding = self.gemini.generate_embedding(query_text)
            
            # Step 4: Query Pinecone with metadata filter
            # Note: Metadata uses 'lesson_number' not 'chapter'
            # Note: 'class' is stored as STRING not integer
            metadata_filter = {
                "class": str(class_level),  # Convert to string to match uploaded metadata
                "subject": subject,
                # Map chapter to lesson_number (formatted as "01", "02", etc.)
                "lesson_number": f"{chapter:02d}"
            }
            
            logger.info(f"Querying Pinecone with filter: {metadata_filter}")
            results = self.pinecone.query(
                vector=query_embedding,
                top_k=top_k,
                filter=metadata_filter
            )
            
            # Step 5: Similarity check - strict threshold
            matches = results.get('matches', [])
            
            if not matches:
                logger.warning("No matching chunks found in Pinecone")
                return "No answer found in the book.", []
            
            # Log all match scores
            logger.info(f"Found {len(matches)} matches with scores: {[m.get('score', 0) for m in matches]}")
            
            # Filter by similarity threshold
            valid_matches = [m for m in matches if m.get('score', 0) >= SIMILARITY_THRESHOLD]
            
            if not valid_matches:
                logger.warning(f"All matches below similarity threshold ({SIMILARITY_THRESHOLD})")
                return "No answer found in the book.", []
            
            # Step 6: Extract text chunks from valid results
            chunks = []
            for match in valid_matches:
                if 'metadata' in match and 'text' in match['metadata']:
                    text = match['metadata']['text']
                    # Filter out junk chunks (page numbers, headers, etc.)
                    if len(text) > 50 and not text.startswith('1000 m2000'):  # Skip pagination artifacts
                        chunks.append(text)
            
            logger.info(f"Extracted {len(chunks)} text chunks from valid matches")
            
            if not chunks:
                logger.warning("No text content in matched chunks")
                return "No answer found in the book.", []
            
            # Step 7: Combine chunks into context
            context = "\n\n---\n\n".join(chunks)
            logger.info(f"Context length: {len(context)} chars, Preview: {context[:150]}...")
            
            # Step 8: Generate answer using Gemini
            logger.info(f"Generating {mode} explanation using Gemini for Class {class_level}...")
            logger.info(f"Context preview: {context[:200]}...")
            
            try:
                answer = self.gemini.format_explanation(
                    context=context,
                    question=query_text,
                    mode=mode,
                    class_level=class_level  # Pass class level for language adjustment
                )
                logger.info(f"✓ Gemini response received: {len(answer)} chars - '{answer[:100]}...'")
            except Exception as e:
                logger.error(f"❌ Gemini generation failed: {type(e).__name__}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                answer = "No answer found in the book."
            
            return answer, chunks
        
        except Exception as e:
            logger.error(f"❌ RAG query failed: {e}")
            raise
    
    def retrieve_chapter_context(
        self,
        class_level: int,
        subject: str,
        chapter: int,
        max_chunks: int = 20
    ) -> str:
        """
        Retrieve full chapter context from Pinecone for MCQ generation.
        
        Args:
            class_level: Class (5-10)
            subject: Subject name
            chapter: Chapter number
            max_chunks: Maximum chunks to retrieve
        
        Returns:
            Combined chapter text
        """
        try:
            # Use a generic query to get chapter content
            dummy_query = f"{subject} chapter {chapter}"
            query_embedding = self.gemini.generate_embedding(dummy_query)
            
            metadata_filter = {
                "class": str(class_level),  # Convert to string
                "subject": subject,
                "lesson_number": f"{chapter:02d}"
            }
            
            results = self.pinecone.query(
                vector=query_embedding,
                top_k=max_chunks,
                filter=metadata_filter
            )
            
            # Extract and combine chunks
            chunks = []
            for match in results.get('matches', []):
                if 'metadata' in match and 'text' in match['metadata']:
                    chunks.append(match['metadata']['text'])
            
            if not chunks:
                raise ValueError(f"No content found for Class {class_level}, {subject}, Chapter {chapter}")
            
            return "\n\n".join(chunks)
        
        except Exception as e:
            logger.error(f"❌ Chapter context retrieval failed: {e}")
            raise


# Global RAG service instance
rag_service = RAGService()
