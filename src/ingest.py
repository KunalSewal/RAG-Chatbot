import os
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2
from src.logging_utils import get_logger
from src.error_handling import DocumentIngestionError

logger = get_logger(__name__)

class DocumentIngester:
    """Handles loading and extracting text from various document formats."""
    
    def __init__(self):
        self.supported_extensions = {'.pdf', '.txt'}
    
    def ingest_document(self, file_path: str) -> Dict[str, Any]:
        """
        Ingest a single document and extract its text content.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing document metadata and content
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise DocumentIngestionError(f"File not found: {file_path}")
            
            if path.suffix.lower() not in self.supported_extensions:
                raise DocumentIngestionError(f"Unsupported file type: {path.suffix}")
            
            logger.info(f"Ingesting document: {file_path}")
            
            if path.suffix.lower() == '.pdf':
                content = self._extract_pdf_text(path)
            elif path.suffix.lower() == '.txt':
                content = self._extract_txt_text(path)
            
            return {
                'file_path': str(path),
                'file_name': path.name,
                'content': content,
                'file_size': path.stat().st_size,
                'extension': path.suffix.lower()
            }
            
        except Exception as e:
            logger.error(f"Error ingesting document {file_path}: {str(e)}")
            raise DocumentIngestionError(f"Failed to ingest document: {str(e)}")
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    def _extract_txt_text(self, file_path: Path) -> str:
        """Extract text from TXT file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    
    def ingest_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Ingest all supported documents from a directory.
        
        Args:
            directory_path: Path to the directory containing documents
            
        Returns:
            List of document dictionaries
        """
        documents = []
        directory = Path(directory_path)
        
        if not directory.exists():
            raise DocumentIngestionError(f"Directory not found: {directory_path}")
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    doc = self.ingest_document(str(file_path))
                    documents.append(doc)
                except DocumentIngestionError as e:
                    logger.warning(f"Skipping file {file_path}: {str(e)}")
        
        logger.info(f"Ingested {len(documents)} documents from {directory_path}")
        return documents
