from typing import Dict, Any, Optional
from llm_service import LLMService, create_llm_service
from application_memory import ApplicationMemory, create_application_memory
from job_analyzer import ResumeLoader
from config import Config

class FormFiller:
    """
    Intelligently fills application forms using LLM and memory.
    
    SOLID Principles:
    - Single Responsibility: Only handles form filling logic
    - Dependency Inversion: Depends on abstractions (LLMService, ApplicationMemory)
    """
    
    def __init__(self, llm_service: LLMService, memory: ApplicationMemory, resume_loader: ResumeLoader):
        self._llm = llm_service
        self._memory = memory
        self._resume = resume_loader.load()
    
    def get_answer(self, field: Dict[str, Any]) -> Optional[str]:
        """
        Get answer for a form field.
        
        Args:
            field: Dict with keys: label, type, options (for dropdown/radio)
        
        Returns:
            Answer string or None if unable to answer
        """
        question = field.get("label", "")
        field_type = field.get("type", "text")
        
        # Check memory first
        cached_answer = self._memory.get_answer(question)
        if cached_answer:
            print(f"Using cached answer for: {question}")
            return cached_answer
        
        # Generate new answer using LLM
        print(f"Generating answer for: {question}")
        answer = self._generate_answer(field)
        
        if answer:
            # Store for future use
            self._memory.store_answer(question, answer, field_type)
        
        return answer
    
    def _generate_answer(self, field: Dict[str, Any]) -> Optional[str]:
        """Generate answer using LLM."""
        question = field.get("label", "")
        field_type = field.get("type", "text")
        options = field.get("options", [])
        
        system_prompt = """You are an expert at filling job application forms.
Given a question and the candidate's resume, provide a concise, accurate answer.

Rules:
1. Be truthful based on the resume
2. For yes/no questions, answer "Yes" or "No"
3. For number questions, provide just the number
4. For text questions, keep answers under 100 characters
5. For dropdown/radio, choose from provided options
"""
        
        user_prompt = f"""
Resume:
{self._resume}

Question: {question}
Field Type: {field_type}
"""
        
        if options:
            user_prompt += f"Options: {', '.join(options)}\n"
        
        user_prompt += "\nProvide only the answer, no explanation."
        
        try:
            answer = self._llm.chat(system_prompt, user_prompt, prefer_smart=False)
            return answer.strip()
        except Exception as e:
            print(f"Error generating answer: {e}")
            return None


# Factory function
def create_form_filler() -> FormFiller:
    """Factory function to create FormFiller with default dependencies."""
    llm_service = create_llm_service()
    memory = create_application_memory()
    resume_loader = ResumeLoader(Config.RESUME_PATH)
    return FormFiller(llm_service, memory, resume_loader)


if __name__ == "__main__":
    # Test
    filler = create_form_filler()
    
    test_fields = [
        {"label": "How many years of Python experience do you have?", "type": "text"},
        {"label": "Are you authorized to work in the US?", "type": "radio", "options": ["Yes", "No"]},
        {"label": "What is your highest level of education?", "type": "dropdown", 
         "options": ["High School", "Bachelor's", "Master's", "PhD"]}
    ]
    
    for field in test_fields:
        answer = filler.get_answer(field)
        print(f"Q: {field['label']}")
        print(f"A: {answer}\n")
