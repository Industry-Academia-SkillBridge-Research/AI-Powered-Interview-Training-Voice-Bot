# 🤖 AI-Powered Interview Training System

A modern, full-stack interview training application powered by Ollama LLaMA 3.2, RAG (Retrieval Augmented Generation), and React.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=llama&logoColor=white)

## ✨ Features

### 🎯 Core Functionality
- **PDF Job Description Upload** - Drag & drop interface
- **RAG-Powered Questions** - Context-aware interview questions
- **Real-time Conversation** - Interactive chat interface
- **Voice Input & Output** - Speech recognition and text-to-speech
- **Progress Tracking** - Visual progress indicators
- **Session Management** - Multiple interview sessions

### 🧠 AI Capabilities
- **Semantic Search** - FAISS vector database for context retrieval
- **LLaMA 3.2** - Advanced language model for question generation
- **Embeddings** - nomic-embed-text for semantic understanding
- **Adaptive Questions** - Questions adapt based on your answers

### 🎨 Modern UI/UX
- **Dark Theme** - Professional, eye-friendly design
- **Responsive** - Works on desktop and mobile
- **Animations** - Smooth transitions and loading states
- **Accessibility** - Keyboard shortcuts and screen reader support

## 🏗️ Architecture


### 🔑 Key Design Principle
- **Embeddings**: 100% LOCAL using Ollama (no cloud API calls)
- **Text Generation**: Google Gemini (questions, feedback)

```
┌─────────────────────────────────────────────────────────────┐
│                    USER UPLOADS JD PDF                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  1. PDF EXTRACTION (pdf_loader.py)                          │
│     - Extract text from PDF using PyMuPDF                   │
│     - Validate content                                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  2. TEXT CHUNKING (loader.py)                               │
│     - Split text into chunks (1000 chars)                   │
│     - RecursiveCharacterTextSplitter                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  3. LOCAL EMBEDDINGS (embeddings.py) ⭐                      │
│     - Provider: Ollama                                      │
│     - Model: nomic-embed-text                               │
│     - 100% LOCAL - No cloud API calls                       │
│     - No rate limits or quotas                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  4. VECTOR STORE (vector_store.py)                          │
│     - FAISS vector database                                 │
│     - Fast similarity search                                │
│     - Persistent storage support                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  INTERVIEW SESSION STARTS                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  5. RETRIEVAL (retriever.py)                                │
│     - Query: "job requirements and skills"                  │
│     - Retrieve top K relevant chunks                        │
│     - Uses LOCAL embeddings (no API calls)                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  6. LLM GENERATION (gemini.py) ⭐                            │
│     - Provider: Google Gemini                               │
│     - Model: gemini-1.5-flash                               │
│     - Purpose: Text generation ONLY                         │
│     - Input: Retrieved context + conversation history       │
│     - Output: Interview question                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  7. INTERVIEW ENGINE (interview.py)                         │
│     - Orchestrate RAG pipeline                              │
│     - Manage conversation flow                              │
│     - Track questions asked                                 │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- **Python 3.10+**
- **Node.js 16+**
- **Ollama** (https://ollama.com/download)

### 1. Install Ollama (for LOCAL embeddings)
```bash
# Install Ollama
# Visit: https://ollama.ai/download

# Start Ollama server
ollama serve

# Pull the embedding model
ollama pull nomic-embed-text
```

### 2. Set Environment Variables
```bash
# .env file
GEMINI_API_KEY=your_gemini_api_key_here
CHAT_MODEL=gemini-1.5-flash

# Ollama configuration
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### 3. Install Python Dependencies
```bash
pip install langchain langchain-community langchain-google-genai
pip install faiss-cpu  # or faiss-gpu for GPU support
pip install pymupdf  # for PDF extraction
```

## 🚀 Quick Start

### 1. Install Ollama Models
```powershell
ollama pull llama3.2
ollama pull nomic-embed-text
```

### 2. Backend Setup
```powershell
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
python -m app.api
```
Backend runs at: `http://localhost:8000`

### 3. Frontend Setup
```powershell
cd frontend

# First time: Replace old files with new ones
cd src
del pages\upload_jd_page.js
ren pages\upload_jd_page_new.js upload_jd_page.js
del pages\interview_page.js
ren pages\interview_page_new.js interview_page.js
del pages\feedback_page.js
ren pages\feedback_page_new.js feedback_page.js
del styles.css
ren styles_new.css styles.css
cd ..

# Install and run
npm install
npm start
```
Frontend runs at: `http://localhost:3000`

## 📖 Usage

1. **Upload Job Description**
   - Open http://localhost:3000
   - Upload a PDF job description
   - System processes it using RAG

2. **Answer Questions**
   - AI generates contextual questions
   - Type or use voice input
   - Submit your answer

3. **Complete Interview**
   - Progress through all questions
   - Review your performance
   - Start a new interview

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Ollama** - Local LLM inference
- **FAISS** - Vector similarity search
- **PyMuPDF** - PDF text extraction
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI library
- **React Router** - Navigation
- **Axios** - HTTP client
- **Web Speech API** - Voice input/output
- **CSS3** - Modern styling

