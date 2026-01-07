"""
FastAPI server for AI-Powered Interview Training System
Provides REST API endpoints for frontend integration
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from typing import List, Optional
import fitz  # PyMuPDF
import tempfile
import os
import uvicorn

from app.interview.jd_loader import extract_jd_text
from app.interview.vector_store import JDVectorStore
from app.interview.interview_engine import InterviewSession
from app.services.openai_client import OllamaClient
from app.core.config import settings


# Initialize FastAPI app
app = FastAPI(
    title="AI Interview Training API",
    description="RAG-based interview training system with Ollama",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (in production, use session management or Redis)
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


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "AI Interview Training API",
        "ollama_url": settings.OLLAMA_BASE_URL,
        "model": settings.OLLAMA_MODEL
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        client = OllamaClient()
        # Test connection to Ollama
        return {
            "status": "healthy",
            "ollama": "connected",
            "base_url": settings.OLLAMA_BASE_URL,
            "model": settings.OLLAMA_MODEL,
            "embedding_model": settings.OLLAMA_EMBEDDING_MODEL
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/api/upload-jd", response_model=JDUploadResponse)
async def upload_jd(file: UploadFile = File(...)):
    """
    Upload job description PDF and initialize RAG vector store
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Extract text from PDF
        jd_text = extract_jd_text(Path(tmp_path))
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        if not jd_text or len(jd_text) < 50:
            raise HTTPException(status_code=400, detail="Could not extract sufficient text from PDF")
        
        # Initialize Ollama client
        client = OllamaClient()
        
        # Initialize RAG vector store
        vectorstore = JDVectorStore(jd_text, client)
        
        # Create interview session
        session = InterviewSession(vectorstore)
        
        # Generate session ID
        session_id = f"session_{len(sessions) + 1}_{file.filename}"
        
        # Store session
        sessions[session_id] = {
            "session": session,
            "jd_text": jd_text,
            "filename": file.filename
        }
        
        return JDUploadResponse(
            session_id=session_id,
            text=jd_text[:500] + "..." if len(jd_text) > 500 else jd_text,
            chunks_count=len(vectorstore.chunks),
            message="Job description processed successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/api/start-interview", response_model=QuestionResponse)
async def start_interview(request: QuestionRequest):
    """
    Start interview and get first question
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[request.session_id]["session"]
        
        # Get first question
        question = session.ask_next_question()
        
        return QuestionResponse(
            question=question,
            question_number=session.question_count,
            total_questions=session.max_questions,
            is_complete=False
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating question: {str(e)}")


@app.post("/api/next-question", response_model=QuestionResponse)
async def next_question(request: QuestionRequest):
    """
    Submit answer and get next question
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not request.user_answer:
        raise HTTPException(status_code=400, detail="Answer is required")
    
    try:
        session = sessions[request.session_id]["session"]
        
        # Check if interview is complete
        if session.question_count >= session.max_questions:
            return QuestionResponse(
                question="",
                question_number=session.question_count,
                total_questions=session.max_questions,
                is_complete=True
            )
        
        # Get next question based on answer
        question = session.ask_next_question(user_answer=request.user_answer)
        
        is_complete = session.question_count >= session.max_questions
        
        return QuestionResponse(
            question=question if not is_complete else "",
            question_number=session.question_count,
            total_questions=session.max_questions,
            is_complete=is_complete
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating question: {str(e)}")


@app.get("/api/session/{session_id}", response_model=SessionStatus)
async def get_session_status(session_id: str):
    """
    Get session status
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]["session"]
    
    return SessionStatus(
        session_id=session_id,
        is_active=session.question_count < session.max_questions,
        question_count=session.question_count,
        max_questions=session.max_questions
    )


@app.delete("/api/session/{session_id}")
async def end_session(session_id: str):
    """
    End and cleanup session
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    
    return {"message": "Session ended successfully", "session_id": session_id}


@app.get("/api/sessions")
async def list_sessions():
    """
    List all active sessions (for debugging)
    """
    return {
        "count": len(sessions),
        "sessions": [
            {
                "session_id": sid,
                "filename": data["filename"],
                "question_count": data["session"].question_count,
                "max_questions": data["session"].max_questions
            }
            for sid, data in sessions.items()
        ]
    }


if __name__ == "__main__":
    # import uvicorn
    
    print("=" * 60)
    print("Starting AI Interview Training API Server")
    print("=" * 60)
    print(f"\nAPI URL: http://localhost:8000")
    print(f"Docs: http://localhost:8000/docs")
    print(f"Ollama: {settings.OLLAMA_BASE_URL}")
    print(f"Model: {settings.OLLAMA_MODEL}")
    print(f"Embeddings: {settings.OLLAMA_EMBEDDING_MODEL}\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
