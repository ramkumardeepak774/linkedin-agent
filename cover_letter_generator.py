from llm_service import LLMService
from config import Config

class CoverLetterGenerator:
    def __init__(self):
        self.llm = LLMService()
        self.resume = Config.RESUME_PATH.read_text() if Config.RESUME_PATH.exists() else ""
    
    def generate(self, job_data):
        """
        Generate a personalized cover letter for a job.
        
        Args:
            job_data: Dict with title, company, description
        
        Returns:
            str: Cover letter text
        """
        job_title = job_data.get("title", "this position")
        company = job_data.get("company", "your company")
        job_desc = job_data.get("description", "")
        
        system_prompt = """You are a professional cover letter writer.
Write compelling, personalized cover letters that:
1. Are 3 paragraphs long
2. Highlight relevant experience from the resume
3. Show genuine interest in the role
4. Are professional but warm in tone
5. Are concise (under 300 words)

Do NOT use generic phrases like "I am writing to express my interest".
Start with a strong hook."""
        
        user_prompt = f"""
Job Title: {job_title}
Company: {company}
Job Description: {job_desc}

Candidate Resume:
{self.resume}

Write a cover letter for this candidate applying to this job.
"""
        
        try:
            cover_letter = self.llm.chat(system_prompt, user_prompt, use_smart=True)
            return cover_letter.strip()
        except Exception as e:
            print(f"Error generating cover letter: {e}")
            # Return a basic template on error
            return f"""I am excited to apply for the {job_title} position at {company}.

With my background in software engineering and proven track record of delivering results, I believe I would be a strong addition to your team.

I look forward to discussing how my skills and experience align with your needs.

Best regards"""

if __name__ == "__main__":
    # Test
    generator = CoverLetterGenerator()
    
    test_job = {
        "title": "Machine Learning Engineer",
        "company": "Tesla",
        "description": "Build autonomous driving ML models"
    }
    
    letter = generator.generate(test_job)
    print(letter)
