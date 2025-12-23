from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    Follows Interface Segregation Principle - clients depend only on methods they use.
    """
    
    @abstractmethod
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Send a chat request and return response."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is configured and available."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the provider name for logging."""
        pass
