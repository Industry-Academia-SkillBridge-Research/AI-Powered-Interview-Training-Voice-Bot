from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import io

from app.interview_gemini.rag.embeddings import get_local_embeddings  # LOCAL Ollama embeddings
from app.interview_gemini.rag.pdf_loader import extract_text_from_pdf
from app.interview_gemini.rag.loader import chunk_text
from app.interview_gemini.rag.vector_store import create_vector_store
from app.interview_gemini.utils.session import create_session, get_session
from app.interview_gemini.services.interview import generate_next_turn
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Interview Training API",
    description="RAG-based interview system using LOCAL Ollama embeddings + Gemini text generation"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LOCAL Ollama embeddings (NO cloud API calls for embeddings)
try:
    embeddings = get_local_embeddings()
    logger.info("✓ LOCAL Ollama embeddings initialized successfully")
except Exception as e:
    logger.error(f"✗ Failed to initialize Ollama embeddings: {str(e)}")
    logger.error("Make sure Ollama is running: ollama serve")
    logger.error("Make sure model is installed: ollama pull nomic-embed-text")
    embeddings = None

# Global sessions storage for additional metadata
sessions = {}

# Pydantic models
class JDUploadResponse(BaseModel):
    session_id: str
    text: str
    chunks_count: int
    message: str

class QuestionRequest(BaseModel):
    session_id: str
    user_answer: Optional[str] = None

class QuestionResponse(BaseModel):
    question: str
    question_number: int
    total_questions: int
    is_complete: bool

class SessionStatus(BaseModel):
    session_id: str
    is_active: bool
    question_count: int
    max_questions: int


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "AI Interview Training API",
        "embeddings": "LOCAL Ollama (nomic-embed-text)",
        "llm": f"Google Gemini ({settings.CHAT_MODEL})",
        "ollama_url": settings.OLLAMA_BASE_URL,
        "embeddings_ready": embeddings is not None
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy" if embeddings else "degraded",
        "embeddings": {
            "provider": "Ollama (LOCAL)",
            "model": settings.OLLAMA_EMBEDDING_MODEL,
            "url": settings.OLLAMA_BASE_URL,
            "ready": embeddings is not None
        },
        "llm": {
            "provider": "Google Gemini",
            "model": settings.CHAT_MODEL,
            "ready": bool(settings.GEMINI_API_KEY)
        }
    }


