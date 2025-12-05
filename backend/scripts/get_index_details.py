"""
Get Pinecone index details including the host URL.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pinecone import Pinecone
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_index_details():
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    
    logger.info("Fetching Pinecone index details...\n")
    
    for index_info in pc.list_indexes():
        logger.info(f"Index: {index_info.name}")
        logger.info(f"Host: {index_info.host}")
        logger.info(f"Dimension: {index_info.dimension}")
        logger.info(f"Metric: {index_info.metric}")
        logger.info("-" * 70)

if __name__ == "__main__":
    get_index_details()
