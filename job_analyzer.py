from typing import Dict, Any
from pathlib import Path
from llm_service import LLMService, create_llm_service
from config import Config

class ResumeLoader:
    """
    Single Responsibility: Load and manage resume data.
    """
    
    def __init__(self, resume_path: Path):
        self._resume_path = resume_path
        self._resume_content = None
    
    def load(self) -> str:
        """Load resume from file, creating example if not exists."""
        if self._resume_content:
            return self._resume_content
        
        if not self._resume_path.exists():
            print(f"WARNING: Resume not found at {self._resume_path}")
            print("Creating example resume. Please update data/resume.txt!")
            
            example = """
Skills: Python, Machine Learning, TensorFlow, PyTorch, AWS, Docker
Experience: 3 years as Machine Learning Engineer
- Built recommendation systems serving 1M+ users
- Deployed ML models to production using AWS SageMaker
- Developed NLP pipelines for text classification
Education: BS Computer Science
Target Role: Senior Machine Learning Engineer
"""
            self._resume_path.write_text(example.strip())
            self._resume_content = example.strip()
        else:
            self._resume_content = self._resume_path.read_text().strip()
        
        return self._resume_content


class JobAnalyzer:
    """
    Analyzes jobs and scores them based on resume match.
    
    SOLID Principles:
    - Single Responsibility: Only analyzes jobs
    - Dependency Inversion: Depends on LLMService abstraction
    - Open/Closed: Can extend scoring logic without modifying core
    """
    
    def __init__(self, llm_service: LLMService, resume_loader: ResumeLoader):
        """
        Dependency Injection: Inject dependencies instead of creating them.
        
        Args:
            llm_service: LLM service for analysis
            resume_loader: Resume data loader
        """
        self._llm = llm_service
        self._resume_loader = resume_loader
        self._resume = resume_loader.load()
    
    def analyze(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a job and return scoring data.
        
        Args:
            job_data: Dict with keys: title, company, description (optional)
        
        Returns:
            Dict: {
                "score": 85,
                "reason": "Strong ML skills match",
                "should_apply": True,
                "matching_skills": [...],
                "missing_skills": [...]
            }
        """
        job_title = job_data.get("title", "Unknown")
        company = job_data.get("company", "Unknown")
        job_desc = job_data.get("description", "No description available")
        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(job_title, company, job_desc)
        
        try:
            result = self._llm.chat_json(system_prompt, user_prompt)
            result["should_apply"] = result["score"] >= Config.MIN_JOB_SCORE
            return result
        except Exception as e:
            print(f"Error analyzing job: {e}")
            return self._get_default_result(str(e))
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for job analysis."""
        return """You are an expert career advisor and job matcher.
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
    
    def _build_user_prompt(self, title: str, company: str, desc: str) -> str:
        """Build user prompt with job and resume data."""
        return f"""
Candidate Resume:
{self._resume}

Job Posting:
Title: {title}
Company: {company}
Description: {desc}

Analyze this job and respond with JSON:
{{
    "score": <0-100>,
    "reason": "<brief explanation>",
    "matching_skills": ["skill1", "skill2"],
    "missing_skills": ["skill1", "skill2"]
}}
"""
    
    def _get_default_result(self, error_msg: str) -> Dict[str, Any]:
        """Return default low score on error."""
        return {
            "score": 0,
            "reason": f"Analysis failed: {error_msg}",
            "should_apply": False,
            "matching_skills": [],
            "missing_skills": []
        }


# Factory function
def create_job_analyzer() -> JobAnalyzer:
    """Factory function to create JobAnalyzer with default dependencies."""
    llm_service = create_llm_service()
    resume_loader = ResumeLoader(Config.RESUME_PATH)
    return JobAnalyzer(llm_service, resume_loader)


if __name__ == "__main__":
    # Test
    analyzer = create_job_analyzer()
    
    test_job = {
        "title": "Senior Machine Learning Engineer",
        "company": "Google",
        "description": "We need someone with Python, TensorFlow, and 5+ years ML experience"
    }
    
    result = analyzer.analyze(test_job)
    print(f"Score: {result['score']}")
    print(f"Reason: {result['reason']}")
    print(f"Should Apply: {result['should_apply']}")
