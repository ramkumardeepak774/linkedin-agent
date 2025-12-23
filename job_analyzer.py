from llm_service import LLMService
from config import Config
from pathlib import Path

class JobAnalyzer:
    def __init__(self):
        self.llm = LLMService()
        self.resume = self._load_resume()
    
    def _load_resume(self):
        """Load user's resume from file."""
        if not Config.RESUME_PATH.exists():
            print(f"WARNING: Resume not found at {Config.RESUME_PATH}")
            print("Creating example resume. Please update data/resume.txt with your actual resume!")
            
            example_resume = """
Skills: Python, Machine Learning, TensorFlow, PyTorch, AWS, Docker
Experience: 3 years as Machine Learning Engineer
- Built recommendation systems serving 1M+ users
- Deployed ML models to production using AWS SageMaker
- Developed NLP pipelines for text classification
Education: BS Computer Science
Target Role: Senior Machine Learning Engineer
"""
            Config.RESUME_PATH.write_text(example_resume.strip())
            return example_resume.strip()
        
        return Config.RESUME_PATH.read_text().strip()
    
    def analyze_job(self, job_data):
        """
        Analyze a job and return a score (0-100) and reasoning.
        
        Args:
            job_data: Dict with keys: title, company, description (optional), url
        
        Returns:
            Dict: {"score": 85, "reason": "Strong ML skills match", "should_apply": True}
        """
        job_title = job_data.get("title", "Unknown")
        company = job_data.get("company", "Unknown")
        job_desc = job_data.get("description", "No description available")
        
        system_prompt = """You are an expert career advisor and job matcher.
Your task is to analyze job postings and score them based on how well they match a candidate's resume.

Scoring criteria:
- 90-100: Perfect match, highly relevant role
- 70-89: Good match, most requirements met
- 50-69: Moderate match, some skills align
- 30-49: Weak match, few skills align
- 0-29: Poor match, not relevant

Consider:
1. Skills match (technical and soft skills)
2. Experience level alignment
3. Role relevance to career goals
4. Company reputation (if known)
"""
        
        user_prompt = f"""
Candidate Resume:
{self.resume}

Job Posting:
Title: {job_title}
Company: {company}
Description: {job_desc}

Analyze this job and respond with JSON:
{{
    "score": <0-100>,
    "reason": "<brief explanation>",
    "matching_skills": ["skill1", "skill2"],
    "missing_skills": ["skill1", "skill2"]
}}
"""
        
        try:
            result = self.llm.chat_json(system_prompt, user_prompt)
            result["should_apply"] = result["score"] >= Config.MIN_JOB_SCORE
            return result
        except Exception as e:
            print(f"Error analyzing job: {e}")
            # Return default low score on error
            return {
                "score": 0,
                "reason": f"Analysis failed: {str(e)}",
                "should_apply": False,
                "matching_skills": [],
                "missing_skills": []
            }

if __name__ == "__main__":
    # Test
    analyzer = JobAnalyzer()
    
    test_job = {
        "title": "Senior Machine Learning Engineer",
        "company": "Google",
        "description": "We need someone with Python, TensorFlow, and 5+ years ML experience"
    }
    
    result = analyzer.analyze_job(test_job)
    print(f"Score: {result['score']}")
    print(f"Reason: {result['reason']}")
    print(f"Should Apply: {result['should_apply']}")
