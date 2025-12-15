# RAG Document Chatbot

A full-stack Retrieval-Augmented Generation (RAG) system that enables intelligent document-based question answering with conversation memory and semantic search. Built with FastAPI, Next.js 14, and Amazon Nova 2 Lite reasoning model.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-14.0+-black.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🌟 Key Features

### Dual-Mode Chat System
- **General Chat Mode**: Standard AI conversation without documents
- **RAG Mode**: Context-aware responses using uploaded documents as knowledge base
- Automatic mode switching based on document availability

### Advanced Conversation Management
- **Multi-Chat Sessions**: Create unlimited independent chat threads
- **Per-Chat Document Isolation**: Each chat maintains its own document context
- **Auto-Generated Titles**: Chat names generated from first user message
- **Chat History Sidebar**: Quick navigation between all conversation threads
- **Document Badges**: Visual indicators showing which documents are active per message

### Document Processing & Search
- **PDF Support**: Upload and process PDF documents
- **Semantic Search**: SentenceTransformers embeddings (384-dimensional vectors)
- **Vector Database**: ChromaDB for efficient similarity search
- **Chunking**: Intelligent text splitting (1000 chars, 200 overlap)
- **Source Citations**: Every RAG answer includes document sources

### Modern UI/UX
- **Dark Theme**: Professional dark mode interface with gradient backgrounds
- **Responsive Design**: Mobile-friendly layout
- **Smooth Animations**: Framer Motion for polished interactions
- **Markdown Rendering**: Full markdown support with syntax-highlighted code blocks
- **Copy to Clipboard**: One-click copy for AI responses
- **Real-time Feedback**: Loading states and typing indicators

### AI & Reasoning
- **Amazon Nova 2 Lite**: Free-tier reasoning model via OpenRouter
- **Reasoning Mode**: Chain-of-thought processing for complex queries (auto-enabled for Nova models)
- **Fallback Model**: Llama 3.2 3B for reliability
- **Conversation Memory**: In-memory context retention (last 5 turns)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js 14 Frontend                       │
│  React 18 • TypeScript • Tailwind CSS • Framer Motion      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Chat History │  │  Chat Canvas │  │ Document Upload │  │
│  │   Sidebar    │  │  (Messages)  │  │    & Badges     │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │ REST API (Axios)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Python)                   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐│
│  │              RAG Pipeline Orchestrator                  ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Document   │  │  Embedding   │  │   LLM Wrapper   │  │
│  │   Ingester   │  │   Manager    │  │  (OpenRouter)   │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │    Memory    │  │ Preprocessor │  │  Error Handler  │  │
│  │  (In-Memory) │  │  (Chunking)  │  │   & Logging     │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└───────┬──────────────────┬──────────────────┬──────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   ChromaDB   │  │    OpenRouter    │  │ SentenceTransf.  │
│  (Vectors)   │  │  Amazon Nova 2   │  │   all-MiniLM-    │
│  Persistent  │  │ Lite (Reasoning) │  │   L6-v2 (CPU)    │
└──────────────┘  └──────────────────┘  └──────────────────┘
```

### Request Flow

**Document Upload**:
1. Frontend uploads PDF → Backend `/documents/upload`
2. PyPDF2 extracts text → RecursiveCharacterTextSplitter chunks (1000/200)
3. SentenceTransformer creates 384-dim embeddings (lazy-loaded)
4. ChromaDB stores vectors + metadata
5. Documents linked to current chat session

**Query Processing**:
1. User sends question → Backend `/query`
2. Query embedded → ChromaDB similarity search (top-k=5)
3. Retrieved docs + conversation history → OpenRouter API
4. Amazon Nova 2 Lite generates response (reasoning enabled)
5. Response + sources returned to frontend
6. Message stored in conversation memory

---

## 🛠️ Technology Stack

### Backend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API Framework** | FastAPI 0.104+ | REST API with automatic OpenAPI docs |
| **LLM** | Amazon Nova 2 Lite | Free reasoning model (OpenRouter) |
| **Embeddings** | SentenceTransformers | Local 384-dim vectors (CPU) |
| **Vector DB** | ChromaDB | Persistent vector storage |
| **Document Processing** | PyPDF2, langchain-text-splitters | PDF extraction & chunking |
| **Memory** | In-memory dict | Conversation history (ephemeral) |
| **Logging** | Python logging | Structured logging to file/console |

### Frontend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | Next.js 14 | React with App Router |
| **Language** | TypeScript 5.3+ | Type safety |
| **Styling** | Tailwind CSS 3.4 | Utility-first CSS |
| **Animations** | Framer Motion 10.16 | Smooth UI transitions |
| **HTTP** | Axios 1.6 | API requests |
| **Markdown** | react-markdown | Response rendering |
| **Code Highlighting** | react-syntax-highlighter | Code block styling |
| **Icons** | Lucide React | UI icons |

### Infrastructure
| Component | Technology | Notes |
|-----------|-----------|-------|
| **Containerization** | Docker & Docker Compose | Multi-stage builds |
| **Database** | ChromaDB (vector) + SQLite | Persistent storage |
| **API Protocol** | REST (OpenAPI 3.0) | Automatic docs at `/docs` |
| **CORS** | Wildcard (development) | Restricted in production |

---

## 📦 Installation

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **Docker** (optional, for containerized deployment)
- **OpenRouter API Key** (free tier available)

### Quick Start (Docker - Recommended)

1. **Clone repository**:
```bash
git clone https://github.com/KunalSewal/RAG-Chatbot.git
cd RAG-Chatbot
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

