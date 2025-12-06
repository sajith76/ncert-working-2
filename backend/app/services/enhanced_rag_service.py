"""
Enhanced Multi-Index RAG Service

Implements intelligent cross-index retrieval:
- Basic Mode: Current class + relevant lower classes (textbook only)
- Deep Dive Mode: From fundamentals (earliest class) + web content for comprehensive understanding
"""

from app.services.gemini_service import gemini_service
from app.db.mongo import pinecone_db, pinecone_web_db
import logging
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class EnhancedRAGService:
    """
    Enhanced RAG service with multi-index progressive learning.
    
    Features:
    - Context-aware retrieval from multiple class levels
    - Two modes: Basic (quick answers) and Deep Dive (comprehensive from fundamentals)
    - Intelligent namespace/index routing
    """
    
    def __init__(self):
        self.gemini = gemini_service
        self.textbook_db = pinecone_db  # ncert-all-subjects index
        self.web_db = pinecone_web_db    # ncert-web-content index
        
        # Subject to namespace mapping for ncert-all-subjects index
        self.subject_namespaces = {
            "Mathematics": "mathematics",
            "Physics": "physics",
            "Chemistry": "chemistry",
            "Biology": "biology",
            "Social Science": "social_science",
            "History": "history",
            "Geography": "geography",
            "Civics": "civics",
            "Economics": "economics",
            "English": "english",
            "Hindi": "hindi"
        }
        
        # Class ranges for each subject
        self.subject_class_ranges = {
            "Mathematics": list(range(5, 13)),  # Class 5-12
            "Physics": list(range(11, 13)),     # Class 11-12
            "Chemistry": list(range(11, 13)),    # Class 11-12
            "Biology": list(range(11, 13)),      # Class 11-12
            "Social Science": list(range(5, 11)), # Class 5-10
            "History": list(range(5, 13)),       # Class 5-12
            "Geography": list(range(5, 13)),     # Class 5-12
            "Civics": list(range(5, 11)),        # Class 5-10
            "Economics": list(range(9, 13)),     # Class 9-12
            "English": list(range(5, 13)),       # Class 5-12
            "Hindi": list(range(5, 13))          # Class 5-12
        }
    
    def get_namespace(self, subject: str) -> str:
        """Get Pinecone namespace for subject"""
        return self.subject_namespaces.get(subject, subject.lower().replace(" ", "_"))
    
    def get_prerequisite_classes(
        self,
        subject: str,
        student_class: int,
        mode: str = "basic"
    ) -> List[int]:
        """
        Get list of classes to search based on mode.
        
        Args:
            subject: Subject name
            student_class: Student's current class
            mode: "basic" (current + recent lower) or "deepdive" (all from fundamentals)
        
        Returns:
            List of class numbers to search, ordered from earliest to current
        """
        available_classes = self.subject_class_ranges.get(subject, list(range(5, 13)))
        available_classes = [c for c in available_classes if c <= student_class]
        
        if mode == "basic":
            # Basic mode: Current class + 2 previous classes
            # Example: Class 10 → [8, 9, 10]
            prerequisite_range = 2
            start_class = max(available_classes[0], student_class - prerequisite_range)
            return [c for c in available_classes if start_class <= c <= student_class]
        
        else:  # deepdive mode
            # Deep dive: ALL classes from start to current
            # Example: Class 10 Math → [5, 6, 7, 8, 9, 10]
            return available_classes
    
    def query_multi_class(
        self,
        query_text: str,
        subject: str,
        student_class: int,
        chapter: Optional[int] = None,
        mode: str = "basic",
        chunks_per_class: int = 5
    ) -> Tuple[List[Dict], Dict[int, int]]:
        """
        Query across multiple class levels for progressive learning.
        
        Args:
            query_text: Student's question
            subject: Subject name
            student_class: Current class level
            chapter: Optional chapter filter (None for all chapters)
            mode: "basic" or "deepdive"
            chunks_per_class: Max chunks per class level
        
        Returns:
            Tuple of (chunks, class_distribution)
        """
        try:
            # Get embedding
            query_embedding = self.gemini.generate_embedding(query_text)
            
            # Get classes to search
            classes_to_search = self.get_prerequisite_classes(subject, student_class, mode)
            logger.info(f"🔍 {mode.upper()} mode: Searching classes {classes_to_search} for {subject}")
            
            # Get namespace
            namespace = self.get_namespace(subject)
            
            # Query each class level
            all_chunks = []
            class_distribution = {}
            
            for class_level in classes_to_search:
                # Build metadata filter
                metadata_filter = {
                    "class": class_level,  # Use integer for new system
                    "subject": subject
                }
                
                if chapter is not None:
                    metadata_filter["chapter"] = chapter
                
                try:
                    # Query textbook index with namespace
                    results = self.textbook_db.index.query(
                        namespace=namespace,
                        vector=query_embedding,
                        top_k=chunks_per_class,
                        filter=metadata_filter,
                        include_metadata=True
                    )
                    
                    # Extract matches
                    matches = results.get('matches', [])
                    class_chunks = 0
                    
                    for match in matches:
                        score = match.get('score', 0)
                        
                        # Dynamic threshold based on mode
                        threshold = 0.3 if mode == "basic" else 0.2
                        
                        if score >= threshold:
                            metadata = match.get('metadata', {})
                            chunk_data = {
                                'text': metadata.get('text', ''),
                                'class': class_level,
                                'subject': subject,
                                'chapter': metadata.get('chapter'),
                                'page': metadata.get('page'),
                                'score': score,
                                'source': 'textbook'
                            }
                            all_chunks.append(chunk_data)
                            class_chunks += 1
                    
                    if class_chunks > 0:
                        class_distribution[class_level] = class_chunks
                        logger.info(f"  ✓ Class {class_level}: {class_chunks} chunks (scores: {[round(m['score'], 2) for m in matches[:3]]})")
                
                except Exception as class_error:
                    logger.warning(f"  ✗ Class {class_level} query failed: {class_error}")
                    continue
            
            # Sort chunks: earlier classes first (for progressive building)
            all_chunks.sort(key=lambda x: (x['class'], -x['score']))
            
            logger.info(f"📊 Total chunks retrieved: {len(all_chunks)} from {len(class_distribution)} class levels")
            
            return all_chunks, class_distribution
            
        except Exception as e:
            logger.error(f"❌ Multi-class query failed: {e}")
            return [], {}
    
    def query_web_content(
        self,
        query_text: str,
        subject: str,
        student_class: int,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Query web content index for additional context (DeepDive mode).
        
        Args:
            query_text: Student's question
            subject: Subject name
            student_class: Current class level
            top_k: Number of results
        
        Returns:
            List of web content chunks
        """
        try:
            if not self.web_db or not self.web_db.index:
                logger.info("ℹ️ Web content DB not available")
                return []
            
            # Generate embedding
            query_embedding = self.gemini.generate_embedding(query_text)
            
            # Query web content index
            # Note: Web content may use broader metadata structure
            metadata_filter = {
                "subject": subject,
                # Don't filter by class for web content - get broader context
            }
            
            results = self.web_db.query(
                vector=query_embedding,
                top_k=top_k,
                filter=metadata_filter
            )
            
            web_chunks = []
            for match in results.get('matches', []):
                if match.get('score', 0) >= 0.5:  # Higher threshold for web content
                    metadata = match.get('metadata', {})
                    chunk_data = {
                        'text': metadata.get('text', ''),
                        'source': 'web',
                        'score': match.get('score', 0),
                        'url': metadata.get('url', 'N/A')
                    }
                    web_chunks.append(chunk_data)
            
            logger.info(f"🌐 Web content: {len(web_chunks)} chunks retrieved")
            return web_chunks
            
        except Exception as e:
            logger.warning(f"Web content query failed: {e}")
            return []
    
    def generate_basic_answer(
        self,
        question: str,
        textbook_chunks: List[Dict],
        class_distribution: Dict[int, int],
        student_class: int,
        subject: str
    ) -> str:
        """
        Generate basic mode answer using textbook content from multiple classes.
        
        Args:
            question: Student's question
            textbook_chunks: Retrieved chunks from multiple classes
            class_distribution: Number of chunks per class
            student_class: Student's current class
            subject: Subject name
        
        Returns:
            Generated answer
        """
        if not textbook_chunks:
            return f"I couldn't find relevant information in your {subject} textbooks. Try asking about specific topics from your chapters!"
        
        # Build context with class markers
        context_parts = []
        current_class = None
        
        for chunk in textbook_chunks[:15]:  # Limit to top 15 chunks
            chunk_class = chunk.get('class')
            
            # Add class header when switching classes
            if chunk_class != current_class:
                if chunk_class < student_class:
                    context_parts.append(f"\n**FROM CLASS {chunk_class} (Foundation):**\n")
                else:
                    context_parts.append(f"\n**FROM CLASS {chunk_class}:**\n")
                current_class = chunk_class
            
            context_parts.append(chunk['text'])
        
        combined_context = "\n\n".join(context_parts)
        
        # Build progressive note
        classes_used = sorted(class_distribution.keys())
        if len(classes_used) > 1:
            progressive_note = f"(Using content from Classes {', '.join(map(str, classes_used))} to build complete understanding)"
        else:
            progressive_note = ""
        
        # Generate answer
        prompt = f"""You are a helpful tutor for Class {student_class} {subject} students.

STUDENT QUESTION: {question}

TEXTBOOK CONTENT (Multiple Classes):
{combined_context}

{progressive_note}

INSTRUCTIONS:
1. Answer the question using ONLY the textbook content provided
2. If content is from multiple classes, build the answer progressively:
   - Start with foundational concepts from earlier classes
   - Build up to current class level understanding
3. Keep the answer clear and appropriate for Class {student_class} students
4. Use examples from the textbook if available
5. If the content from earlier classes helps explain basics, mention it naturally

Generate a clear, helpful answer:"""
        
        answer = self.gemini.generate_response(prompt)
        logger.info(f"✓ Basic answer generated ({len(answer)} chars)")
        
        return answer
    
    def generate_deepdive_answer(
        self,
        question: str,
        textbook_chunks: List[Dict],
        web_chunks: List[Dict],
        class_distribution: Dict[int, int],
        student_class: int,
        subject: str
    ) -> str:
        """
        Generate comprehensive deep dive answer starting from fundamentals.
        
        Args:
            question: Student's question
            textbook_chunks: Retrieved chunks from all prerequisite classes
            web_chunks: Retrieved web content chunks
            class_distribution: Number of textbook chunks per class
            student_class: Student's current class
            subject: Subject name
        
        Returns:
            Comprehensive answer
        """
        if not textbook_chunks and not web_chunks:
            return f"I couldn't find enough information to provide a comprehensive answer. Try asking about specific topics from your {subject} curriculum!"
        
        # Build layered context
        context_sections = []
        
        # Section 1: Textbook content (progressive from fundamentals)
        if textbook_chunks:
            textbook_context = []
            classes_used = sorted(set(chunk.get('class') for chunk in textbook_chunks))
            
            context_sections.append(f"**TEXTBOOK CONTENT (Classes {', '.join(map(str, classes_used))}):**\n")
            
            # Group by class for progressive building
            for class_level in classes_used:
                class_chunks = [c for c in textbook_chunks if c.get('class') == class_level][:5]
                
                if class_level < student_class:
                    textbook_context.append(f"\n--- Foundation from Class {class_level} ---")
                else:
                    textbook_context.append(f"\n--- Class {class_level} ---")
                
                for chunk in class_chunks:
                    textbook_context.append(chunk['text'])
            
            context_sections.append("\n\n".join(textbook_context))
        
        # Section 2: Web content (additional background)
        if web_chunks:
            context_sections.append("\n\n**ADDITIONAL CONTEXT (Background Information):**\n")
            web_context = [chunk['text'] for chunk in web_chunks[:5]]
            context_sections.append("\n\n".join(web_context))
        
        combined_context = "\n\n".join(context_sections)
        
        # Build comprehensive prompt
        earliest_class = min(class_distribution.keys()) if class_distribution else student_class
        
        prompt = f"""You are an expert tutor providing a COMPREHENSIVE explanation for a Class {student_class} {subject} student in DEEP DIVE mode.

STUDENT QUESTION: {question}

CONTENT (from Classes {earliest_class} to {student_class} + additional resources):
{combined_context}

DEEP DIVE MODE INSTRUCTIONS:
1. **Start from Fundamentals**: Begin with the most basic concept from the earliest class
2. **Progressive Building**: Build understanding step-by-step through class levels
3. **Comprehensive Coverage**: Address the "Wh-questions" - What, Why, When, Where, How (as applicable)
4. **Structure**:
   - 🌱 **Fundamentals** (if using content from Classes {earliest_class}-{student_class-1})
   - 📚 **Core Concept** (Class {student_class} level understanding)
   - 🔍 **Deep Dive** (comprehensive explanation with examples, applications, significance)
   - 💡 **Key Takeaways** (summarize main points)
5. **Make it engaging**: Use analogies, examples, and clear explanations
6. **Appropriate language**: Suitable for Class {student_class} students but comprehensive

Generate a thorough, well-structured deep dive explanation:"""
        
        answer = self.gemini.generate_response(prompt)
        logger.info(f"✓ Deep dive answer generated ({len(answer)} chars)")
        
        return answer
    
    # Main public methods
    
    def answer_question_basic(
        self,
        question: str,
        subject: str,
        student_class: int,
        chapter: Optional[int] = None
    ) -> Tuple[str, List[Dict]]:
        """
        Answer question in BASIC mode.
        Uses current class + recent lower classes (textbook only).
        
        Args:
            question: Student's question
            subject: Subject name
            student_class: Current class level
            chapter: Optional chapter filter
        
        Returns:
            Tuple of (answer, source_chunks)
        """
        logger.info(f"📚 BASIC MODE: Class {student_class} {subject}")
        logger.info(f"   Question: {question[:100]}...")
        
        # Query multi-class textbook content
        chunks, class_dist = self.query_multi_class(
            query_text=question,
            subject=subject,
            student_class=student_class,
            chapter=chapter,
            mode="basic",
            chunks_per_class=5
        )
        
        # Generate answer
        answer = self.generate_basic_answer(
            question=question,
            textbook_chunks=chunks,
            class_distribution=class_dist,
            student_class=student_class,
            subject=subject
        )
        
        return answer, chunks
    
    def answer_question_deepdive(
        self,
        question: str,
        subject: str,
        student_class: int,
        chapter: Optional[int] = None
    ) -> Tuple[str, List[Dict]]:
        """
        Answer question in DEEP DIVE mode.
        Starts from fundamentals (earliest available class) + web content.
        
        Args:
            question: Student's question
            subject: Subject name
            student_class: Current class level
            chapter: Optional chapter filter
        
        Returns:
            Tuple of (answer, combined_source_chunks)
        """
        logger.info(f"🔍 DEEP DIVE MODE: Class {student_class} {subject}")
        logger.info(f"   Question: {question[:100]}...")
        logger.info(f"   Will search from fundamentals (earliest class) to current class")
        
        # Query textbook content (all prerequisite classes)
        textbook_chunks, class_dist = self.query_multi_class(
            query_text=question,
            subject=subject,
            student_class=student_class,
            chapter=chapter,
            mode="deepdive",
            chunks_per_class=8  # More chunks per class for comprehensive coverage
        )
        
        # Query web content for additional context
        web_chunks = self.query_web_content(
            query_text=question,
            subject=subject,
            student_class=student_class,
            top_k=10
        )
        
        # Generate comprehensive answer
        answer = self.generate_deepdive_answer(
            question=question,
            textbook_chunks=textbook_chunks,
            web_chunks=web_chunks,
            class_distribution=class_dist,
            student_class=student_class,
            subject=subject
        )
        
        # Combine all chunks for source display
        all_chunks = textbook_chunks + web_chunks
        
        return answer, all_chunks


# Global instance
enhanced_rag_service = EnhancedRAGService()
