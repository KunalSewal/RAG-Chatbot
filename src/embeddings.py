from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from config.settings import settings
from src.logging_utils import get_logger
from src.error_handling import EmbeddingError

logger = get_logger(__name__)

class EmbeddingManager:
    """Manages document embeddings and vector storage using local models."""
    
    def __init__(self):
        # Initialize local embedding model (no API calls, completely free!)
        logger.info(f"Loading local embedding model: {settings.embedding_model}")
        model_name = settings.embedding_model.split('/')[-1]  # Extract model name
        self.embedding_model = SentenceTransformer(model_name)
        logger.info("Local embedding model loaded successfully")
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Delete old collection if it exists (to fix dimension mismatch)
        try:
            self.chroma_client.delete_collection(name="documents")
            logger.info("Deleted old documents collection")
        except:
            pass
        
        # Create fresh collection
        self.collection = self.chroma_client.create_collection(
            name="documents",
            metadata={"description": "Document embeddings for RAG chatbot"}
        )
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for a text using local SentenceTransformer model.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            # Use local model - completely free, no API calls!
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            raise EmbeddingError(f"Failed to create embedding: {str(e)}")
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Add document chunks to the vector database.
        
        Args:
            chunks: List of chunk dictionaries
        """
        try:
            # Prepare data for ChromaDB
            ids = []
            documents = []
            metadatas = []
            embeddings = []
            
            for chunk in chunks:
                # Create embedding
                embedding = self.create_embedding(chunk['content'])
                
                ids.append(chunk['chunk_id'])
                documents.append(chunk['content'])
                embeddings.append(embedding)
                metadatas.append({
                    'source_document': chunk['source_document'],
                    'source_path': chunk['source_path'],
                    'chunk_index': chunk['chunk_index'],
                    'chunk_size': chunk['chunk_size']
                })
            
            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(chunks)} chunks to vector database")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector database: {str(e)}")
            raise EmbeddingError(f"Failed to add documents: {str(e)}")
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents using semantic similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of similar document chunks
        """
        try:
            # Create query embedding
            query_embedding = self.create_embedding(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            similar_docs = []
            for i in range(len(results['ids'][0])):
                doc = {
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                similar_docs.append(doc)
            
            logger.info(f"Found {len(similar_docs)} similar documents for query")
            return similar_docs
            
        except Exception as e:
            logger.error(f"Error searching similar documents: {str(e)}")
            raise EmbeddingError(f"Failed to search documents: {str(e)}")
    
    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        try:
            # Delete and recreate collection
            self.chroma_client.delete_collection("documents")
            self.collection = self.chroma_client.get_or_create_collection(
                name="documents",
                metadata={"description": "Document embeddings for RAG chatbot"}
            )
            logger.info("Cleared vector database")
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            raise EmbeddingError(f"Failed to clear collection: {str(e)}")
