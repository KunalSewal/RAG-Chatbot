"""
FastAPI Backend for RAG Chatbot
Production-ready REST API with streaming support
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import asyncio
import shutil

from src.rag_pipeline import RAGPipeline
from src.logging_utils import setup_logging, get_logger
from src.error_handling import ChatbotError
from config.settings import settings

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Production-grade Document Q&A System with RAG",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance
pipeline: Optional[RAGPipeline] = None


# Request/Response Models
class QueryRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    top_k: int = 5
    stream: bool = False


class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    conversation_id: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    message: str
    files_processed: int
    chunks_created: int


class HealthResponse(BaseModel):
    status: str
    version: str
    models: Dict[str, str]


# Startup/Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Initialize the RAG pipeline on startup"""
    global pipeline
    try:
        logger.info("Starting RAG Chatbot API...")
        pipeline = RAGPipeline()
        logger.info("RAG Pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down RAG Chatbot API...")


# Health Check Endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        models={
            "llm": settings.llm_model,
            "embedding": settings.embedding_model
        }
    )


# Document Management Endpoints
@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload and ingest documents into the knowledge base
    """
    try:
        logger.info(f"Received {len(files)} files for upload")
        
        # Save uploaded files temporarily
        temp_paths = []
        settings.data_directory.mkdir(exist_ok=True)
        
        for file in files:
            temp_path = settings.data_directory / file.filename
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_paths.append(str(temp_path))
        
        # Ingest documents
        pipeline.ingest_documents(temp_paths)
        
        # Get chunk count (approximate)
        chunk_count = len(temp_paths) * 10  # Rough estimate
        
        logger.info(f"Successfully processed {len(files)} documents")
        
        return DocumentUploadResponse(
            message="Documents processed successfully",
            files_processed=len(files),
            chunks_created=chunk_count
        )
        
    except Exception as e:
        logger.error(f"Error uploading documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process documents: {str(e)}")


@app.delete("/documents/clear")
async def clear_documents():
    """Clear all documents from the knowledge base"""
    try:
        pipeline.clear_knowledge_base()
        return {"message": "Knowledge base cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear knowledge base: {str(e)}")


# Query Endpoints
@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the knowledge base with a question
    """
    try:
        logger.info(f"Processing query: {request.question[:100]}...")
        
        response = pipeline.ask_question(
            question=request.question,
            conversation_id=request.conversation_id,
            top_k=request.top_k
        )
        
        return QueryResponse(**response)
        
    except ChatbotError as e:
        logger.error(f"Chatbot error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/query/stream")
async def query_documents_stream(request: QueryRequest):
    """
    Query the knowledge base with streaming response
    """
    try:
        logger.info(f"Processing streaming query: {request.question[:100]}...")
        
        async def generate_stream():
            try:
                # Get relevant documents
                relevant_docs = pipeline.embedding_manager.search_similar(
                    request.question, 
                    request.top_k
                )
                
                # Get conversation history
                conversation_history = None
                if request.conversation_id:
                    conversation_history = pipeline.memory.get_conversation_history(
                        request.conversation_id
                    )
                
                # Stream response
                full_answer = ""
                async for chunk in pipeline.llm.generate_response_stream(
                    query=request.question,
                    context_documents=relevant_docs,
                    conversation_history=conversation_history
                ):
                    full_answer += chunk
                    yield chunk
                
                # Store conversation turn after streaming
                if request.conversation_id:
                    pipeline.memory.add_conversation_turn(
                        conversation_id=request.conversation_id,
                        user_message=request.question,
                        assistant_message=full_answer
                    )
                    
            except Exception as e:
                logger.error(f"Error in streaming: {str(e)}")
                yield f"\n\nError: {str(e)}"
        
        return StreamingResponse(generate_stream(), media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Error setting up stream: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Streaming query failed: {str(e)}")


# WebSocket Endpoint for Real-time Chat
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat
    """
    await websocket.accept()
    conversation_id = pipeline.memory.create_conversation()
    
    try:
        logger.info(f"WebSocket connection established. Conversation ID: {conversation_id}")
        
        while True:
            # Receive question from client
            data = await websocket.receive_json()
            question = data.get("question", "")
            
            if not question:
                await websocket.send_json({"error": "Empty question"})
                continue
            
            logger.info(f"WebSocket query: {question[:100]}...")
            
            # Get relevant documents
            relevant_docs = pipeline.embedding_manager.search_similar(question, top_k=5)
            
            # Get conversation history
            conversation_history = pipeline.memory.get_conversation_history(conversation_id)
            
            # Stream response
            full_answer = ""
            await websocket.send_json({"type": "start"})
            
            async for chunk in pipeline.llm.generate_response_stream(
                query=question,
                context_documents=relevant_docs,
                conversation_history=conversation_history
            ):
                full_answer += chunk
                await websocket.send_json({
                    "type": "chunk",
                    "content": chunk
                })
            
            # Send sources
            sources = [
                {
                    "source": doc['metadata'].get('source_document', 'Unknown'),
                    "content_preview": doc['content'][:200]
                }
                for doc in relevant_docs
            ]
            
            await websocket.send_json({
                "type": "end",
                "sources": sources
            })
            
            # Store conversation
            pipeline.memory.add_conversation_turn(
                conversation_id=conversation_id,
                user_message=question,
                assistant_message=full_answer
            )
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected. Conversation ID: {conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass


# Conversation Management
@app.post("/conversations/new")
async def create_conversation():
    """Create a new conversation"""
    conversation_id = pipeline.memory.create_conversation()
    return {"conversation_id": conversation_id}


@app.get("/conversations/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    """Get conversation history"""
    try:
        history = pipeline.memory.get_conversation_history(conversation_id)
        return {"conversation_id": conversation_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Conversation not found: {str(e)}")


# Analytics Endpoint
@app.get("/analytics/stats")
async def get_analytics():
    """Get system analytics and statistics"""
    # TODO: Implement analytics collection
    return {
        "total_documents": "N/A",
        "total_queries": "N/A",
        "avg_response_time": "N/A",
        "popular_queries": []
    }


# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        workers=1  # Use 1 for development, settings.api_workers for production
    )