@app.post("/api/upload-jd", response_model=JDUploadResponse)
async def upload_jd(file: UploadFile = File(...)):
    """
    Upload job description PDF and create vector store using LOCAL Ollama embeddings.
    NO cloud API calls for embeddings - all done locally.
    """
    if not embeddings:
        raise HTTPException(
            status_code=503,
            detail="Ollama embeddings not available. Ensure Ollama is running."
        )
    
    try:
        logger.info(f"Processing JD upload: {file.filename}")
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        content = await file.read()
        
        # Extract text from PDF
        logger.info("Extracting text from PDF...")
        jd_text = extract_text_from_pdf(content)
        logger.info(f"Extracted {len(jd_text)} characters")
        
        # Chunk text
        logger.info("Chunking text...")
        chunks = chunk_text(jd_text)
        logger.info(f"Created {len(chunks)} chunks")
        
        # Create vector store using LOCAL Ollama embeddings
        logger.info("Creating vector store with LOCAL Ollama embeddings...")
        vector_store = create_vector_store(chunks, embeddings)
        logger.info("✓ Vector store created successfully (100% local, no cloud API calls)")
        
        # Create session
        session_id = create_session(vector_store)
        logger.info(f"✓ Session created: {session_id}")
        
        return JDUploadResponse(
            session_id=session_id,
            text=jd_text[:500] + "..." if len(jd_text) > 500 else jd_text,
            chunks_count=len(chunks),
            message=f"Job description processed successfully using LOCAL embeddings ({len(chunks)} chunks)"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JD upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/api/start-interview", response_model=QuestionResponse)
async def start_interview(request: QuestionRequest):
    """Start interview and get first question"""
    try:
        logger.info(f"Starting interview for session: {request.session_id}")
        session = get_session(request.session_id)
        logger.info(f"Session retrieved: {session.keys()}")
        
        # Get first question
        logger.info("Calling generate_next_turn...")
        question, _, _ = generate_next_turn(session)
        logger.info(f"Question generated: {question[:50] if question else 'None'}...")
        
        # Defensive validation: ensure question is a valid string
        if not question:
            logger.error("Generated question is None or empty")
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate interview question. Please try again."
            )
        
        # Ensure question is a string (should already be from extract_text_from_gemini)
        if not isinstance(question, str):
            logger.error(f"Question is not a string, type: {type(question)}")
            question = str(question).strip()
        
        return QuestionResponse(
            question=question,
            question_number=session["question_count"],
            total_questions=settings.MAX_INTERVIEW_QUESTIONS,
            is_complete=False
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Handle text extraction errors
        logger.error(f"Validation error in start_interview: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process Gemini response: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in start_interview: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating question: {str(e)}")


@app.post("/api/next-question", response_model=QuestionResponse)
async def next_question(request: QuestionRequest):
    """Submit answer and get next question"""
    if not request.user_answer:
        raise HTTPException(status_code=400, detail="Answer is required")
    
    try:
        session = get_session(request.session_id)
        
        # Get next question based on answer
        question, feedback, ended = generate_next_turn(
            session,
            user_answer=request.user_answer
        )
        
        # Defensive validation for question string
        if question and not isinstance(question, str):
            logger.warning(f"Question is not a string, type: {type(question)}")
            question = str(question).strip()
        
        return QuestionResponse(
            question=question if not ended else "",
            question_number=session["question_count"],
            total_questions=settings.MAX_INTERVIEW_QUESTIONS,
            is_complete=ended
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error in next_question: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process Gemini response: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in next_question: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating question: {str(e)}")


@app.get("/api/session/{session_id}", response_model=SessionStatus)
async def get_session_status(session_id: str):
    """Get session status"""
    try:
        session = get_session(session_id)
        
        return SessionStatus(
            session_id=session_id,
            is_active=session["question_count"] < settings.MAX_INTERVIEW_QUESTIONS,
            question_count=session["question_count"],
            max_questions=settings.MAX_INTERVIEW_QUESTIONS
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="Session not found")


@app.delete("/api/session/{session_id}")
async def end_session(session_id: str):
    """End and cleanup session"""
    try:
        if session_id in sessions:
            del sessions[session_id]
        return {"message": "Session ended successfully", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ending session: {str(e)}")


# from pathlib import Path
# from app.interview.jd_loader import extract_jd_text
# from app.interview.vector_store import JDVectorStore
# from app.interview.interview_engine import InterviewSession
# from app.services.openai_client import OllamaClient
# from app.core.config import settings


# def main():
#     print("=" * 60)
#     print("AI-Powered Interview Training System")
#     print("=" * 60)
    
#     # 1. Load Job Description
#     jd_path = Path("C:\\Users\\dilit\\OneDrive - Sri Lanka Institute of Information Technology\\Research\\ai-powered-interview-training-voicebot\\backend\\app\\inputs\\Data_Science_Intern_JD.pdf")
#     print(f"\nLoading job description from: {jd_path.name}")
#     jd_text = extract_jd_text(jd_path)
#     print(f"Loaded {len(jd_text)} characters from JD")

#     # 2. Initialize Ollama client
#     print(f"\nConnecting to Ollama at {settings.OLLAMA_BASE_URL}")
#     print(f"   Model: {settings.OLLAMA_MODEL}")
#     print(f"   Embeddings: {settings.OLLAMA_EMBEDDING_MODEL}")
#     client = OllamaClient()

#     # 3. Initialize RAG vector store
#     print("\nInitializing RAG vector store...")
#     vectorstore = JDVectorStore(jd_text, client)
#     print("Vector store ready")

#     # 4. Create interview session
#     print(f"\nCreating interview session ({settings.MAX_INTERVIEW_QUESTIONS} questions max)")
#     session = InterviewSession(vectorstore)
#     print("Interview session initialized")

#     # 5. Run the interview
#     print("\n" + "=" * 60)
#     print("Starting Interview - Type 'exit', 'quit', or 'stop' to end")
#     print("=" * 60 + "\n")
    
#     # Ask first question
#     print("[Generating first question...]\n")
#     question = session.ask_next_question()
#     print(f"AI Interviewer: {question}\n")
    
#     # Continue interview loop
#     while session.question_count < settings.MAX_INTERVIEW_QUESTIONS:
#         # Get user answer
#         user_answer = input("Your Answer: ").strip()
        
#         if user_answer.lower() in ["exit", "quit", "stop"]:
#             print("\n" + "=" * 60)
#             print("Interview ended. Thank you for participating!")
#             print("=" * 60)
#             break
        
#         if not user_answer:
#             print("Please provide an answer.\n")
#             continue
        
#         # Process answer and get next question
#         print("\n[Analyzing response and generating next question...]\n")
#         question = session.ask_next_question(user_answer=user_answer)
#         print(f"AI Interviewer: {question}\n")
    
#     else:
#         print("\n" + "=" * 60)
#         print(f"Interview completed! You answered {session.question_count} questions.")
#         print("Thank you for participating!")
#         print("=" * 60)

# if __name__ == "__main__":
#     main()
