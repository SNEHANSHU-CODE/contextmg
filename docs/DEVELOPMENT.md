# ContextForge Development Guide

Complete guide for setting up, developing, testing, and deploying ContextForge.

---

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Testing](#testing)
5. [Code Quality](#code-quality)
6. [Contributing Changes](#contributing-changes)
7. [Release Process](#release-process)
8. [Troubleshooting](#troubleshooting)

---

## Development Environment Setup

### Prerequisites

- **Python 3.10** or higher
- **Git** for version control
- **pip** for package management
- 2GB disk space minimum

### Step 1: Clone Repository

```bash
git clone https://github.com/contextforge/contextforge.git
cd contextforge
```

### Step 2: Create Virtual Environment

```bash
# Using venv (recommended)
python -m venv .venv

# Activate environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
# Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Install in development mode with all dependencies
pip install -e ".[dev]"
```

### Step 4: Verify Installation

```bash
# Check imports
python -c "from contextforge import *; print('✓ ContextForge installed')"

# Run tests
pytest --version
black --version
```

### Optional: IDE Setup

#### VS Code

```bash
# Install recommended extensions
code --install-extension ms-python.python
code --install-extension ms-python.pylance
code --install-extension ms-python.vscode-pylance
```

**settings.json:**
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "ms-python.python"
    }
}
```

#### PyCharm

```bash
# Set Python interpreter
Settings → Project → Python Interpreter → Add → Existing Environment
# Select: .venv/bin/python
```

---

## Project Structure

```
contextforge/
├── .github/
│   ├── workflows/          # CI/CD pipelines
│   └── ISSUE_TEMPLATE/     # Issue templates
├── docs/
│   ├── index.md            # Documentation hub
│   ├── GETTING_STARTED.md  # Quick start
│   ├── ARCHITECTURE.md     # Design deep dive
│   ├── API_REFERENCE.md    # API docs
│   ├── EXAMPLES.md         # Usage patterns
│   ├── DEVELOPMENT.md      # This file
│   ├── COMMUNITY.md        # Community guidelines
│   └── ROADMAP.md          # Feature roadmap
├── src/contextforge/
│   ├── __init__.py         # Package initialization
│   ├── base.py             # Component abstractions (360 lines)
│   ├── engine.py           # Orchestration engine (450 lines)
│   ├── components/         # Component implementations
│   │   └── __init__.py
│   └── integration/        # Framework integrations
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── test_engine.py      # Engine tests (450+ lines)
│   ├── test_components.py  # Component tests
│   └── fixtures/           # Test fixtures
├── pyproject.toml          # Build configuration
├── README.md               # Project overview
├── CONTRIBUTING.md         # Contribution guidelines
├── LICENSE                 # MIT License
├── .gitignore              # Git ignore rules
└── .pre-commit-config.yaml # Pre-commit hooks
```

---

## Development Workflow

### Step 1: Create Feature Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch (use descriptive name)
git checkout -b feature/my-feature
# OR for bugfixes:
git checkout -b fix/issue-123

# Branch naming convention:
# feature/description-of-feature
# fix/issue-description
# docs/documentation-update
# test/test-improvement
```

### Step 2: Make Changes

```bash
# Edit files in src/contextforge/

# Add corresponding tests in tests/

# Update documentation if needed

# Run code frequently:
pytest tests/test_engine.py -v    # Test during development
black src/ tests/                 # Format code
```

### Step 3: Write Tests

**Test locations:**
- `tests/test_engine.py` - Engine tests
- `tests/test_components.py` - Component tests
- `tests/fixtures/` - Reusable test data

**Test structure:**
```python
import pytest
from contextforge.engine import AutomatedContextEngine

class TestFeatureName:
    """Test suite for feature name."""
    
    def test_basic_functionality(self):
        """Test the primary use case."""
        # Arrange
        engine = AutomatedContextEngine()
        payload = {...}
        
        # Act
        result = engine.invoke(payload)
        
        # Assert
        assert result is not None
        assert isinstance(result, PromptValue)
    
    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ValueError):
            # Should raise
            pass
```

### Step 4: Run Tests and Linting

```bash
# Run specific test file
pytest tests/test_engine.py -v

# Run specific test class
pytest tests/test_engine.py::TestAutomatedContextEngine -v

# Run specific test
pytest tests/test_engine.py::TestAutomatedContextEngine::test_token_budget -v

# Run with coverage
pytest --cov=contextforge --cov-report=html tests/

# Format code
black src/ tests/

# Check formatting
black --check src/ tests/

# Lint (if configured)
pylint src/contextforge/

# Type checking
mypy src/contextforge/
```

### Step 5: Commit Changes

```bash
# Stage changes
git add src/ tests/ docs/

# Commit with descriptive message
git commit -m "feat: add token budget enforcement in AdaptiveContextPool

- Implement strict budget validation
- Add word-level compression fallback
- Include comprehensive error messages
- Add 15 new test cases

Fixes #123"
```

**Commit message format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:** feat, fix, docs, test, refactor, perf, style, chore

### Step 6: Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/my-feature

# Create PR on GitHub
# - Fill in PR template
# - Link related issues: Fixes #123
# - Add description of changes
# - Request reviewers
```

---

## Testing

### Test Coverage Targets

- **Overall**: >85% coverage
- **Core modules**: >90% coverage
- **Tests must include**: success paths, error conditions, edge cases

### Running Tests

```bash
# All tests
pytest

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Run specific marker
pytest -m unit

# Coverage report
pytest --cov=contextforge --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=contextforge --cov-report=html
# View: open htmlcov/index.html
```

### Writing Tests

**Good test characteristics:**
- ✓ Descriptive names: `test_token_budget_enforcement_on_large_documents`
- ✓ Single responsibility: One concept per test
- ✓ Independent: Tests don't depend on each other
- ✓ Fast: Most tests complete in <100ms
- ✓ Deterministic: Same result every run

**Test fixtures:**
```python
import pytest

@pytest.fixture
def sample_engine():
    """Create engine for tests."""
    return AutomatedContextEngine(max_tokens=2000)

@pytest.fixture
def sample_documents():
    """Create sample documents."""
    return [
        Document(page_content="...", metadata={"id": "d1", "score": 0.95}),
        Document(page_content="...", metadata={"id": "d2", "score": 0.70}),
    ]

def test_with_fixtures(sample_engine, sample_documents):
    """Use fixtures."""
    result = sample_engine.invoke({
        "query": "Test",
        "chat_history": [],
        "vector_docs": sample_documents,
        "bm25_docs": []
    })
    assert result is not None
```

### CI/CD Testing

Tests run automatically on:
- **Push to main**: Full test suite
- **Pull requests**: Full test suite + coverage check
- **Release tags**: Full suite + cross-platform

---

## Code Quality

### Formatting with Black

```bash
# Format all Python files
black src/ tests/

# Check without formatting
black --check src/ tests/

# Line length (default 88)
black --line-length 100 src/
```

**Black configuration** (pyproject.toml):
```toml
[tool.black]
line-length = 88
target-version = ['py310', 'py311', 'py312']
```

### Type Checking

```bash
# Check types (if mypy configured)
mypy src/contextforge/

# Strict mode
mypy --strict src/contextforge/
```

### Linting

```bash
# Pylint (if installed)
pylint src/contextforge/

# Flake8 (if installed)
flake8 src/ tests/

# Ruff (fast alternative)
ruff check src/ tests/
```

### Pre-commit Hooks

```bash
# Install pre-commit framework
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

---

## Code Style Guide

### Python Style

```python
# Good: Clear, documented, type-hinted
def calculate_token_budget(
    max_tokens: int,
    used_tokens: int
) -> int:
    """
    Calculate remaining token budget.
    
    Args:
        max_tokens: Maximum total tokens
        used_tokens: Tokens already consumed
    
    Returns:
        Remaining token budget
    
    Raises:
        ValueError: If max_tokens is negative
    """
    if max_tokens < 0:
        raise ValueError("max_tokens must be non-negative")
    
    return max(0, max_tokens - used_tokens)


# Avoid: Unclear, no documentation
def calc(m, u):
    return max(0, m - u)
```

### Documentation

```python
# Module-level docstring
"""
This module implements token budget allocation algorithms.

Token budgets are strictly enforced across all components
to prevent context overflow and ensure deterministic behavior.
"""

# Class docstring
class TokenAllocator:
    """Manages token distribution across components."""
    
    # Method docstring
    def allocate(self, budget: int) -> Dict[str, int]:
        """Allocate budget across components."""
        pass
```

### Imports

```python
# Order: standard library, third-party, local
import json
from typing import Dict, List

import tiktoken
from langchain_core.documents import Document

from contextforge.base import BaseContextComponent
```

---

## Contributing Changes

### Before You Start

1. **Check existing issues/PRs** - Don't duplicate work
2. **Discuss large changes** - Open an issue first
3. **Follow style guide** - Format with Black
4. **Write tests** - Required for all code changes

### PR Checklist

Before submitting PR, verify:

- [ ] Code follows Black formatting (`black src/ tests/`)
- [ ] All tests pass (`pytest -v`)
- [ ] Coverage maintained (>85% overall)
- [ ] Documentation updated if needed
- [ ] Docstrings added/updated
- [ ] Type hints included
- [ ] No commented-out code
- [ ] Commit messages are clear
- [ ] Related issues mentioned

### PR Review Process

1. **Automated checks** run (tests, formatting, coverage)
2. **Maintainer review** (2-3 days)
3. **Feedback incorporated** (you update PR)
4. **Approval** and merge

---

## Release Process

### Version Numbers

We follow semantic versioning: `MAJOR.MINOR.PATCH`

- **PATCH** (0.0.x): Bug fixes, internal improvements
- **MINOR** (0.x.0): New features, backward compatible
- **MAJOR** (x.0.0): Breaking changes

### Release Steps

```bash
# 1. Update version in pyproject.toml
# version = "0.2.0"

# 2. Update CHANGELOG.md
# - List all changes
# - Note breaking changes
# - Credit contributors

# 3. Create release tag
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0

# 4. Build distribution
python -m build

# 5. Upload to PyPI
python -m twine upload dist/*

# 6. Create GitHub release
# - Tag: v0.2.0
# - Title: ContextForge 0.2.0
# - Description: Changelog content
```

### Release Checklist

- [ ] Tests pass on all Python versions
- [ ] Documentation updated
- [ ] Version number bumped
- [ ] Changelog updated
- [ ] Contributors credited
- [ ] Git tag created
- [ ] PyPI package published
- [ ] GitHub release created

---

## Troubleshooting

### Common Issues

#### Issue: "ImportError: No module named 'contextforge'"

```bash
# Solution: Install in development mode
pip install -e .

# Or verify installation
pip list | grep contextforge
```

#### Issue: "ModuleNotFoundError: No module named 'tiktoken'"

```bash
# Solution: Install dependencies
pip install -e ".[dev]"

# Or manually
pip install tiktoken langchain-core
```

#### Issue: "Test failures on Python 3.11"

```bash
# Solution: Update dependencies
pip install --upgrade --force-reinstall tiktoken

# Check Python version
python --version

# Check tiktoken version compatibility
pip list | grep tiktoken
```

#### Issue: "Black/Pylint not found"

```bash
# Solution: Install development dependencies
pip install -e ".[dev]"

# This installs: pytest, black, google-genai, etc.
```

#### Issue: "Permission denied" when running tests

```bash
# Solution: Check file permissions
chmod +x tests/*.py

# Or regenerate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### Debugging

```bash
# Run with debug output
pytest -vv --tb=long

# Run specific test with debugging
pytest tests/test_engine.py::TestClass::test_method -vv -s

# Print statements show with -s flag
def test_something():
    print("Debug output")  # Shows with pytest -s
    assert True
```

### Performance Profiling

```bash
# Profile a test
python -m cProfile -s cumulative test_script.py

# Memory profiling (if memory_profiler installed)
pip install memory-profiler
python -m memory_profiler test_script.py
```

---

## Useful Commands Reference

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Development
pytest -v                          # Run tests
black src/ tests/                  # Format code
pytest --cov=contextforge tests/   # Coverage report

# Before commit
black src/ tests/
pytest -v
pytest --cov=contextforge tests/ --cov-report=term-missing

# Creating PR
git checkout -b feature/name
# ... make changes ...
git add .
git commit -m "feat: description"
git push origin feature/name
# Create PR on GitHub

# After merge
git checkout main
git pull origin main
git branch -d feature/name
```

---

## Additional Resources

- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Black Documentation](https://black.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [ContextForge Architecture](ARCHITECTURE.md)

---

**Last Updated**: May 2026 | **Development Guide Version**: 1.0.0
