"""
Assessment Router - Voice assessment endpoints for generating questions and evaluating answers.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from app.services.rag_service import rag_service
from app.services.gemini_service import gemini_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/assessment",
    tags=["Assessment"]
)


# ==================== REQUEST/RESPONSE MODELS ====================

class QuestionRequest(BaseModel):
    """Request schema for generating assessment questions."""
    class_level: int = Field(..., ge=5, le=10, description="Class level (5-10)")
    subject: str = Field(..., description="Subject name")
    chapter: int = Field(..., ge=1, description="Chapter number")
    num_questions: int = Field(3, ge=1, le=5, description="Number of questions (1-5)")


class QuestionResponse(BaseModel):
    """Response schema for generated questions."""
    questions: List[str] = Field(..., description="List of generated questions")
    chapter: int = Field(..., description="Chapter number")
    subject: str = Field(..., description="Subject name")


class Answer(BaseModel):
    """Single Q&A pair."""
    question: str = Field(..., description="The question asked")
    answer: str = Field(..., description="Student's answer (transcribed from voice)")
    timestamp: str = Field(None, description="Optional timestamp")


class EvaluationRequest(BaseModel):
    """Request schema for evaluating answers."""
    class_level: int = Field(..., ge=5, le=10, description="Class level (5-10)")
    subject: str = Field(..., description="Subject name")
    chapter: int = Field(..., ge=1, description="Chapter number")
    answers: List[Answer] = Field(..., description="List of Q&A pairs to evaluate")


class EvaluationResponse(BaseModel):
    """Response schema for evaluation."""
    score: int = Field(..., ge=0, le=100, description="Overall score (0-100)")
    feedback: str = Field(..., description="AI-generated feedback")
    strengths: List[str] = Field(..., description="Student's strengths")
    improvements: List[str] = Field(..., description="Areas for improvement")
    question_scores: List[dict] = Field(default=[], description="Per-question performance")
    topics_to_study: List[str] = Field(default=[], description="Topics to review based on weak areas")


# ==================== ENDPOINTS ====================

@router.post("/questions", response_model=QuestionResponse)
async def generate_questions(request: QuestionRequest):
    """
    Generate assessment questions from textbook content using RAG.
    
    Questions are generated based on the actual content from the textbook
    chapter, ensuring they are relevant and context-appropriate.
    """
    try:
        logger.info(f"📝 Generating {request.num_questions} questions for Class {request.class_level}, {request.subject}, Ch. {request.chapter}")
        
        # Get chapter content using RAG service
        context = rag_service.retrieve_chapter_context(
            class_level=request.class_level,
            subject=request.subject,
            chapter=request.chapter,
            max_chunks=15  # Get more context for better question generation
        )
        
        # Build prompt for question generation
        prompt = f"""You are an educational assessment expert creating questions for a Class {request.class_level} student.

**TEXTBOOK CONTENT (Chapter {request.chapter}):**
{context}

**TASK:**
Generate {request.num_questions} assessment questions that:
1. Are based ONLY on the content provided above
2. Are appropriate for a Class {request.class_level} student
3. Test understanding of key concepts from the chapter
4. Can be answered in 30-60 seconds (voice response)
5. Are clear and direct (no multiple choice)

**IMPORTANT RULES:**
- Questions must be derived from the textbook content above
- Do NOT ask about topics not mentioned in the content
- Use simple, clear language appropriate for Class {request.class_level}
- Questions should encourage thoughtful explanations

**FORMAT:**
Return ONLY the questions, one per line, numbered 1, 2, 3, etc.
Do NOT include any other text or explanations.

