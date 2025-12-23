from langchain_fireworks import ChatFireworks
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import Config
import json

class LLMService:
    def __init__(self):
        self.fireworks_available = bool(Config.FIREWORKS_API_KEY)
        self.openai_available = bool(Config.OPENAI_API_KEY)
        
        if not self.fireworks_available and not self.openai_available:
            raise ValueError("No LLM API keys found! Set FIREWORKS_API_KEY or OPENAI_API_KEY in .env")
        
        # Initialize models
        if self.fireworks_available:
            self.default_llm = ChatFireworks(
                model=Config.DEFAULT_LLM_MODEL,
                temperature=0.7,
                max_tokens=2000
            )
            print("Using Fireworks AI (Llama 3)")
        
        if self.openai_available:
            self.smart_llm = ChatOpenAI(
                model=Config.SMART_LLM_MODEL,
                temperature=0.7,
                max_tokens=2000
            )
            if not self.fireworks_available:
                self.default_llm = self.smart_llm
                print("Using OpenAI (GPT-4o)")
        
        self.total_cost = 0.0
    
    def chat(self, system_prompt, user_prompt, use_smart=False):
        """
        Send a chat request to the LLM.
        
        Args:
            system_prompt: System instructions
            user_prompt: User query
            use_smart: If True, use GPT-4o instead of Llama
        
        Returns:
            str: LLM response
        """
        try:
            llm = self.smart_llm if (use_smart and self.openai_available) else self.default_llm
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = llm.invoke(messages)
            return response.content
            
        except Exception as e:
            print(f"LLM Error: {e}")
            # Fallback to OpenAI if Fireworks fails
            if not use_smart and self.openai_available and self.fireworks_available:
                print("Fireworks failed, falling back to OpenAI...")
                return self.chat(system_prompt, user_prompt, use_smart=True)
            raise
    
    def chat_json(self, system_prompt, user_prompt, use_smart=False):
        """
        Request JSON response from LLM.
        """
        system_prompt += "\n\nYou MUST respond with valid JSON only. No markdown, no explanations."
        response = self.chat(system_prompt, user_prompt, use_smart)
        
        # Clean markdown if present
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        return json.loads(response)

if __name__ == "__main__":
    # Test
    llm = LLMService()
    result = llm.chat(
        "You are a helpful assistant.",
        "Say hello in 5 words."
    )
    print(result)
