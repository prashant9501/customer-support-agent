# Contributing to Customer Support Agent

Thank you for considering contributing to the Customer Support Agent project! This document provides guidelines for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**Bug Report Should Include:**
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages and logs
- Screenshots if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues.

**Enhancement Suggestion Should Include:**
- Clear, descriptive title
- Detailed description of the proposed feature
- Use cases and benefits
- Possible implementation approach

### Pull Requests

1. **Fork the Repository**
   ```bash
   git clone https://github.com/your-username/customer-support-agent.git
   cd customer-support-agent
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make Your Changes**
   - Follow the code style guide
   - Add tests for new functionality
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   cd backend
   pytest tests/ -v
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature X"
   # or
   git commit -m "fix: resolve issue with Y"
   ```

   **Commit Message Format:**
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting, etc.)
   - `refactor:` - Code refactoring
   - `test:` - Adding or updating tests
   - `chore:` - Maintenance tasks

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template
   - Wait for review

## Development Setup

### Prerequisites
- Python 3.11+
- Git
- Virtual environment tool

### Setup Steps

```bash
# Clone repository
git clone https://github.com/your-username/customer-support-agent.git
cd customer-support-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create .env file
cp .env.example .env
# Add your OPENAI_API_KEY

# Initialize database
python -c "from app.database.vectordb import initialize_vectordb; initialize_vectordb()"

# Run tests
pytest tests/ -v
```

## Code Style Guide

### Python Code

**Follow PEP 8:**
```python
# Good
def categorize_inquiry(state: CustomerSupportState) -> Dict[str, str]:
    """
    Categorize customer query into: Technical, Billing, or General
    
    Args:
        state: Current workflow state containing customer_query
        
    Returns:
        Dictionary with query_category field
    """
    query = state["customer_query"]
    # ...
```

**Use Type Hints:**
```python
from typing import Dict, List, Optional

def search_knowledge_base(
    query: str,
    category_filter: Optional[str] = None,
    top_k: int = 3
) -> List[Document]:
    # ...
```

**Write Docstrings:**
```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When input is invalid
    """
```

**Use Meaningful Names:**
```python
# Good
user_query = request.query
category_result = categorize_inquiry(state)

# Bad
q = request.query
res = categorize_inquiry(state)
```

### JavaScript Code

**Use ES6+ Features:**
```javascript
// Good
const sendMessage = async (query) => {
    const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        body: JSON.stringify({ query })
    });
    return response.json();
};

// Use const/let, not var
const API_BASE = window.location.origin;
let sessionId = null;
```

**Add JSDoc Comments:**
```javascript
/**
 * Send message to API
 * @param {string} query - User's query text
 * @returns {Promise<Object>} API response
 */
async function sendMessage(query) {
    // ...
}
```

## Testing Guidelines

### Writing Tests

**Test Structure:**
```python
import pytest

class TestFeatureName:
    """Test feature X"""
    
    def test_specific_behavior(self):
        """Test that X does Y when Z"""
        # Arrange
        input_data = create_test_data()
        
        # Act
        result = function_under_test(input_data)
        
        # Assert
        assert result == expected_value
```

**Use Fixtures:**
```python
@pytest.fixture
def sample_query():
    return "What payment methods do you support?"

def test_categorization(sample_query):
    result = categorize_inquiry({"customer_query": sample_query})
    assert "category" in result
```

**Test Coverage:**
- Aim for >80% code coverage
- Test happy paths and edge cases
- Test error handling

**Run Tests:**
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_agents.py -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html
```

## Documentation

### Update Documentation When:
- Adding new features
- Changing API endpoints
- Modifying configuration
- Fixing bugs that affect usage

### Documentation Files:
- `README.md` - Main documentation
- `QUICKSTART.md` - Getting started guide
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- Code docstrings - Inline documentation

## Project Structure

```
customer-support-agent/
├── backend/
│   ├── app/
│   │   ├── agents/      # Add new agents here
│   │   ├── workflows/   # Modify workflows here
│   │   ├── models/      # Add new schemas here
│   │   └── main.py      # Add new endpoints here
│   ├── tests/           # Add tests here
│   └── requirements.txt # Add dependencies here
│
├── frontend/
│   ├── static/
│   │   ├── css/        # Style changes
│   │   └── js/         # Frontend logic
│   └── index.html      # UI structure
│
└── deployment/         # Deployment configs
```

## Review Process

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No sensitive data in commits
- [ ] Commit messages are clear
- [ ] PR description explains changes

### Review Timeline
- Initial review: Within 2 business days
- Follow-up: Within 1 business day
- Merge: After approval from maintainer

## Questions?

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: support@k21academy.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing! 🎉**
