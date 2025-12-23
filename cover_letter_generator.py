from typing import Dict, Any
from llm_service import LLMService, create_llm_service
from job_analyzer import ResumeLoader
from config import Config

class CoverLetterGenerator:
    """
    Generates personalized cover letters.
    
    SOLID Principles:
    - Single Responsibility: Only generates cover letters
    - Dependency Inversion: Depends on abstractions (LLMService)
    """
    
    def __init__(self, llm_service: LLMService, resume_loader: ResumeLoader):
        """
        Dependency Injection.
        
        Args:
            llm_service: LLM service for generation
            resume_loader: Resume data loader
        """
        self._llm = llm_service
        self._resume = resume_loader.load()
    
    def generate(self, job_data: Dict[str, Any]) -> str:
        """
        Generate a personalized cover letter.
        
        Args:
            job_data: Dict with title, company, description
        
        Returns:
            str: Cover letter text
        """
        job_title = job_data.get("title", "this position")
        company = job_data.get("company", "your company")
        job_desc = job_data.get("description", "")
        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(job_title, company, job_desc)
        
        try:
            # Use prefer_smart=True for better quality cover letters
            cover_letter = self._llm.chat(system_prompt, user_prompt, prefer_smart=True)
            return cover_letter.strip()
        except Exception as e:
            print(f"Error generating cover letter: {e}")
            return self._get_fallback_letter(job_title, company)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for cover letter generation."""
        return """You are a professional cover letter writer.
Write compelling, personalized cover letters that:
1. Are 3 paragraphs long
2. Highlight relevant experience from the resume
3. Show genuine interest in the role
4. Are professional but warm in tone
5. Are concise (under 300 words)

Do NOT use generic phrases like "I am writing to express my interest".
Start with a strong hook."""
    
    def _build_user_prompt(self, title: str, company: str, desc: str) -> str:
        """Build user prompt with job and resume data."""
        return f"""
Job Title: {title}
Company: {company}
Job Description: {desc}

Candidate Resume:
{self._resume}

Write a cover letter for this candidate applying to this job.
"""
    
    def _get_fallback_letter(self, title: str, company: str) -> str:
        """Return basic template on error."""
        return f"""I am excited to apply for the {title} position at {company}.

With my background in software engineering and proven track record of delivering results, I believe I would be a strong addition to your team.

I look forward to discussing how my skills and experience align with your needs.

Best regards"""


# Factory function
def create_cover_letter_generator() -> CoverLetterGenerator:
    """Factory function to create CoverLetterGenerator with default dependencies."""
    llm_service = create_llm_service()
    resume_loader = ResumeLoader(Config.RESUME_PATH)
    return CoverLetterGenerator(llm_service, resume_loader)


if __name__ == "__main__":
    # Test
    generator = create_cover_letter_generator()
    
    test_job = {
        "title": "Machine Learning Engineer",
        "company": "Tesla",
        "description": "Build autonomous driving ML models"
    }
    
    letter = generator.generate(test_job)
    print(letter)
