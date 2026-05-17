# Contributing to ContextForge 👥

Thank you for your interest in helping build the industry standard for context engineering! We love pull requests.

## 🧬 Code Architecture Paradigm

ContextForge follows two immutable engineering rules:
1. **Always LLM-Agnostic**: All core components process data and manage token layouts purely as text strings or native LangChain `PromptValue` envelopes. Never bind a component to a specific vendor model API.
2. **Deterministic Token Allocation**: Components must never blindly exceed token constraints. Use the token tracking APIs to guarantee strict allocation compliance before execution.

## 🛠️ Local Development Workflow

1. Fork the repository on GitHub and clone your fork locally.
2. Activate your isolated virtual workspace environment.
3. Install the package in editable mode with development testing tools:
   ```bash
   pip install -e ".[dev]"
   ```

## 🧪 Submission Checklist

Before opening a Pull Request, verify your changes conform to our workspace rules:
* Run the codebase lint checks using `black .` to keep styles clean.
* Add comprehensive unit test validation files inside the `tests/` directory.
* Run the full testing suite locally using `pytest` and verify all tests pass.
