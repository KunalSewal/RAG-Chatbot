from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from src.logging_utils import get_logger

logger = get_logger(__name__)

class ConversationMemory:
    """Manages conversation history using in-memory storage."""
    
    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
    
    def create_conversation(self, title: Optional[str] = None) -> str:
        """
        Create a new conversation and return its ID.
        
        Returns:
            Conversation ID
        """
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = []
        logger.info(f"Created new conversation: {conversation_id}")
        return conversation_id
    
    def add_conversation_turn(
        self, 
        conversation_id: str, 
        user_message: str, 
        assistant_message: str
    ) -> None:
        """
        Add a conversation turn to the history.
        
        Args:
            conversation_id: Conversation identifier
            user_message: User's message
            assistant_message: Assistant's response
        """
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        turn = {
            'timestamp': datetime.now().isoformat(),
            'user': user_message,
            'assistant': assistant_message
        }
        
        self.conversations[conversation_id].append(turn)
        logger.info(f"Added turn to conversation {conversation_id}")
    
    def get_conversation_history(
        self, 
        conversation_id: str, 
        max_turns: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation history for a given conversation ID.
        
        Args:
            conversation_id: Conversation identifier
            max_turns: Maximum number of turns to return
            
        Returns:
            List of conversation turns
        """
        if conversation_id not in self.conversations:
            return []
        
        history = self.conversations[conversation_id]
        
        if max_turns:
            history = history[-max_turns:]
        
        return history
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation from memory.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            True if deleted successfully, False if not found
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Deleted conversation {conversation_id}")
            return True
        return False
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """
        List all conversations with metadata.
        
        Returns:
            List of conversation metadata
        """
        conversations = []
        for conv_id, history in self.conversations.items():
            if history:
                first_turn = history[0]
                last_turn = history[-1]
                conversations.append({
                    'conversation_id': conv_id,
                    'title': 'Local Chat',
                    'created_at': first_turn['timestamp'],
                    'last_updated': last_turn['timestamp'],
                    'message_count': len(history),
                    'preview': history[0]['user'][:100] + "..." if len(history[0]['user']) > 100 else history[0]['user']
                })
        
        return conversations
    
    def clear_all_conversations(self) -> None:
        """Clear all conversations from memory."""
        self.conversations.clear()
        logger.info("Cleared all conversations")
