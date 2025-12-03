"""
Chat Router - RAG-based chat endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.services.rag_service import rag_service
from app.services.gemini_service import gemini_service
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
    - `define`: Clear definitions and meanings
    - `elaborate`: Detailed explanation with examples and context
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


# ==================== STICK FLOW ENDPOINT ====================

class StickFlowRequest(BaseModel):
    """Request schema for Stick Flow visual diagram generation."""
    highlight_text: str = Field(..., description="Text to create flow diagram for")
    class_level: int = Field(..., ge=5, le=10, description="Class level (5-10)")
    subject: str = Field(..., description="Subject name")
    chapter: int = Field(..., ge=1, description="Chapter number")


class StickFlowResponse(BaseModel):
    """Response schema for Stick Flow."""
    imageUrl: str = Field(..., description="Generated flow diagram image URL")
    description: str = Field(None, description="Optional description of the flow")


@router.post("/stick-flow", response_model=StickFlowResponse)
async def generate_stick_flow(request: StickFlowRequest):
    """
    Generate visual flow diagram using Gemini image generation.
    
    Creates a step-by-step flow diagram of the concept using ONLY textbook content.
    The image will be a clean, attractive visual representation focusing solely on
    the content without extraneous elements.
    """
    try:
        logger.info(f"Stick Flow request: Class {request.class_level}, {request.subject}, Ch. {request.chapter}")
        
        # Get context from RAG
        context = rag_service.retrieve_chapter_context(
            class_level=request.class_level,
            subject=request.subject,
            chapter=request.chapter,
            max_chunks=15
        )
        
        # Build flow diagram generation prompt with strict constraints
        flow_prompt = f"""Create a visual flow diagram for Class {request.class_level} students.

**TEXTBOOK CONTENT:**
{context[:2000]}

**CONCEPT TO VISUALIZE:**
{request.highlight_text}

**STRICT REQUIREMENTS:**
1. Create a clear, step-by-step flow diagram
2. Use ONLY information from the textbook content above
3. Make it visually attractive with:
   - Clear boxes/shapes for each step
   - Arrows showing flow/sequence
   - Simple icons or symbols where appropriate
   - Color coding for different types of steps
4. Keep text minimal - use keywords and short phrases
5. Focus ONLY on the concept - no decorative elements, backgrounds, or unrelated content
6. Make it suitable for Class {request.class_level} students
7. Layout should be vertical or horizontal flowchart style

**OUTPUT:**
A clean, professional flow diagram that a student can use for quick revision.
"""
        
        # Generate image using Gemini (using text-to-image capability)
        # For now, we'll generate a text description and return a placeholder
        # In production, you'd integrate with an actual image generation service
        
        description_prompt = f"""Based on this textbook content:

{context[:1500]}

Create a brief description (2-3 sentences) of how to visualize "{request.highlight_text}" as a flow diagram.
Focus on the steps and connections."""

        description = gemini_service.generate_response(description_prompt)
        
        # TODO: Integrate actual image generation
        # For now, return a placeholder
        image_url = f"https://via.placeholder.com/800x600/6366f1/ffffff?text=Flow+Diagram:+{request.highlight_text[:30]}"
        
        logger.info(f"✅ Stick Flow generated successfully")
        
        return StickFlowResponse(
            imageUrl=image_url,
            description=description
        )
    
    except Exception as e:
        logger.error(f"❌ Stick Flow error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== STUDENT CHATBOT ENDPOINT ====================

class StudentChatRequest(BaseModel):
    """Request schema for student chatbot."""
    question: str = Field(..., description="Student's question")
    class_level: int = Field(..., ge=5, le=10, description="Class level (5-10)")
    subject: str = Field(..., description="Subject name")
    chapter: int = Field(..., ge=1, description="Chapter number")


@router.post("/student", response_model=ChatResponse)
async def student_chatbot(request: StudentChatRequest):
    """
    Open student chatbot endpoint with RAG.
    
    Handles any student question about the chapter. Uses Pinecone RAG to retrieve
    relevant content and formats responses appropriately. Strictly enforces that
    only textbook content is used - questions outside the book are politely declined.
    """
    try:
        logger.info(f"Student chat: Class {request.class_level}, {request.subject}, Ch. {request.chapter}")
        logger.info(f"Question: {request.question[:100]}...")
        
        # Use elaborate mode for comprehensive answers
        answer, source_chunks = rag_service.query_with_rag(
            query_text=request.question,
            class_level=request.class_level,
            subject=request.subject,
            chapter=request.chapter,
            mode="elaborate",  # Detailed explanation mode
            top_k=15  # More context for better answers
        )
        
        return ChatResponse(
            answer=answer,
            used_mode="elaborate",
            source_chunks=source_chunks
        )
    
    except Exception as e:
        logger.error(f"❌ Student chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
