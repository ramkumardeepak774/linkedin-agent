import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from config import Config
from difflib import SequenceMatcher

class ApplicationMemory:
    """
    Stores and retrieves answers to application questions.
    
    SOLID Principles:
    - Single Responsibility: Only manages application Q&A memory
    - Open/Closed: Can extend with different storage backends
    """
    
    def __init__(self, memory_path: Optional[Path] = None):
        self.memory_path = memory_path or Config.DATA_DIR / "application_memory.json"
        self._memory = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load memory from JSON file."""
        if not self.memory_path.exists():
            return {"questions": {}, "metadata": {"created": datetime.now().isoformat()}}
        
        with open(self.memory_path, 'r') as f:
            return json.load(f)
    
    def _save(self):
        """Save memory to JSON file."""
        self._memory["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.memory_path, 'w') as f:
            json.dump(self._memory, f, indent=2)
    
    def _normalize_question(self, question: str) -> str:
        """Normalize question for matching."""
        return question.lower().strip().replace("?", "").replace(".", "")
    
    def _similarity(self, q1: str, q2: str) -> float:
        """Calculate similarity between two questions (0-1)."""
        return SequenceMatcher(None, 
                              self._normalize_question(q1), 
                              self._normalize_question(q2)).ratio()
    
    def get_answer(self, question: str, similarity_threshold: float = 0.8) -> Optional[str]:
        """
        Get answer for a question, using fuzzy matching.
        
        Args:
            question: The question to find answer for
            similarity_threshold: Minimum similarity to consider a match (0-1)
        
        Returns:
            Answer string if found, None otherwise
        """
        # Exact match first
        normalized = self._normalize_question(question)
        for key, data in self._memory["questions"].items():
            if self._normalize_question(data["question"]) == normalized:
                data["last_used"] = datetime.now().isoformat()
                data["use_count"] = data.get("use_count", 0) + 1
                self._save()
                return data["answer"]
        
        # Fuzzy match
        best_match = None
        best_score = 0
        
        for key, data in self._memory["questions"].items():
            score = self._similarity(question, data["question"])
            if score > best_score and score >= similarity_threshold:
                best_score = score
                best_match = data
        
        if best_match:
            best_match["last_used"] = datetime.now().isoformat()
            best_match["use_count"] = best_match.get("use_count", 0) + 1
            self._save()
            return best_match["answer"]
        
        return None
    
    def store_answer(self, question: str, answer: str, field_type: str = "text"):
        """
        Store a question-answer pair.
        
        Args:
            question: The question
            answer: The answer
            field_type: Type of field (text, dropdown, radio, checkbox)
        """
        key = self._normalize_question(question).replace(" ", "_")[:50]
        
        self._memory["questions"][key] = {
            "question": question,
            "answer": answer,
            "type": field_type,
            "created": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
            "use_count": 1
        }
        
        self._save()
        print(f"Stored: '{question}' → '{answer}'")
    
    def get_all_answers(self) -> Dict[str, Any]:
        """Get all stored Q&A pairs."""
        return self._memory["questions"]
    
    def clear(self):
        """Clear all stored answers."""
        self._memory = {"questions": {}, "metadata": {"created": datetime.now().isoformat()}}
        self._save()


# Factory function
def create_application_memory() -> ApplicationMemory:
    """Factory function to create ApplicationMemory."""
    return ApplicationMemory()


if __name__ == "__main__":
    # Test
    memory = create_application_memory()
    
    # Store some answers
    memory.store_answer("How many years of Python experience do you have?", "5", "text")
    memory.store_answer("Are you authorized to work in the US?", "Yes", "radio")
    
    # Retrieve with exact match
    print(memory.get_answer("How many years of Python experience do you have?"))
    
    # Retrieve with fuzzy match
    print(memory.get_answer("Years of Python experience?"))  # Should still match
    
    # Show all
    print(json.dumps(memory.get_all_answers(), indent=2))
