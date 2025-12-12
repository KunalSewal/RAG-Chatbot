from typing import List, Dict, Any, Optional, AsyncGenerator
from openai import OpenAI
from config.settings import settings
from src.logging_utils import get_logger
from src.error_handling import LLMError

logger = get_logger(__name__)

class LLMWrapper:
    """Wrapper for Large Language Model operations using OpenRouter API with Amazon Nova reasoning."""
    
    def __init__(self):
        # OpenRouter uses OpenAI-compatible API
        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url
        )
        self.model = settings.llm_model
        self.fallback_model = settings.llm_fallback_model
        self.enable_reasoning = "amazon/nova" in self.model.lower()  # Enable reasoning for Nova models
        logger.info(f"Initialized LLM with model: {self.model} (reasoning: {self.enable_reasoning})")
    
    def generate_response(
        self, 
        query: str, 
        context_documents: List[Dict[str, Any]], 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        use_fallback: bool = False
    ) -> str:
        """
        Generate a response using the LLM with retrieved context.
        
        Args:
            query: User's question
            context_documents: Retrieved relevant documents
            conversation_history: Previous conversation turns
            use_fallback: Use fallback model if True
            
        Returns:
            Generated response
        """
        try:
            # Build context from retrieved documents
            context = self._build_context(context_documents)
            
            # Build conversation messages
            messages = self._build_messages(query, context, conversation_history)
            
            # Select model
            model = self.fallback_model if use_fallback else self.model
            enable_reasoning = self.enable_reasoning and not use_fallback
            
            # Generate response using OpenRouter (OpenAI-compatible API)
            extra_body = {"reasoning": {"enabled": True}} if enable_reasoning else {}
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                stream=False,
                extra_body=extra_body
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Log reasoning details if available
            if hasattr(response.choices[0].message, 'reasoning_details') and response.choices[0].message.reasoning_details:
                logger.info(f"Reasoning tokens: {getattr(response.choices[0].message.reasoning_details, 'tokens', 'N/A')}")
            
            logger.info(f"Generated response for query: {query[:50]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            # Try fallback model if main model fails
            if not use_fallback:
                logger.info("Retrying with fallback model...")
                return self.generate_response(query, context_documents, conversation_history, use_fallback=True)
            raise LLMError(f"Failed to generate response: {str(e)}")
    
    def _build_context(self, context_documents: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents."""
        if not context_documents:
            return "No relevant context found."
        
        context_parts = []
        for i, doc in enumerate(context_documents, 1):
            source = doc['metadata'].get('source_document', 'Unknown')
            content = doc['content']
            context_parts.append(f"Source {i} ({source}):\n{content}")
        
        return "\n\n".join(context_parts)
    
    def _build_messages(
        self, 
        query: str, 
        context: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """Build message list for the chat completion API."""
        
        system_prompt = """You are a helpful AI assistant that answers questions based on the provided context. 
        Follow these guidelines:
        1. Answer questions based primarily on the provided context
        2. If the context doesn't contain enough information, say so clearly
        3. Be concise but informative
        4. Cite sources when possible
        5. If asked about something not in the context, politely explain the limitation"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if conversation_history:
            for turn in conversation_history[-5:]:  # Keep last 5 turns
                messages.append({"role": "user", "content": turn.get("user", "")})
                messages.append({"role": "assistant", "content": turn.get("assistant", "")})
        
        # Add current query with context
        user_message = f"Context:\n{context}\n\nQuestion: {query}"
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    async def generate_response_stream(
        self, 
        query: str, 
        context_documents: List[Dict[str, Any]], 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response using the LLM with retrieved context.
        
        Args:
            query: User's question
            context_documents: Retrieved relevant documents
            conversation_history: Previous conversation turns
            
        Yields:
            Chunks of the generated response
        """
        try:
            # Build context from retrieved documents
            context = self._build_context(context_documents)
            
            # Build conversation messages
            messages = self._build_messages(query, context, conversation_history)
            
            # Generate streaming response
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Error generating streaming response: {str(e)}")
            raise LLMError(f"Failed to generate streaming response: {str(e)}")
    
    def summarize_document(self, document_content: str) -> str:
        """
        Generate a summary of a document.
        
        Args:
            document_content: Full document content
            
        Returns:
            Document summary
        """
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant that creates concise summaries of documents."},
                {"role": "user", "content": f"Please provide a concise summary of the following document:\n\n{document_content}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info("Generated document summary")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise LLMError(f"Failed to generate summary: {str(e)}")
    
    def generate_general_response(
        self, 
        query: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a general chat response without document context.
        
        Args:
            query: User's question
            conversation_history: Previous conversation turns
            
        Returns:
            Generated response string
        """
        try:
            logger.info(f"Generating general chat response for: {query[:50]}...")
            
            messages = [
                {"role": "system", "content": "You are a helpful, friendly AI assistant. Answer questions clearly and concisely."}
            ]
            
            # Add conversation history
            if conversation_history:
                for turn in conversation_history[-5:]:
                    messages.append({"role": "user", "content": turn.get("user", "")})
                    messages.append({"role": "assistant", "content": turn.get("assistant", "")})
            
            # Add current query
            messages.append({"role": "user", "content": query})
            
            # Try main model
            try:
                # Enable reasoning for Nova models
                extra_body = {"reasoning": {"enabled": True}} if self.enable_reasoning else {}
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000,
                    extra_body=extra_body
                )
                answer = response.choices[0].message.content.strip()
                
                # Log reasoning if available
                if hasattr(response.choices[0].message, 'reasoning_details') and response.choices[0].message.reasoning_details:
                    logger.info(f"Used reasoning mode - tokens: {getattr(response.choices[0].message.reasoning_details, 'tokens', 'N/A')}")
                
                logger.info(f"Generated general response")
                return answer
                
            except Exception as e:
                logger.error(f"Error with main model: {str(e)}")
                if self.fallback_model:
                    logger.info("Retrying with fallback model...")
                    response = self.client.chat.completions.create(
                        model=self.fallback_model,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=2000
                    )
                    answer = response.choices[0].message.content.strip()
                    logger.info(f"Generated response with fallback model")
                    return answer
                else:
                    raise
                    
        except Exception as e:
            logger.error(f"Error generating general response: {str(e)}")
            raise LLMError(f"Failed to generate response: {str(e)}")
