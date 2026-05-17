# Contributing to ContextForge

Thank you for your interest in contributing to ContextForge! We believe that collaborative development leads to better software for everyone. This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors. We are committed to providing a welcoming space for people of all backgrounds and experience levels.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the issue list to avoid duplicates. When you create a bug report, include:

- **Clear description**: What is the bug and what did you expect to happen?
- **Steps to reproduce**: Provide specific steps to reproduce the issue
- **Python version**: Include the Python version you're using
- **Dependencies**: List relevant library versions (langchain-core, tiktoken, etc.)
- **Error messages**: Include full traceback if applicable
- **Code sample**: Provide a minimal code example that triggers the bug

### Suggesting Features

Feature suggestions are welcome! When proposing a feature:

- **Use clear, descriptive language**: Explain the use case and benefits
- **Provide context**: How does this feature fit into ContextForge's mission?
- **Include examples**: Show how the feature would be used
- **Consider alternatives**: Have you thought of other ways to solve this?

### Pull Requests

We accept pull requests from community members. To submit a PR:

1. **Fork the repository** and create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our code standards (see below)

3. **Write or update tests** for your changes
   ```bash
   pytest -v
   ```

4. **Run code formatting** to ensure consistency
   ```bash
   black src/ tests/
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: clear description of changes"
   ```

6. **Push to your fork** and open a pull request
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Local Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/contextforge.git
cd contextforge

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install in development mode with all dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest -v

# Run tests with coverage report
pytest --cov=contextforge tests/

# Run specific test class
pytest tests/test_engine.py::TestAutomatedContextEngine -v

# Run tests matching a pattern
pytest -k "token_budget" -v
```

### Code Formatting

We use Black for code formatting to maintain consistency:

```bash
# Format all Python files
black src/ tests/

# Check formatting without changes
black --check src/ tests/
```

## Code Standards

### Style Guidelines

- **Line length**: Maximum 88 characters (Black default)
- **Imports**: Group and sort using isort conventions
- **Type hints**: Use type hints for all function signatures
- **Docstrings**: Follow Google-style docstring format

### Example Function Structure

```python
def my_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    Brief one-line description of the function.
    
    Longer detailed description explaining the purpose, behavior,
    and any important details about how the function works.
    
    Args:
        param1: Description of param1 and its expected format.
        param2: Description of param2 and its constraints.
        
    Returns:
        Description of the return value and its structure.
        
    Raises:
        ValueError: Description of when this exception is raised.
        TypeError: Description of when this exception is raised.
    """
    # Implementation
    pass
```

### Docstring Standards

- Use triple-quoted strings (""")
- Include parameter and return value documentation
- Document exceptions that can be raised
- Provide usage examples for complex functions
- Keep descriptions concise but complete

## Testing Standards

### Test Coverage Requirements

- New code must have corresponding unit tests
- Tests should cover both success and error paths
- Edge cases and boundary conditions should be tested
- Aim for >80% code coverage

### Test Organization

```python
class TestComponentName:
    """Test suite for ComponentName class."""
    
    def test_basic_functionality(self):
        """Test the primary use case."""
        # Arrange
        # Act
        # Assert
        pass
    
    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ValueError):
            # Code that should raise
            pass
```

## Documentation

### Updating README

If your changes affect usage, please update the README.md with:
- New API endpoints or functions
- New configuration options
- Updated examples
- New sections if introducing major features

### API Documentation

Keep docstrings updated in the code:
- Update docstrings when changing parameters
- Add examples to complex functions
- Document edge cases and limitations

## Commit Messages

Write clear, descriptive commit messages:

```
# Good
commit -m "Add token budget enforcement in AdaptiveContextPool

- Validate token budget before rendering
- Apply word-level compression if budget exceeded
- Add comprehensive error messages for debugging"

# Avoid
commit -m "Fix bug"
commit -m "Update stuff"
```

### Commit Message Format

- First line: Short summary (50 chars max)
- Blank line
- Detailed explanation (wrap at 72 chars)
- Reference related issues: "Fixes #123"

## Release Process

The maintainers follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Code Review Process

When you submit a PR:

1. **Automated checks run**: Tests, formatting, coverage
2. **Code review**: Maintainers review for quality and consistency
3. **Feedback**: Comments and suggestions for improvement
4. **Revisions**: You address feedback with new commits
5. **Approval**: Once approved, PR is merged

## Areas We're Looking For Help

- **Bug fixes**: See open issues labeled "bug"
- **Documentation**: Improve examples, tutorials, API docs
- **Performance**: Optimize hot paths, profile memory usage
- **Testing**: Increase test coverage and add edge cases
- **Features**: Implement features from the roadmap

## Questions?

- Open an issue for questions
- Check existing issues and discussions first
- Ask on GitHub Discussions

## License

By contributing to ContextForge, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make ContextForge better! 🚀