Example:
1. What is the main difference between X and Y as explained in the chapter?
2. How does the chapter describe the process of Z?
3. Why is A important according to the lesson?
"""

        # Generate questions using Gemini
        questions_text = gemini_service.generate_response(prompt)
        
        # Parse questions (split by newlines and extract numbered questions)
        questions = []
        for line in questions_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering/bullets
                question = line.split('.', 1)[-1].strip() if '.' in line else line.lstrip('-•').strip()
                if question and len(question) > 10:  # Basic validation
                    questions.append(question)
        
        # Ensure we have the requested number of questions
        questions = questions[:request.num_questions]
        
        if len(questions) < request.num_questions:
            logger.warning(f"⚠️ Could only generate {len(questions)} questions instead of {request.num_questions}")
        
        logger.info(f"✅ Generated {len(questions)} questions successfully")
        
        return QuestionResponse(
            questions=questions,
            chapter=request.chapter,
            subject=request.subject
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Question generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_answers(request: EvaluationRequest):
    """
    Evaluate student's voice assessment answers using RAG + Gemini.
    
    Compares answers against textbook content and provides detailed feedback.
    """
    try:
        logger.info(f"🔍 Evaluating {len(request.answers)} answers for Class {request.class_level}, {request.subject}, Ch. {request.chapter}")
        
        # Get chapter content for evaluation context
        context = rag_service.retrieve_chapter_context(
            class_level=request.class_level,
            subject=request.subject,
            chapter=request.chapter,
            max_chunks=15  # Get extensive context for evaluation
        )
        
        # Build evaluation prompt
        qa_pairs = "\n\n".join([
            f"**Question {i+1}:** {ans.question}\n**Student's Answer:** {ans.answer}"
            for i, ans in enumerate(request.answers)
        ])
        
        prompt = f"""You are a STRICT AI teacher evaluating a Class {request.class_level} student's voice assessment.

**TEXTBOOK CONTENT (Chapter {request.chapter}):**
{context}

**STUDENT'S ANSWERS:**
{qa_pairs}

**EVALUATION CRITERIA (STRICT):**
1. **Accuracy (50%)**: Compare answers with textbook content. Award points ONLY for factually correct information from the textbook.
2. **Completeness (30%)**: Check if key points from the chapter are mentioned. Partial answers get partial credit.
3. **Understanding (20%)**: Assess depth of comprehension. Surface-level answers get minimal points.

**CLASS {request.class_level} SCORING GUIDELINES:**
- **Excellent (80-100)**: Student demonstrates deep understanding, answers are accurate, and all key points covered
- **Good (60-79)**: Student shows understanding with mostly correct information, may miss 1-2 key points
- **Average (40-59)**: Basic understanding with several missing or incorrect points
- **Poor (20-39)**: Limited understanding, most information incorrect or missing
- **Very Poor (0-19)**: Almost no correct information or completely off-topic

**IMPORTANT RULES:**
- Be STRICT: Award points only for content that matches the textbook
- Incorrect information = 0 points for that part
- Vague or generic answers without specific textbook content = low score
- For Class {request.class_level}, expect age-appropriate depth
- If answer doesn't reference textbook concepts, score should be LOW

**PROVIDE:**
1. **Overall Score** (0-100): Based on strict textbook alignment
2. **Feedback** (2-3 sentences): Be honest and constructive
3. **Strengths** (1-3 points): What the student got right from the textbook
4. **Improvements** (2-4 points): Specific textbook concepts they missed or got wrong
5. **Question Scores** (0-100 each): Individual score for each question
6. **Topics to Study**: Specific topics/concepts from the chapter the student should review