3. **Start with Docker Compose**:
```bash
docker-compose up -d
```

4. **Access application**:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Local Development Setup

#### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your OpenRouter API key

# Run backend
python api/main.py
```
Backend runs on: http://localhost:8000

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```
Frontend runs on: http://localhost:3000

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Model Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=amazon/nova-2-lite-v1:free
LLM_FALLBACK_MODEL=meta-llama/llama-3.2-3b-instruct:free

# Text Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Vector Database
CHROMA_PERSIST_DIRECTORY=./database/chroma_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

### Getting OpenRouter API Key
1. Visit https://openrouter.ai
2. Sign up for free account
3. Navigate to "Keys" section
4. Generate new API key
5. Copy key to `.env` file

---

## 🚀 Usage Guide

### Starting a New Chat
1. Click "**+ New Chat**" in sidebar
2. New chat session created with empty document context

### Uploading Documents
1. Click **📎 paperclip icon** next to message input
2. Select PDF file(s)
3. Documents are processed and added to **current chat only**
4. Document badges appear on messages to show available context

### Asking Questions

**General Chat Mode** (no documents):
```
User: What is machine learning?
AI: [Provides general answer without document context]
```

**RAG Mode** (with documents):
```
User: [Upload research paper]
User: What are the key findings?
AI: [Answers based on uploaded document with source citations]
```

### Managing Chats
- **Switch chats**: Click any chat in sidebar
- **Delete chat**: Hover over chat → click trash icon
- **View chat info**: See message count and document count per chat

### Copy Responses
- Click **📋 copy icon** on any AI message
- Checkmark appears to confirm copy

---

## 📚 API Documentation

### Core Endpoints

#### Health Check
```http
GET /health
```
Returns API status and model information.

