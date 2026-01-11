"""
Annotation Router - Text annotation with AI assistance (Define, Elaborate, Flow)

Supports multilingual input/output - responds in the same language as the selected text.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Literal
from app.services.enhanced_rag_service import enhanced_rag_service
from app.services.gemini_service import gemini_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/annotation",
    tags=["Annotation"]
)


def detect_text_language(text: str) -> str:
    """Detect language of the selected text and return language instruction."""
    try:
        from app.services.openvino_multilingual_service import multilingual_service
        lang, confidence = multilingual_service.detect_language_with_confidence(text)
        
        lang_names = {
            "hi": "Hindi",
            "ur": "Urdu",
            "ta": "Tamil",
            "te": "Telugu",
            "bn": "Bengali",
            "mr": "Marathi",
            "gu": "Gujarati",
            "kn": "Kannada",
            "ml": "Malayalam",
            "pa": "Punjabi",
            "ar": "Arabic",
            "en": "English"
        }
        
        if lang != "en" and confidence > 0.5:
            lang_name = lang_names.get(lang, lang.upper())
            return f"\n\n**IMPORTANT: The input text is in {lang_name}. You MUST respond entirely in {lang_name} using the same script.**"
        return ""
    except:
        return ""


class AnnotationRequest(BaseModel):
    """Request schema for annotation AI actions."""
    selected_text: str = Field(..., description="Text selected by user for annotation")
    action: Literal["define", "elaborate", "stick_flow"] = Field(..., description="AI action to perform")
    class_level: int = Field(..., ge=5, le=12, description="Student's class level")
    subject: str = Field(..., description="Subject name (Mathematics, Physics, etc.)")
    chapter: int | None = Field(None, ge=1, description="Optional chapter number")
    image_data: str | None = Field(None, description="Optional base64 image data for screenshot doubts")


def extract_text_from_image(image_data: str, language_hint: str = None) -> str:
    """
    Extract text from base64 image using Multilingual OCR Service.
    Uses EasyOCR for Hindi/Indic scripts, OpenVINO for English.
    Runs locally - NO API calls needed!
    
    Args:
        image_data: Base64 encoded image
        language_hint: Optional language hint (e.g., 'hi' for Hindi, 'en' for English)
    """
    import base64
    import io
    import numpy as np
    
    try:
        # Remove data URL prefix if present
        if image_data.startswith('data:'):
            image_data = image_data.split(',', 1)[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        
        # Use Multilingual OCR Service (EasyOCR + OpenVINO, runs locally)
        try:
            from app.services.multilingual_ocr_service import get_multilingual_ocr_service
            from PIL import Image
            
            # Convert image bytes to numpy array
            img = Image.open(io.BytesIO(image_bytes))
            img_array = np.array(img)
            
            # Get multilingual OCR service
            ocr_service = get_multilingual_ocr_service()
            
            if ocr_service.is_available():
                # Extract text with language hint if provided
                text, detected_lang = ocr_service.extract_text(img_array, language_hint=language_hint)
                
                if text and text.strip():
                    logger.info(f"   ✅ Multilingual OCR extracted ({detected_lang}): '{text[:100]}...'")
                    return text.strip()
                else:
                    logger.warning("   ⚠️ Multilingual OCR found no text")
                    return None
            else:
                logger.warning("   ⚠️ Multilingual OCR service not available")
                return None
                
        except ImportError as e:
            logger.warning(f"Multilingual OCR import error: {e}")
            return None
        except Exception as e:
            logger.warning(f"Multilingual OCR error: {e}")
            return None
        
    except Exception as e:
        logger.error(f"Image processing error: {e}")
        return None


class AnnotationResponse(BaseModel):
    """Response schema for annotation."""
    answer: str = Field(..., description="AI-generated response")
    action_type: str = Field(..., description="Type of action performed")
    source_count: int = Field(..., description="Number of sources used")


@router.post("/", response_model=AnnotationResponse)
async def process_annotation(request: AnnotationRequest):
    """
    🎯 Process annotation request with AI assistance.
    
    **Actions:**
    - `define`: Quick, accurate definition from textbook
    - `elaborate`: Detailed explanation with examples  
    - `stick_flow`: Text-based flow diagram showing concept breakdown
    
    **Cost-Efficient Design:**
    - Uses RAG for context (reduces Gemini tokens)
    - Targeted prompts for specific actions
    - No image generation (text-based flows)
    
    **Edge Case Handling:**
    - Class 11-12: Limited content available (graceful fallback)
    - Missing content: Searches earlier classes for foundation
    - No matches: Uses Gemini general knowledge with disclaimer
    """
    try:
        # Determine the text to process
        query_text = request.selected_text
        
        # Map subject to language hint for OCR
        # Physics, Chemistry, Biology, Math, etc. use English textbooks
        subject_to_lang = {
            # Indian languages
            "hindi": "hi",
            "urdu": "ur",
            "tamil": "ta",
            "telugu": "te",
            "bengali": "bn",
            "marathi": "mr",
            "gujarati": "gu",
            "kannada": "kn",
            "malayalam": "ml",
            "punjabi": "pa",
            # English subjects (explicitly set to avoid auto-detect issues)
            "english": "en",
            "physics": "en",
            "chemistry": "en",
            "biology": "en",
            "mathematics": "en",
            "math": "en",
            "maths": "en",
            "social science": "en",
            "history": "en",
            "geography": "en",
            "civics": "en",
            "economics": "en",
            "science": "en",
        }
        language_hint = subject_to_lang.get(request.subject.lower(), "en")  # Default to English
        
        # If image data is provided, extract text from it using OCR
        if request.image_data:
            logger.info(f"📷 Screenshot doubt received, extracting text...")
            logger.info(f"   Using language hint: {language_hint or 'auto-detect'}")
            extracted_text = extract_text_from_image(request.image_data, language_hint=language_hint)
            
            if extracted_text:
                query_text = extracted_text
                logger.info(f"   OCR extracted: '{query_text[:100]}...'")
            else:
                # Fallback to using Gemini vision (future enhancement)
                logger.info(f"   OCR failed, using original query text")
        
        logger.info(f"📝 Annotation request: {request.action.upper()} for '{query_text[:50]}...'")
        logger.info(f"   Class {request.class_level}, {request.subject}")
        
        # Detect input language for multilingual response
        lang_instruction = detect_text_language(query_text)
        if lang_instruction:
            logger.info(f"   🌐 Detected non-English input, will respond in same language")
        
        # EDGE CASE: Check class availability
        # Currently we have comprehensive data for Classes 5-10
        # Classes 11-12 have limited content
        if request.class_level > 10:
            logger.warning(f"⚠️ Class {request.class_level} requested (limited content available)")
            # Don't block the request - let the RAG system try to find content
            # If not found, it will fall back to general knowledge
        
        # Get relevant context from textbook using RAG
        if request.action == "define":
            # Quick mode: Current + 2 previous classes WITH lower LLM reuse threshold
            answer, source_chunks = enhanced_rag_service.answer_annotation_basic(
                question=f"Define: {query_text}",
                subject=request.subject,
                student_class=request.class_level,
                chapter=request.chapter
            )
            
            # Determine the response language based on subject
            subject_lower = request.subject.lower()
            is_hindi_subject = subject_lower == "hindi"
            is_urdu_subject = subject_lower == "urdu"
            
            # Create language instruction based on subject
            if is_hindi_subject:
                language_instruction = """
