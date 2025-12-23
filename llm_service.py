from typing import List, Optional
import json
from llm_provider import LLMProvider
from llm_providers import FireworksProvider, OpenAIProvider

class LLMService:
    """
    LLM Service using Strategy Pattern.
    
    Design Patterns:
    - Strategy: Different LLM providers can be swapped at runtime
    - Chain of Responsibility: Falls back through providers on failure
    
    SOLID Principles:
    - Single Responsibility: Only handles LLM communication
    - Open/Closed: Open for extension (new providers), closed for modification
    - Dependency Inversion: Depends on LLMProvider abstraction, not concrete classes
    """
    
    def __init__(self, providers: Optional[List[LLMProvider]] = None):
        """
        Initialize with dependency injection.
        
        Args:
            providers: List of LLM providers in order of preference.
                      If None, uses default providers.
        """
        if providers is None:
            # Default providers in order of preference
            providers = [FireworksProvider(), OpenAIProvider()]
        
        self._providers = [p for p in providers if p.is_available()]
        
        if not self._providers:
            raise ValueError(
                "No LLM providers available. "
                "Please set FIREWORKS_API_KEY or OPENAI_API_KEY in .env"
            )
        
        print(f"LLM Service initialized with: {[p.get_name() for p in self._providers]}")
    
    def chat(self, system_prompt: str, user_prompt: str, 
             prefer_smart: bool = False) -> str:
        """
        Send a chat request with automatic fallback.
        
        Args:
            system_prompt: System instructions
            user_prompt: User query
            prefer_smart: If True, prefer more capable (expensive) models
        
        Returns:
            str: LLM response
        
        Raises:
            RuntimeError: If all providers fail
        """
        providers = self._providers[::-1] if prefer_smart else self._providers
        
        last_error = None
        for provider in providers:
            try:
                print(f"Using {provider.get_name()}...")
                return provider.chat(system_prompt, user_prompt)
            except Exception as e:
                print(f"{provider.get_name()} failed: {e}")
                last_error = e
                continue
        
        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")
    
    def chat_json(self, system_prompt: str, user_prompt: str, 
                  prefer_smart: bool = False) -> dict:
        """
        Request JSON response from LLM.
        
        Returns:
            dict: Parsed JSON response
        """
        system_prompt += "\n\nYou MUST respond with valid JSON only. No markdown, no explanations."
        response = self.chat(system_prompt, user_prompt, prefer_smart)
        
        # Clean markdown if present
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        return json.loads(response)


# Factory function for easy instantiation
def create_llm_service() -> LLMService:
    """Factory function to create LLM service with default configuration."""
    return LLMService()


if __name__ == "__main__":
    # Test
    llm = create_llm_service()
    result = llm.chat(
        "You are a helpful assistant.",
        "Say hello in 5 words."
    )
    print(result)