**Response**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "models": {
    "llm": "amazon/nova-2-lite-v1:free",
    "embedding": "sentence-transformers/all-MiniLM-L6-v2"
  }
}
```

#### Upload Documents
```http
POST /documents/upload
Content-Type: multipart/form-data
```
Upload PDF documents to the knowledge base.

**Request**:
```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "files=@document.pdf"
```

**Response**:
```json
{
  "message": "Documents processed successfully",
  "files_processed": 1,
  "chunks_created": 10
}
```

#### Query (Non-Streaming)
```http
POST /query
Content-Type: application/json
```
Ask a question and get a complete response.

**Request**:
```json
{
  "question": "What are the main findings?",
  "conversation_id": "optional-uuid",
  "top_k": 5
}
```

**Response**:
```json
{
  "answer": "Based on the documents...",
  "sources": [
    {
      "source": "document.pdf",
      "content_preview": "First 200 chars of relevant chunk..."
    }
  ],
  "conversation_id": "uuid"
}
```

#### Query (Streaming)
```http
POST /query/stream
Content-Type: application/json
```
Stream response tokens in real-time.

#### WebSocket Chat
```
WS /ws/chat
```
Real-time bidirectional chat (not currently used by frontend).

#### Conversation Management
```http
POST /conversations/new
GET /conversations/{conversation_id}/history
```
Create and retrieve conversation history.

#### Clear Knowledge Base
```http
DELETE /documents/clear
```
Remove all documents from ChromaDB.

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🐳 Docker Deployment

### Architecture
- **Multi-stage builds** for optimized image sizes
- **Volume mounts** for persistent data (database, logs)
- **Health checks** for backend monitoring
- **Service orchestration** via docker-compose

### Docker Commands

**Start services**:
```bash
docker-compose up -d
```

**View logs**:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Stop services**:
```bash
docker-compose down
```

**Rebuild after code changes**:
```bash
docker-compose up --build -d
```

**Check service status**:
```bash
docker-compose ps
```

### Docker Configuration

**Backend Dockerfile**:
- Base: `python:3.11-slim`
- Installs system dependencies
- Copies requirements and installs packages
- Exposes port 8000
- Runs `python api/main.py`

**Frontend Dockerfile**:
- Base: `node:20-alpine`
- Multi-stage: Build stage + Production stage
- Next.js standalone output for optimized size
- Exposes port 3000

---

## 🧪 Testing

### Manual Testing
1. Start application (Docker or local)
2. Create new chat
3. Upload sample PDF (e.g., research paper)
4. Ask document-related question
5. Verify response includes source citations
6. Test general chat without documents
7. Create multiple chats and verify isolation

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Upload document
curl -X POST http://localhost:8000/documents/upload \
  -F "files=@sample.pdf"

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Summarize the document", "top_k": 5}'
```

---

## ⚠️ Known Limitations

### Cloud Deployment
- **Render Free Tier**: Insufficient RAM (512MB) for embedding model + dependencies
  - Embedding model loads on first use (lazy loading implemented)
  - May still OOM on first document upload
- **Solution**: Use paid hosting (2GB+ RAM) or switch to API-based embeddings

### Memory & Persistence
- **Conversation Memory**: In-memory only (resets on server restart)
- **Documents**: Stored in ChromaDB (persistent across restarts)
- **File Storage**: Uploaded PDFs saved to `./data` directory

### Feature Gaps
- No user authentication
- No document deletion from UI
- No conversation export
- No streaming in frontend (API supports it)
- No rate limiting
- Analytics endpoint not implemented

### Browser Compatibility
- Modern browsers only (ES6+ required)
- Tested on Chrome, Firefox, Safari, Edge

---

## 🔧 Troubleshooting

### Backend Issues

**Port 8000 already in use**:
```bash
# Find process
lsof -ti:8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

**Module not found errors**:
```bash
pip install -r requirements.txt
```

**ChromaDB errors**:
```bash
# Delete and recreate database
rm -rf database/chroma_db
# Restart backend - will recreate collection
```

**CUDA/GPU errors**:
- Embedding model forces CPU mode (no GPU required)
- Check [src/embeddings.py](src/embeddings.py#L16-L21) for device setting

### Frontend Issues

**API connection refused**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify `NEXT_PUBLIC_API_URL` in [frontend/app/page.tsx](frontend/app/page.tsx#L11)
3. Check CORS settings in [api/main.py](api/main.py#L40-L46)

**Build errors**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

**TypeScript errors**:
```bash
npm run build  # Check for type errors
```

### Docker Issues

**Build fails**:
```bash
# Clean build
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