⚠️ CRITICAL: You MUST respond ONLY in Hindi using DEVANAGARI script (देवनागरी लिपि)
- Example: क, ख, ग, घ, च, छ, ज, झ
- Write like this: "यह एक उदाहरण है"
- DO NOT use Urdu/Arabic script"""
                format_example = """**परिभाषा:** [Explanation in Hindi Devanagari]

**मुख्य बिंदु:**
• [Point 1 in Hindi]
• [Point 2 in Hindi]"""
            elif is_urdu_subject:
                language_instruction = """
⚠️ CRITICAL: You MUST respond in Urdu using NASTALIQ script
- Write right-to-left in Urdu/Arabic script
- Example: یہ ایک مثال ہے"""
                format_example = """**تعریف:** [Explanation in Urdu]

**اہم نکات:**
• [Point 1 in Urdu]
• [Point 2 in Urdu]"""
            else:
                # Default: English for Physics, Chemistry, Biology, Mathematics, etc.
                language_instruction = ""  # No special instruction, respond in English
                format_example = """**Definition:** [Clear explanation in English]

**Key Points:**
• [Point 1]
• [Point 2]
• [Point 3]"""
            
            # Generate better definition using Gemini
            if source_chunks:
                context = "\n\n".join([chunk.get('text', '')[:500] for chunk in source_chunks[:3]])
                
                prompt = f"""You are a helpful tutor for Class {request.class_level} {request.subject} students.
{language_instruction}
**Student's Query:** {query_text}