**FORMAT YOUR RESPONSE EXACTLY AS:**
SCORE: [number 0-100]
FEEDBACK: [your honest feedback here]
STRENGTHS:
- [specific strength from textbook]
- [another strength if any]
IMPROVEMENTS:
- [specific textbook concept to review]
- [another area to improve]
QUESTION_SCORES:
- Q1: [score 0-100] - [brief hint about what to focus on, NO direct answer]
- Q2: [score 0-100] - [brief hint]
- Q3: [score 0-100] - [brief hint]
TOPICS_TO_STUDY:
- [Specific topic/section from chapter]
- [Another topic]
- [More topics if needed]
"""

        # Get evaluation from Gemini
        evaluation_text = gemini_service.generate_response(prompt)
        
        # Parse the response
        score = 50  # Default - Average (changed from 75)
        feedback = "Your answers need more specific information from the textbook. Review the chapter carefully."
        strengths = ["Attempted all questions"]
        improvements = [
            "Include specific facts and concepts from the textbook",
            "Review the chapter content thoroughly",
            "Practice explaining concepts in your own words using textbook information"
        ]
        question_scores = []
        topics_to_study = []
        
        try:
            # Extract score
            if "SCORE:" in evaluation_text:
                score_line = [line for line in evaluation_text.split('\n') if 'SCORE:' in line][0]
                score = int(''.join(filter(str.isdigit, score_line)))
                score = max(0, min(100, score))  # Clamp between 0-100
            
            # Extract feedback
            if "FEEDBACK:" in evaluation_text:
                feedback_start = evaluation_text.find("FEEDBACK:") + len("FEEDBACK:")
                feedback_end = evaluation_text.find("STRENGTHS:", feedback_start)
                if feedback_end > feedback_start:
                    feedback = evaluation_text[feedback_start:feedback_end].strip()
            
            # Extract strengths
            if "STRENGTHS:" in evaluation_text:
                strengths_start = evaluation_text.find("STRENGTHS:") + len("STRENGTHS:")
                strengths_end = evaluation_text.find("IMPROVEMENTS:", strengths_start)
                if strengths_end > strengths_start:
                    strengths_text = evaluation_text[strengths_start:strengths_end]
                    strengths = [s.strip('- ').strip() for s in strengths_text.split('\n') if s.strip().startswith('-')]
            
            # Extract improvements
            if "IMPROVEMENTS:" in evaluation_text:
                improvements_start = evaluation_text.find("IMPROVEMENTS:") + len("IMPROVEMENTS:")
                improvements_end = evaluation_text.find("QUESTION_SCORES:", improvements_start)
                if improvements_end == -1:
                    improvements_end = evaluation_text.find("TOPICS_TO_STUDY:", improvements_start)
                if improvements_end > improvements_start:
                    improvements_text = evaluation_text[improvements_start:improvements_end]
                    improvements = [s.strip('- ').strip() for s in improvements_text.split('\n') if s.strip().startswith('-')]
            
            # Extract question scores
            if "QUESTION_SCORES:" in evaluation_text:
                qs_start = evaluation_text.find("QUESTION_SCORES:") + len("QUESTION_SCORES:")
                qs_end = evaluation_text.find("TOPICS_TO_STUDY:", qs_start)
                if qs_end > qs_start:
                    qs_text = evaluation_text[qs_start:qs_end]
                    for i, line in enumerate(qs_text.split('\n')):
                        if line.strip().startswith('-') or line.strip().startswith('Q'):
                            # Extract score and hint
                            parts = line.split('-', 1)[-1].strip()
                            q_score = 50
                            hint = "Review this topic"
                            if ':' in parts:
                                score_part, hint = parts.split(':', 1) if ':' in parts else (parts, "")
                                q_score = int(''.join(filter(str.isdigit, score_part[:10]))) if any(c.isdigit() for c in score_part[:10]) else 50
                                hint = hint.strip()
                            question_scores.append({
                                "question_num": i + 1,
                                "score": max(0, min(100, q_score)),
                                "hint": hint or "Review this topic"
                            })
            
            # Extract topics to study
            if "TOPICS_TO_STUDY:" in evaluation_text:
                topics_start = evaluation_text.find("TOPICS_TO_STUDY:") + len("TOPICS_TO_STUDY:")
                topics_text = evaluation_text[topics_start:]
                topics_to_study = [s.strip('- ').strip() for s in topics_text.split('\n') if s.strip().startswith('-')]
        
        except Exception as parse_error:
            logger.warning(f"⚠️ Could not parse evaluation response: {parse_error}")
        
        # Ensure we have question scores for all questions
        while len(question_scores) < len(request.answers):
            question_scores.append({
                "question_num": len(question_scores) + 1,
                "score": 50,
                "hint": "Review the chapter content for this question"
            })
        
        logger.info(f"✅ Evaluation complete. Score: {score}/100")
        
        return EvaluationResponse(
            score=score,
            feedback=feedback,
            strengths=strengths[:3],  # Limit to 3 items
            improvements=improvements[:4],  # Limit to 4 items
            question_scores=question_scores,
            topics_to_study=topics_to_study[:5]  # Limit to 5 topics
        )
    
    except Exception as e:
        logger.error(f"❌ Evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
