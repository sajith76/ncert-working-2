"""
Database connections for MongoDB Atlas and Pinecone Vector Database.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


# ==================== MONGODB ATLAS ====================

class MongoDB:
    """MongoDB Atlas connection manager."""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None
    
    async def connect(self):
        """Initialize MongoDB connection."""
        try:
            self.client = AsyncIOMotorClient(settings.MONGO_URI)
            self.db = self.client.ncert_learning
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("✅ Connected to MongoDB Atlas successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database."""
        return self.db[collection_name]


# Global MongoDB instance
mongodb = MongoDB()


# ==================== PINECONE VECTOR DATABASE ====================

class PineconeDB:
    """Pinecone Vector Database connection manager."""
    
    def __init__(self):
        self.pc = None
        self.index = None
    
    def connect(self):
        """Initialize Pinecone connection."""
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Connect to existing index
            self.index = self.pc.Index(
                name=settings.PINECONE_INDEX,
                host=settings.PINECONE_HOST
            )
            
            # Test connection by getting index stats
            stats = self.index.describe_index_stats()
            logger.info(f"✅ Connected to Pinecone successfully")
            logger.info(f"   Index: {settings.PINECONE_INDEX}")
            logger.info(f"   Total vectors: {stats.get('total_vector_count', 0)}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Pinecone: {e}")
            logger.warning("⚠️  Pinecone connection failed - RAG features will not work")
            logger.warning("   Please check PINECONE_HOST in .env file")
            logger.warning("   Get correct host from: https://app.pinecone.io/")
            # Don't raise - allow server to start without Pinecone
    
    def query(self, vector: list[float], top_k: int = 5, filter: dict = None):
        """
        Query Pinecone index with a vector.
        
        Args:
            vector: Query embedding vector
            top_k: Number of results to return
            filter: Metadata filter (e.g., {"class": 6, "subject": "Geography"})
        
        Returns:
            Query results from Pinecone
        """
        try:
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                filter=filter,
                include_metadata=True
            )
            return results
        except Exception as e:
            logger.error(f"❌ Pinecone query failed: {e}")
            raise
    
    def upsert(self, vectors: list[tuple]):
        """
        Upsert vectors into Pinecone index.
        
        Args:
            vectors: List of (id, vector, metadata) tuples
        """
        try:
            self.index.upsert(vectors=vectors)
            logger.info(f"✅ Upserted {len(vectors)} vectors to Pinecone")
        except Exception as e:
            logger.error(f"❌ Pinecone upsert failed: {e}")
            raise


# Global Pinecone instance
pinecone_db = PineconeDB()


# ==================== DATABASE INITIALIZATION ====================

async def init_databases():
    """Initialize all database connections."""
    logger.info("Initializing database connections...")
    
    # Connect to MongoDB
    await mongodb.connect()
    
    # Connect to Pinecone
    pinecone_db.connect()
    
    logger.info("✅ All databases initialized successfully")


async def close_databases():
    """Close all database connections."""
    logger.info("Closing database connections...")
    await mongodb.close()
    logger.info("✅ All databases closed")


# ==================== HELPER FUNCTIONS ====================

def get_notes_collection():
    """Get notes collection from MongoDB."""
    return mongodb.get_collection("notes")


def get_evaluations_collection():
    """Get evaluations collection from MongoDB."""
    return mongodb.get_collection("evaluations")


def get_assessments_collection():
    """Get assessments collection from MongoDB."""
    return mongodb.get_collection("assessments")


def get_quiz_results_collection():
    """Get quiz results collection from MongoDB."""
    return mongodb.get_collection("quiz_results")