**Container exits immediately**:
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend
```

**Port conflicts**:
```bash
# Change ports in docker-compose.yml
# e.g., "3001:3000" for frontend
```

---

## 📊 Performance

### Metrics (Local Development)
- **Query Latency**: 2-5 seconds (OpenRouter API + embedding)
- **Embedding Speed**: ~50-100 chunks/second (CPU)
- **ChromaDB Search**: <100ms for 1000 documents
- **PDF Processing**: ~1-3 seconds per document
- **Memory Usage**: 
  - Backend: ~500MB base + ~200MB per embedded model load
  - Frontend: ~100MB

### Optimization Tips
- Use GPU for embeddings (10x+ speedup)
- Implement caching for frequent queries
- Use streaming API endpoint for better UX
- Batch document uploads
- Increase `top_k` for more context (slower but more accurate)

---

## 🔐 Security Considerations

### Current Implementation
- ⚠️ **No authentication** - Anyone with URL can access
- ⚠️ **No rate limiting** - Vulnerable to abuse
- ⚠️ **API key in .env** - Secure on server, but never commit
- ⚠️ **CORS wildcard** - Development only, restrict in production
- ⚠️ **No input validation** - FastAPI Pydantic provides basic validation

### Production Recommendations
1. **Add authentication** (JWT, OAuth)
2. **Implement rate limiting** (per IP/user)
3. **Restrict CORS** to specific domains
4. **Validate file uploads** (size limits, type checking)
5. **Use secrets manager** for API keys (not .env)
6. **Add HTTPS** (reverse proxy with SSL)
7. **Sanitize user input** (prevent injection attacks)
8. **Monitor logs** for suspicious activity

---

## 🗺️ Roadmap

### Planned Features
- [ ] User authentication (Firebase/Auth0)
- [ ] Persistent conversation storage (PostgreSQL)
- [ ] Document deletion from UI
- [ ] Multiple file format support (DOCX, TXT, Markdown)
- [ ] Conversation export (JSON, Markdown)
- [ ] Streaming responses in frontend
- [ ] Rate limiting & API keys
- [ ] Admin dashboard
- [ ] Search within chat history
- [ ] Document preview in UI
- [ ] Mobile app (React Native)

### Potential Improvements
- [ ] Switch to API embeddings for cloud deployment
- [ ] Implement hybrid search (semantic + keyword)
- [ ] Add reranking for better retrieval
- [ ] Support web scraping (URL ingestion)
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Document comparison feature
- [ ] Analytics dashboard

---

## 🤝 Contributing

Contributions welcome! This is a portfolio project, but improvements are appreciated.

### Development Workflow
1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Style
- **Python**: PEP 8, type hints, docstrings
- **TypeScript**: ESLint, Prettier, strict mode
- **Commits**: Conventional Commits format

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Amazon Nova 2 Lite** - Free reasoning model
- **OpenRouter** - Unified LLM API
- **LangChain** - Document processing utilities
- **ChromaDB** - Vector database
- **Hugging Face** - SentenceTransformers models
- **Vercel** - Next.js framework creators
- **FastAPI** - Modern Python web framework

---

## 📞 Contact

**Kunal Sewal**
- GitHub: [@KunalSewal](https://github.com/KunalSewal)
- Project: [RAG-Chatbot](https://github.com/KunalSewal/RAG-Chatbot)

---

## 🎯 Project Status

**Current Version**: 2.0.0
**Status**: ✅ Production-ready for local deployment
**Last Updated**: December 2025

### What Works
✅ Docker Compose deployment  
✅ Multi-chat with document isolation  
✅ PDF upload and processing  
✅ Semantic search with ChromaDB  
✅ Amazon Nova 2 Lite reasoning  
✅ Markdown rendering with syntax highlighting  
✅ Responsive dark-themed UI  

### What Doesn't (Yet)
❌ Cloud deployment on free tiers (memory constraints)  
❌ User authentication  
❌ Persistent conversation storage  
❌ Frontend streaming (API supports it)  

---

**Built with ❤️ for demonstrating full-stack RAG capabilities**
