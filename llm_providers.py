from llm_provider import LLMProvider
from langchain_fireworks import ChatFireworks
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import Config

class FireworksProvider(LLMProvider):
    """Fireworks AI provider implementation."""
    
    def __init__(self):
        self._client = None
        if Config.FIREWORKS_API_KEY:
            try:
                self._client = ChatFireworks(
                    model=Config.DEFAULT_LLM_MODEL,
                    temperature=0.7,
                    max_tokens=2000
                )
            except Exception as e:
                print(f"Failed to initialize Fireworks: {e}")
    
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        if not self._client:
            raise RuntimeError("Fireworks client not initialized")
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = self._client.invoke(messages)
        return response.content
    
    def is_available(self) -> bool:
        return self._client is not None
    
    def get_name(self) -> str:
        return "Fireworks AI"


class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation."""
    
    def __init__(self):
        self._client = None
        if Config.OPENAI_API_KEY:
            try:
                self._client = ChatOpenAI(
                    model=Config.SMART_LLM_MODEL,
                    temperature=0.7,
                    max_tokens=2000
                )
            except Exception as e:
                print(f"Failed to initialize OpenAI: {e}")
    
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        if not self._client:
            raise RuntimeError("OpenAI client not initialized")
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = self._client.invoke(messages)
        return response.content
    
    def is_available(self) -> bool:
        return self._client is not None
    
    def get_name(self) -> str:
        return "OpenAI"