**Textbook Content:**
{context}

**Instructions:**
1. Provide a clear, simple definition or explanation
2. Use bullet points for key concepts
3. Keep it concise (under 150 words)
4. Make it easy for a Class {request.class_level} student to understand
{'5. RESPOND ONLY IN HINDI USING DEVANAGARI SCRIPT' if is_hindi_subject else ('5. RESPOND IN URDU USING NASTALIQ SCRIPT' if is_urdu_subject else '5. RESPOND IN ENGLISH')}

**Format your response as:**
{format_example}
{lang_instruction}"""
                
                answer = gemini_service.generate_response(prompt)
            else:
                # No textbook content found - provide general explanation
                prompt = f"""You are a helpful tutor for Class {request.class_level} {request.subject} students.
{language_instruction}
The student selected this text and wants to understand it:
"{query_text}"

Since no specific textbook content was found, provide a helpful explanation:
1. Explain what this text/concept means
2. Keep it simple for Class {request.class_level}
{'3. RESPOND ONLY IN HINDI USING DEVANAGARI SCRIPT' if is_hindi_subject else ('3. RESPOND IN URDU USING NASTALIQ SCRIPT' if is_urdu_subject else '3. RESPOND IN ENGLISH')}
4. Be concise (under 150 words)

Format:
{format_example}"""
                
                answer = gemini_service.generate_response(prompt)
        
        elif request.action == "elaborate":
            # Deep dive mode: Comprehensive explanation
            answer, source_chunks = enhanced_rag_service.answer_question_deepdive(
                question=f"Explain in detail: {query_text}",
                subject=request.subject,
                student_class=request.class_level,
                chapter=request.chapter
            )
            
            # Determine the response language based on subject
            subject_lower = request.subject.lower()
            is_hindi_subject = subject_lower == "hindi"
            is_urdu_subject = subject_lower == "urdu"
            
            # Create language instruction based on subject
            if is_hindi_subject:
                language_instruction = """
⚠️ CRITICAL: You MUST respond ONLY in Hindi using DEVANAGARI script (देवनागरी लिपि)
- Write like this: "यह एक उदाहरण है"
- DO NOT use Urdu/Arabic script"""
                format_example = """**परिचय:** [Introduction in Hindi]
**विस्तार:** [Explanation in Hindi]
**उदाहरण:** [Examples in Hindi]"""
            elif is_urdu_subject:
                language_instruction = """
⚠️ CRITICAL: You MUST respond in Urdu using NASTALIQ script
- Write right-to-left in Urdu/Arabic script"""
                format_example = """**تعارف:** [Introduction in Urdu]
**تفصیل:** [Explanation in Urdu]
**مثال:** [Examples in Urdu]"""
            else:
                # Default: English for Physics, Chemistry, Biology, Mathematics, etc.
                language_instruction = ""
                format_example = """**Introduction:** [What is it?]
**Explanation:** [Detailed breakdown]
**Examples:** [If applicable]"""
            
            # Generate detailed explanation
            if source_chunks:
                context = "\n\n".join([chunk.get('text', '')[:800] for chunk in source_chunks[:5]])
                
                prompt = f"""You are a helpful tutor for Class {request.class_level} {request.subject} students.
{language_instruction}
**Student wants detailed explanation of:** {query_text}

**Textbook Content:**
{context}

