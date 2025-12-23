# LinkedIn Automation Agent - Architecture

## Design Principles

This project follows **SOLID principles** and industry-standard **design patterns** for maintainability and extensibility.

## SOLID Principles Implementation

### 1. Single Responsibility Principle (SRP)
Each class has one reason to change:
- `BrowserManager`: Only handles browser automation
- `JobAnalyzer`: Only analyzes jobs
- `CoverLetterGenerator`: Only generates cover letters
- `ResumeLoader`: Only loads resume data
- `LLMService`: Only manages LLM communication

### 2. Open/Closed Principle (OCP)
Open for extension, closed for modification:
- **LLM Providers**: Add new providers (e.g., `AnthropicProvider`) without modifying `LLMService`
- **Job Scoring**: Extend scoring logic by subclassing `JobAnalyzer`

### 3. Liskov Substitution Principle (LSP)
Subtypes are substitutable for their base types:
- All `LLMProvider` implementations (`FireworksProvider`, `OpenAIProvider`) can be used interchangeably

### 4. Interface Segregation Principle (ISP)
Clients depend only on methods they use:
- `LLMProvider` interface has minimal methods: `chat()`, `is_available()`, `get_name()`
- No "fat interfaces" forcing unnecessary implementations

### 5. Dependency Inversion Principle (DIP)
Depend on abstractions, not concretions:
- `JobAnalyzer` depends on `LLMService` (abstraction), not specific providers
- `LLMService` depends on `LLMProvider` (interface), not concrete implementations

## Design Patterns

### 1. Strategy Pattern
**Where**: `LLMService` with `LLMProvider` implementations
**Why**: Allows runtime selection of LLM provider (Fireworks vs OpenAI)
```python
# Can swap providers without changing client code
llm = LLMService(providers=[OpenAIProvider()])
```

### 2. Factory Pattern
**Where**: `create_llm_service()`, `create_job_analyzer()`, `create_cover_letter_generator()`
**Why**: Encapsulates object creation, making it easy to change dependencies
```python
# Client doesn't need to know about dependencies
analyzer = create_job_analyzer()
```

### 3. Dependency Injection
**Where**: All service classes accept dependencies via constructor
**Why**: Makes testing easier, reduces coupling
```python
# Dependencies injected, not created internally
analyzer = JobAnalyzer(llm_service, resume_loader)
```

### 4. Chain of Responsibility
**Where**: `LLMService` tries providers in sequence until one succeeds
**Why**: Automatic fallback if primary provider fails
```python
# Tries Fireworks, falls back to OpenAI on failure
response = llm.chat(system, user)
```

## Project Structure

```
linkedin-agent/
├── llm_provider.py          # Abstract base class (Interface)
├── llm_providers.py         # Concrete implementations
├── llm_service.py           # Strategy + Chain of Responsibility
├── job_analyzer.py          # Single Responsibility + DI
├── cover_letter_generator.py # Single Responsibility + DI
├── browser_manager.py       # Browser automation
├── agent_graph.py           # LangGraph workflow
├── database.py              # Data persistence
├── config.py                # Configuration
└── main.py                  # Entry point
```

## Benefits

1. **Testability**: Easy to mock dependencies for unit tests
2. **Maintainability**: Changes localized to single classes
3. **Extensibility**: Add new features without breaking existing code
4. **Readability**: Clear separation of concerns

## Adding New Features

### Example: Add Anthropic LLM Provider

1. Create `AnthropicProvider` implementing `LLMProvider`:
```python
class AnthropicProvider(LLMProvider):
    def chat(self, system_prompt, user_prompt):
        # Implementation
        pass
```

2. Add to `LLMService` initialization:
```python
providers = [FireworksProvider(), AnthropicProvider(), OpenAIProvider()]
```

No changes needed to `JobAnalyzer`, `CoverLetterGenerator`, or any client code!

## Testing

Each component can be tested in isolation:
```python
# Mock LLM service for testing
mock_llm = MockLLMService()
analyzer = JobAnalyzer(mock_llm, mock_resume_loader)
result = analyzer.analyze(test_job)
```
