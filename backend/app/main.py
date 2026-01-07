from pathlib import Path
from app.interview.jd_loader import extract_jd_text
from app.interview.vector_store import JDVectorStore
from app.interview.interview_engine import InterviewSession
from app.services.openai_client import OllamaClient
from app.core.config import settings


def main():
    print("=" * 60)
    print("AI-Powered Interview Training System")
    print("=" * 60)
    
    # 1. Load Job Description
    jd_path = Path("C:\\Users\\dilit\\OneDrive - Sri Lanka Institute of Information Technology\\Research\\ai-powered-interview-training-voicebot\\backend\\app\\inputs\\Data_Science_Intern_JD.pdf")
    print(f"\nLoading job description from: {jd_path.name}")
    jd_text = extract_jd_text(jd_path)
    print(f"Loaded {len(jd_text)} characters from JD")

    # 2. Initialize Ollama client
    print(f"\nConnecting to Ollama at {settings.OLLAMA_BASE_URL}")
    print(f"   Model: {settings.OLLAMA_MODEL}")
    print(f"   Embeddings: {settings.OLLAMA_EMBEDDING_MODEL}")
    client = OllamaClient()

    # 3. Initialize RAG vector store
    print("\nInitializing RAG vector store...")
    vectorstore = JDVectorStore(jd_text, client)
    print("Vector store ready")

    # 4. Create interview session
    print(f"\nCreating interview session ({settings.MAX_INTERVIEW_QUESTIONS} questions max)")
    session = InterviewSession(vectorstore)
    print("Interview session initialized")

    # 5. Run the interview
    print("\n" + "=" * 60)
    print("Starting Interview - Type 'exit', 'quit', or 'stop' to end")
    print("=" * 60 + "\n")
    
    # Ask first question
    print("[Generating first question...]\n")
    question = session.ask_next_question()
    print(f"AI Interviewer: {question}\n")
    
    # Continue interview loop
    while session.question_count < settings.MAX_INTERVIEW_QUESTIONS:
        # Get user answer
        user_answer = input("Your Answer: ").strip()
        
        if user_answer.lower() in ["exit", "quit", "stop"]:
            print("\n" + "=" * 60)
            print("Interview ended. Thank you for participating!")
            print("=" * 60)
            break
        
        if not user_answer:
            print("Please provide an answer.\n")
            continue
        
        # Process answer and get next question
        print("\n[Analyzing response and generating next question...]\n")
        question = session.ask_next_question(user_answer=user_answer)
        print(f"AI Interviewer: {question}\n")
    
    else:
        print("\n" + "=" * 60)
        print(f"Interview completed! You answered {session.question_count} questions.")
        print("Thank you for participating!")
        print("=" * 60)

if __name__ == "__main__":
    main()