**Instructions:**
1. Start with a brief introduction
2. Explain the concept step-by-step
3. Include examples where possible
4. Use simple, engaging language for Class {request.class_level}
{'5. RESPOND ONLY IN HINDI USING DEVANAGARI SCRIPT' if is_hindi_subject else ('5. RESPOND IN URDU' if is_urdu_subject else '5. RESPOND IN ENGLISH')}
6. Keep it under 400 words

**Format:**
{format_example}"""
                
                answer = gemini_service.generate_response(prompt)
            else:
                # No content found - provide helpful response
                prompt = f"""You are a tutor for Class {request.class_level} {request.subject}.
{language_instruction}
The student wants to understand: "{query_text}"

Provide a helpful explanation even though specific textbook content wasn't found:
1. Explain the concept in simple terms
{'2. RESPOND ONLY IN HINDI USING DEVANAGARI SCRIPT' if is_hindi_subject else ('2. RESPOND IN URDU' if is_urdu_subject else '2. RESPOND IN ENGLISH')}
3. Keep it educational and age-appropriate
4. Note that this is general knowledge, not from their specific textbook"""
                
                answer = gemini_service.generate_response(prompt)
        
        elif request.action == "stick_flow":
            # Generate text-based flow diagram WITH lower LLM reuse threshold
            answer, source_chunks = enhanced_rag_service.answer_annotation_basic(
                question=f"Explain the flow/process of: {query_text}",
                subject=request.subject,
                student_class=request.class_level,
                chapter=request.chapter
            )
            
            if source_chunks:
                context = "\n\n".join([chunk.get('text', '')[:600] for chunk in source_chunks[:4]])
                
                prompt = f"""Based on the textbook content below, create a clear TEXT-BASED flow diagram for "{query_text}" suitable for a Class {request.class_level} student.

**Textbook Content:**
{context}

**Instructions:**
1. Create a step-by-step flow using text and arrows
2. Use these symbols: ↓ → ← ↑ ⟶ ⟵ 
3. Keep each step brief (5-8 words max)
4. Show relationships and progression clearly
5. Use boxes made with text characters
6. Make it easy to copy-paste and study from
7. Limit to 5-8 major steps
8. Use ONLY information from the textbook content

**Format Example:**
```
┌─────────────────────┐
│   Starting Point    │
└─────────────────────┘
          ↓
┌─────────────────────┐
│   Key Process       │
└─────────────────────┘
          ↓
    ┌─────┴─────┐
    ↓           ↓
┌───────┐   ┌───────┐
│ Path A│   │ Path B│
└───────┘   └───────┘
```

Generate a similar flow diagram for "{query_text}":{lang_instruction}"""
                
                answer = gemini_service.generate_response(prompt)
            else:
                answer = f"""No flow information found in the book.

Try asking about:
• Specific processes or procedures
• Step-by-step concepts
• Sequential topics

Current search: "{request.selected_text}" in Class {request.class_level} {request.subject}"""
        
        logger.info(f"✅ Annotation processed: {len(answer)} chars, {len(source_chunks)} sources")
        
        return AnnotationResponse(
            answer=answer,
            action_type=request.action,
            source_count=len(source_chunks)
        )
    
    except Exception as e:
        logger.error(f"❌ Annotation error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-define")
async def quick_define(
    text: str = Query(..., description="Text to define"),
    class_level: int = Query(..., ge=5, le=12),
    subject: str = Query(..., description="Subject name")
):
    """
    ⚡ Ultra-fast definition endpoint (optimized for speed).
    
    Returns just the definition without extra processing.
    Perfect for quick lookups while reading.
    """
    try:
        # Use basic RAG with minimal chunks
        answer, source_chunks = enhanced_rag_service.answer_question_basic(
            question=f"What is {text}?",
            subject=subject,
            student_class=class_level,
            chapter=None
        )
        
        if source_chunks:
            # Quick definition extraction
            context = source_chunks[0].get('text', '')[:300]
            
            prompt = f"""Give a one-sentence definition of "{text}" based on this textbook excerpt:

{context}

Definition:"""
            
            definition = gemini_service.generate_response(prompt)
            
            return {"definition": definition.strip()}
        else:
            return {"definition": f"Term '{text}' not found in textbook."}
    
    except Exception as e:
        logger.error(f"Quick define error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
