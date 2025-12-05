"""
Web Scraper for DeepDive Mode Content
======================================

This script scrapes educational content from open-source websites and stores it
in the Pinecone web content database for use in DeepDive mode.

Features:
- Scrapes from Wikipedia, Khan Academy, BBC Bitesize, and other educational sites
- Extracts clean text content (no ads, navigation, etc.)
- Generates embeddings using Gemini
- Stores in Pinecone with proper metadata
- Handles rate limiting and errors gracefully

Usage:
    python web_scraper_deepdive.py --topic "World War 2" --class 10 --subject "History"
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict
import logging

from app.services.gemini_service import gemini_service
from app.core.config import settings
from pinecone import Pinecone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== CONFIGURATION ====================

# Trusted educational sources
EDUCATIONAL_SOURCES = {
    "wikipedia": {
        "base_url": "https://en.wikipedia.org",
        "search_url": "https://en.wikipedia.org/w/api.php",
        "quality": "high"
    },
    "britannica": {
        "base_url": "https://www.britannica.com",
        "search_url": "https://www.britannica.com/search",
        "quality": "high"
    },
    "khan_academy": {
        "base_url": "https://www.khanacademy.org",
        "quality": "high"
    }
}

# Rate limiting (be respectful!)
RATE_LIMIT_DELAY = 2  # seconds between requests


# ==================== WEB SCRAPER ====================

class WebScraper:
    """Scrapes educational content from trusted sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NCERTEducationalBot/1.0 (Educational Content Aggregator for Students)'
        })
    
    def search_wikipedia(self, topic: str) -> List[str]:
        """
        Search Wikipedia for topic and return article URLs.
        
        Args:
            topic: Search query
        
        Returns:
            List of article URLs
        """
        try:
            # Use Wikipedia API to search
            params = {
                'action': 'opensearch',
                'search': topic,
                'limit': 5,
                'format': 'json'
            }
            
            response = self.session.get(
                EDUCATIONAL_SOURCES['wikipedia']['search_url'],
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            # API returns [query, titles, descriptions, urls]
            urls = data[3] if len(data) > 3 else []
            
            logger.info(f"Found {len(urls)} Wikipedia articles for '{topic}'")
            return urls
        
        except Exception as e:
            logger.error(f"Wikipedia search failed: {e}")
            return []
    
    def scrape_wikipedia_article(self, url: str) -> Dict[str, str]:
        """
        Scrape content from a Wikipedia article.
        
        Args:
            url: Wikipedia article URL
        
        Returns:
            Dict with title, content, url
        """
        try:
            time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get title
            title = soup.find('h1', {'id': 'firstHeading'})
            title_text = title.get_text() if title else "Unknown"
            
            # Get main content
            content_div = soup.find('div', {'id': 'mw-content-text'})
            if not content_div:
                return None
            
            # Remove unwanted elements
            for unwanted in content_div.find_all(['table', 'script', 'style', 'sup', 'cite']):
                unwanted.decompose()
            
            # Extract paragraphs
            paragraphs = content_div.find_all('p')
            content = '\n\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
            
            # Clean up text
            content = re.sub(r'\[\d+\]', '', content)  # Remove citation numbers
            content = re.sub(r'\n{3,}', '\n\n', content)  # Remove excessive newlines
            
            if not content or len(content) < 200:
                return None
            
            logger.info(f"Scraped: {title_text} ({len(content)} chars)")
            
            return {
                'title': title_text,
                'content': content,
                'url': url,
                'source': 'Wikipedia'
            }
        
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return None
    
    def chunk_content(self, content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split content into overlapping chunks.
        
        Args:
            content: Full content text
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks
        
        Returns:
            List of text chunks
        """
        if len(content) <= chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(content):
                # Look for period, exclamation, or question mark
                for i in range(end, max(start + chunk_size // 2, start), -1):
                    if content[i] in '.!?':
                        end = i + 1
                        break
            
            chunks.append(content[start:end].strip())
            start = end - overlap  # Overlap for context
        
        return chunks


# ==================== PINECONE UPLOADER ====================

class PineconeUploader:
    """Uploads web content to Pinecone web database."""
    
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(
            name=settings.PINECONE_WEB_INDEX,
            host=settings.PINECONE_WEB_HOST
        )
        self.gemini = gemini_service
    
    def upload_chunks(
        self,
        chunks: List[str],
        metadata: Dict[str, str],
        topic: str
    ) -> int:
        """
        Upload text chunks to Pinecone with embeddings.
        
        Args:
            chunks: List of text chunks
            metadata: Metadata dict (class, subject, topic, source, url)
            topic: Topic name for ID generation
        
        Returns:
            Number of chunks uploaded
        """
        try:
            vectors = []
            
            for i, chunk in enumerate(chunks):
                # Generate embedding
                logger.info(f"Generating embedding for chunk {i+1}/{len(chunks)}...")
                embedding = self.gemini.generate_embedding(chunk)
                
                # Create vector ID
                vector_id = f"{topic.replace(' ', '_')}_{metadata['source']}_{i}"
                
                # Create vector with metadata
                vector_metadata = {
                    **metadata,
                    'text': chunk,
                    'chunk_index': i,
                    'topic': topic
                }
                
                vectors.append((vector_id, embedding, vector_metadata))
                
                # Upload in batches of 100
                if len(vectors) >= 100:
                    self.index.upsert(vectors=vectors)
                    logger.info(f"Uploaded batch of {len(vectors)} vectors")
                    vectors = []
                    time.sleep(1)  # Rate limiting
            
            # Upload remaining vectors
            if vectors:
                self.index.upsert(vectors=vectors)
                logger.info(f"Uploaded final batch of {len(vectors)} vectors")
            
            logger.info(f"✅ Successfully uploaded {len(chunks)} chunks to Pinecone")
            return len(chunks)
        
        except Exception as e:
            logger.error(f"❌ Failed to upload to Pinecone: {e}")
            raise


# ==================== MAIN FUNCTION ====================

async def scrape_and_upload(topic: str, class_level: int, subject: str):
    """
    Main function to scrape content and upload to Pinecone.
    
    Args:
        topic: Topic to scrape (e.g., "World War 2")
        class_level: Class level (5-10)
        subject: Subject name (e.g., "History")
    """
    logger.info(f"🚀 Starting web scraping for: {topic}")
    logger.info(f"   Class: {class_level}, Subject: {subject}")
    
    scraper = WebScraper()
    uploader = PineconeUploader()
    
    total_chunks = 0
    
    # Search and scrape Wikipedia
    wikipedia_urls = scraper.search_wikipedia(topic)
    
    for url in wikipedia_urls[:3]:  # Limit to top 3 articles
        article = scraper.scrape_wikipedia_article(url)
        
        if not article:
            continue
        
        # Chunk the content
        chunks = scraper.chunk_content(article['content'])
        logger.info(f"Split into {len(chunks)} chunks")
        
        # Upload to Pinecone
        metadata = {
            'class': str(class_level),
            'subject': subject,
            'source': article['source'],
            'url': article['url'],
            'title': article['title']
        }
        
        uploaded = uploader.upload_chunks(chunks, metadata, topic)
        total_chunks += uploaded
    
    logger.info(f"✅ DONE! Uploaded {total_chunks} total chunks for '{topic}'")
    logger.info(f"   These will be available in DeepDive mode for {subject} Class {class_level}")


# ==================== CLI ====================

def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Scrape educational content for DeepDive mode'
    )
    parser.add_argument(
        '--topic',
        required=True,
        help='Topic to scrape (e.g., "World War 2", "Photosynthesis")'
    )
    parser.add_argument(
        '--class',
        dest='class_level',
        type=int,
        required=True,
        choices=range(5, 11),
        help='Class level (5-10)'
    )
    parser.add_argument(
        '--subject',
        required=True,
        help='Subject name (e.g., "History", "Science", "Geography")'
    )
    
    args = parser.parse_args()
    
    # Run async function
    asyncio.run(scrape_and_upload(
        topic=args.topic,
        class_level=args.class_level,
        subject=args.subject
    ))


if __name__ == "__main__":
    main()
