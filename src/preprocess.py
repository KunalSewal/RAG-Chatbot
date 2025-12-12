import re
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import settings
from src.logging_utils import get_logger

logger = get_logger(__name__)

class TextPreprocessor:
    """Handles text cleaning and chunking operations."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.,!?;:\-\'"()]', '', text)
        
        # Strip and return
        return text.strip()
    
    def chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split document into chunks for processing.
        
        Args:
            document: Document dictionary from ingestion
            
        Returns:
            List of chunk dictionaries
        """
        try:
            # Clean the text
            cleaned_text = self.clean_text(document['content'])
            
            # Split into chunks
            chunks = self.text_splitter.split_text(cleaned_text)
            
            # Create chunk documents
            chunk_documents = []
            for i, chunk in enumerate(chunks):
                chunk_doc = {
                    'chunk_id': f"{document['file_name']}_chunk_{i}",
                    'source_document': document['file_name'],
                    'source_path': document['file_path'],
                    'chunk_index': i,
                    'content': chunk,
                    'chunk_size': len(chunk)
                }
                chunk_documents.append(chunk_doc)
            
            logger.info(f"Split document {document['file_name']} into {len(chunk_documents)} chunks")
            return chunk_documents
            
        except Exception as e:
            logger.error(f"Error chunking document {document['file_name']}: {str(e)}")
            return []
    
    def process_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple documents into chunks.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            List of all chunk dictionaries
        """
        all_chunks = []
        for document in documents:
            chunks = self.chunk_document(document)
            all_chunks.extend(chunks)
        
        logger.info(f"Processed {len(documents)} documents into {len(all_chunks)} total chunks")
        return all_chunks