### AI/ML
- **LLaMA 3.2** - Chat model
- **nomic-embed-text** - Embedding model
- **RAG** - Retrieval Augmented Generation
- **FAISS** - Vector database

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api.py              # FastAPI server
│   │   ├── main.py             # CLI version
│   │   ├── core/
│   │   │   └── config.py       # Configuration
│   │   ├── services/
│   │   │   └── openai_client.py # Ollama client
│   │   └── interview/
│   │       ├── vector_store.py  # RAG implementation
│   │       ├── interview_engine.py # Chat logic
│   │       ├── jd_loader.py     # PDF extraction
│   │       └── prompts.py       # System prompts
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── services/
│   │   │   └── api.js          # API integration
│   │   ├── pages/
│   │   │   ├── upload_jd_page.js
│   │   │   ├── interview_page.js
│   │   │   └── feedback_page.js
│   │   ├── components/
│   │   │   └── [various components]
│   │   └── styles.css          # Modern styling
│   └── package.json
│
├── .env                        # Configuration
├── SETUP_GUIDE.md             # Detailed setup
└── QUICK_START.md             # Quick commands
```

## 🔧 Configuration

Edit `.env` file:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Application Settings
MAX_INTERVIEW_QUESTIONS=7
ENVIRONMENT=development
DEBUG=true
```

## 🎯 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Detailed health status |
| GET | `/docs` | Interactive API documentation |
| POST | `/api/upload-jd` | Upload job description PDF |
| POST | `/api/start-interview` | Get first interview question |
| POST | `/api/next-question` | Submit answer, get next question |
| GET | `/api/session/{id}` | Get session status |
| DELETE | `/api/session/{id}` | End session |
| GET | `/api/sessions` | List all sessions |

## 🎨 UI Components

### Upload Page
- Drag & drop file upload
- PDF validation
- Progress indicators
- Error handling

### Interview Page
- Real-time conversation thread
- Voice input with visual feedback
- Progress bar
- Question/answer history
- Keyboard shortcuts

### Feedback Page
- Completion statistics
- Achievement list
- Technology showcase
- Action buttons

## 🔍 Features in Detail

### RAG System
1. **Document Chunking** - Splits JD into 500-char chunks with 100-char overlap
2. **Embedding Generation** - Creates vector embeddings using nomic-embed-text
3. **Vector Storage** - Stores in FAISS index for fast retrieval
4. **Semantic Search** - Retrieves top-3 relevant chunks per query
5. **Context Injection** - Injects context into LLM prompts

### Voice Features
- **Speech Recognition** - Continuous voice input with real-time transcription
- **Text-to-Speech** - AI questions are spoken aloud
- **Visual Feedback** - Pulsing microphone icon when recording
- **Browser Compatibility** - Works in Chrome, Edge, Safari

### Session Management
- **In-Memory Storage** - Fast session access
- **Session IDs** - Unique identifier per interview
- **State Tracking** - Question count, history, progress
- **Cleanup** - Automatic session cleanup on end

## 🐛 Troubleshooting

### Backend Issues

**"Connection refused" to Ollama**
```powershell
ollama list  # Verify Ollama is running
ollama serve  # If not running
```

**"Model not found"**
```powershell
ollama pull llama3.2
ollama pull nomic-embed-text
```

**Import errors**
```powershell
pip install -r requirements.txt
```

### Frontend Issues

**"Module not found"**
```powershell
npm install
```

**API connection errors**
- Check backend is running on port 8000
- Check console for CORS errors
- Verify API_BASE_URL in api.js

**Voice not working**
- Chrome/Edge required for best support
- Grant microphone permissions
- Check browser console for errors

## 📚 Documentation

- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup instructions
- [QUICK_START.md](QUICK_START.md) - Quick start commands
- [Backend API Docs](http://localhost:8000/docs) - Interactive API documentation

## 🤝 Best Practices Implemented

### Code Quality
- ✅ Type hints and Pydantic models
- ✅ Error handling and validation
- ✅ Modular architecture
- ✅ Clean code principles
- ✅ Comments and docstrings

### Security
- ✅ CORS configuration
- ✅ Input validation
- ✅ File type restrictions
- ✅ Error sanitization

### Performance
- ✅ Efficient vector search
- ✅ Lazy loading
- ✅ Request optimization
- ✅ Memory management

### UX/UI
- ✅ Loading states
- ✅ Error messages
- ✅ Progress indicators
- ✅ Responsive design
- ✅ Accessibility features

## 🎓 Learning Resources

- [Ollama Documentation](https://ollama.com/docs)
- [LLaMA 3.2 Guide](https://ollama.com/library/llama3.2)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [RAG Explained](https://python.langchain.com/docs/use_cases/question_answering/)

## 📝 License

This project is for educational and training purposes.

## 👨‍💻 Author

Built with ❤️ using modern AI technologies

---

**Need Help?** Check the [SETUP_GUIDE.md](SETUP_GUIDE.md) or [QUICK_START.md](QUICK_START.md)
