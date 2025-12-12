from typing import List, Dict, Any, Optional
from src.ingest import DocumentIngester
from src.preprocess import TextPreprocessor
from src.embeddings import EmbeddingManager
from src.llm import LLMWrapper
from src.memory import ConversationMemory
from src.logging_utils import get_logger
from src.error_handling import ChatbotError

logger = get_logger(__name__)

class RAGPipeline:
    """Main RAG pipeline that orchestrates the entire process."""
    
    def __init__(self, user_id: Optional[str] = None):
        self.ingester = DocumentIngester()
        self.preprocessor = TextPreprocessor()
        self.embedding_manager = EmbeddingManager()
        self.llm = LLMWrapper()
        self.memory = ConversationMemory(user_id)
    
    def ingest_documents(self, file_paths: List[str]) -> None:
        """
        Ingest and process documents into the knowledge base.
        
        Args:
            file_paths: List of document file paths to ingest
        """
        try:
            logger.info(f"Starting document ingestion for {len(file_paths)} files")
            
            # Step 1: Ingest documents
            documents = []
            for file_path in file_paths:
                doc = self.ingester.ingest_document(file_path)
                documents.append(doc)
            
            # Step 2: Preprocess and chunk
            chunks = self.preprocessor.process_documents(documents)
            
            # Step 3: Create embeddings and store
            self.embedding_manager.add_documents(chunks)
            
            logger.info(f"Successfully ingested {len(documents)} documents into {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error in document ingestion pipeline: {str(e)}")
            raise ChatbotError(f"Document ingestion failed: {str(e)}")
    
    def ingest_directory(self, directory_path: str) -> None:
        """
        Ingest all documents from a directory.
        
        Args:
            directory_path: Path to directory containing documents
        """
        try:
            logger.info(f"Starting directory ingestion: {directory_path}")
            
            # Step 1: Ingest all documents from directory
            documents = self.ingester.ingest_directory(directory_path)
            
            # Step 2: Preprocess and chunk
            chunks = self.preprocessor.process_documents(documents)
            
            # Step 3: Create embeddings and store
            self.embedding_manager.add_documents(chunks)
            
            logger.info(f"Successfully ingested directory with {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error in directory ingestion: {str(e)}")
            raise ChatbotError(f"Directory ingestion failed: {str(e)}")
    
    def ask_question(
        self, 
        question: str, 
        conversation_id: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Answer a question using the RAG pipeline.
        
        Args:
            question: User's question
            conversation_id: Optional conversation ID for context
            top_k: Number of relevant documents to retrieve
            
        Returns:
            Dictionary containing answer and metadata
        """
        try:
            logger.info(f"Processing question: {question[:100]}...")
            
            # Step 1: Try to retrieve relevant documents (if any exist)
            relevant_docs = []
            try:
                relevant_docs = self.embedding_manager.search_similar(question, top_k)
                logger.info(f"Found {len(relevant_docs)} relevant documents")
            except Exception as e:
                logger.warning(f"No documents in knowledge base, using general chat mode: {str(e)}")
            
            # Step 2: Get conversation history if available
            conversation_history = None
            if conversation_id:
                conversation_history = self.memory.get_conversation_history(conversation_id)
            
            # Step 3: Generate response using LLM (with or without documents)
            if relevant_docs:
                # RAG mode - use documents as context
                answer = self.llm.generate_response(
                    query=question,
                    context_documents=relevant_docs,
                    conversation_history=conversation_history
                )
            else:
                # General chat mode - no documents
                logger.info("Using general chat mode (no documents)")
                answer = self.llm.generate_general_response(
                    query=question,
                    conversation_history=conversation_history
                )
            
            # Step 4: Store conversation turn
            if conversation_id:
                self.memory.add_conversation_turn(
                    conversation_id=conversation_id,
                    user_message=question,
                    assistant_message=answer
                )
            
            # Step 5: Prepare response
            response = {
                'answer': answer,
                'sources': [
                    {
                        'source': doc['metadata'].get('source_document', 'Unknown'),
                        'content_preview': doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
                    }
                    for doc in relevant_docs
                ],
                'conversation_id': conversation_id
            }
            
            logger.info("Successfully generated response")
            return response
            
        except Exception as e:
            logger.error(f"Error in question answering: {str(e)}")
            raise ChatbotError(f"Question answering failed: {str(e)}")
    
    def clear_knowledge_base(self) -> None:
        """Clear all documents from the knowledge base."""
        try:
            self.embedding_manager.clear_collection()
            logger.info("Cleared knowledge base")
        except Exception as e:
            logger.error(f"Error clearing knowledge base: {str(e)}")
            raise ChatbotError(f"Failed to clear knowledge base: {str(e)}")
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a given conversation ID."""
        return self.memory.get_conversation_history(conversation_id)
