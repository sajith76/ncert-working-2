"""
Chat Router - RAG-based chat endpoints.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.services.rag_service import rag_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat / RAG"]
)


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    RAG-based chat endpoint.
    
    Retrieves relevant context from Pinecone based on class, subject, and chapter,
    then generates an explanation using Gemini based on the selected mode.
    
    **Modes:**
    - `simple`: Simplest explanation
    - `meaning`: Definitions and meanings
    - `story`: Narrative format
    - `example`: Practical examples
    - `summary`: Concise summary
    """
    try:
        logger.info(f"Chat request: Class {request.class_level}, {request.subject}, Ch. {request.chapter}, Mode: {request.mode}")
        
        # Query RAG system
        answer, source_chunks = rag_service.query_with_rag(
            query_text=request.highlight_text,
            class_level=request.class_level,
            subject=request.subject,
            chapter=request.chapter,
            mode=request.mode
        )
        
        return ChatResponse(
            answer=answer,
            used_mode=request.mode,
            source_chunks=source_chunks
        )
    
    except Exception as e:
        logger.error(f"❌ Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
