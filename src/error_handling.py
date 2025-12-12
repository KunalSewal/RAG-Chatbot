class ChatbotError(Exception):
    """Base exception for chatbot errors."""
    pass

class DocumentIngestionError(ChatbotError):
    """Raised when document ingestion fails."""
    pass

class EmbeddingError(ChatbotError):
    """Raised when embedding operations fail."""
    pass

class LLMError(ChatbotError):
    """Raised when LLM operations fail."""
    pass

class DatabaseError(ChatbotError):
    """Raised when database operations fail."""
    pass

class RetrievalError(ChatbotError):
    """Raised when document retrieval fails."""
    pass
