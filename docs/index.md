# ContextForge Documentation

Welcome to the ContextForge documentation hub! This is your comprehensive resource for understanding, using, and contributing to ContextForge.

## 📚 Documentation Sections

### Getting Started
- **[Getting Started Guide](GETTING_STARTED.md)** - Start here if you're new to ContextForge
- **[Installation Guide](GETTING_STARTED.md#installation)** - Step-by-step setup instructions
- **[Quick Start Examples](EXAMPLES.md#quick-start)** - Running code immediately

### Learning
- **[Architecture Deep Dive](ARCHITECTURE.md)** - Understand the design philosophy and system layers
- **[API Reference](API_REFERENCE.md)** - Complete API documentation with types and signatures
- **[Examples & Patterns](EXAMPLES.md)** - Real-world usage patterns and advanced techniques
- **[Component Guide](ARCHITECTURE.md#components)** - Learn about component lifecycle and priorities

### Contributing
- **[Development Setup](DEVELOPMENT.md)** - Get your development environment ready
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute code, docs, and features
- **[Community Guidelines](COMMUNITY.md)** - Our values, code of conduct, and support channels
- **[Roadmap](ROADMAP.md)** - See what's planned and how you can help

### Reference
- **[Glossary](ARCHITECTURE.md#glossary)** - Key terminology and concepts
- **[FAQ](COMMUNITY.md#faq)** - Frequently asked questions
- **[Troubleshooting](DEVELOPMENT.md#troubleshooting)** - Debug common issues

---

## 🚀 Quick Links

### For Users
```python
from contextforge.engine import AutomatedContextEngine

engine = AutomatedContextEngine(max_tokens=4000)
result = engine.invoke(payload)
```
→ Learn more in [Quick Start](EXAMPLES.md#quick-start)

### For Contributors
1. Read [Community Guidelines](COMMUNITY.md)
2. Set up [Development Environment](DEVELOPMENT.md)
3. Check [Roadmap](ROADMAP.md) for issues to work on
4. Follow [Contributing Guide](../CONTRIBUTING.md)

### For Maintainers
- [Release Process](DEVELOPMENT.md#release-process)
- [Performance Benchmarks](ARCHITECTURE.md#performance)
- [Deployment Guide](DEVELOPMENT.md#deployment)

---

## 📖 Core Concepts

### Three Core Questions About ContextForge

**Q1: What problem does it solve?**
```
Static prompt concatenation → Token overflow, information loss, runaway costs
ContextForge Solution → Dynamic, token-aware component graph with priority scheduling
```

**Q2: How is it different?**
```
Traditional frameworks: Prompts as strings
ContextForge: Prompts as React-like component DAGs with deterministic rendering
```

**Q3: When should I use it?**
```
✓ Production LLM applications (RAG, chat systems)
✓ Token-budget-critical environments
✓ Complex context composition
✗ Simple single-prompt scenarios
```

---

## 🌟 Key Features

| Feature | Benefit |
|---------|---------|
| **Component-Based** | Reusable, composable prompt building blocks |
| **Token-Aware** | Guaranteed budget compliance with automatic compression |
| **Priority Scheduling** | System invariants always get space first |
| **Hybrid Fusion** | Seamlessly merge vector and BM25 search results |
| **Lost-in-Middle Mitigation** | Intelligent document placement for peak LLM attention |
| **LCEL Native** | Drop-in LangChain integration with pipe operator |

---

## 🤝 Getting Help

### Ask a Question
- 💬 [GitHub Discussions](https://github.com/contextforge/contextforge/discussions)
- 🐛 [Report a Bug](https://github.com/contextforge/contextforge/issues)
- ✨ [Request a Feature](https://github.com/contextforge/contextforge/issues)

### Stay Updated
- 🌟 Star the repository
- 👀 Watch for releases
- 📰 Subscribe to [announcements](https://github.com/contextforge/contextforge/releases)

---

## 📊 Project Statistics

- **Active Contributors**: Growing community
- **Open Issues**: Welcoming for new contributors
- **Code Coverage**: >85%
- **Python Versions**: 3.10+
- **License**: MIT (Free & Open Source)

---

## 🗺️ Learning Path

### Beginner
1. Read [Getting Started](GETTING_STARTED.md)
2. Run [Quick Start Examples](EXAMPLES.md#quick-start)
3. Explore [API Reference](API_REFERENCE.md)

### Intermediate
1. Study [Architecture](ARCHITECTURE.md)
2. Build [Custom Components](EXAMPLES.md#custom-components)
3. Integrate with [LangChain Chains](EXAMPLES.md#langchain-integration)

### Advanced
1. Understand [Priority Scheduling](ARCHITECTURE.md#priority-scheduling)
2. Implement [Custom Algorithms](EXAMPLES.md#advanced-patterns)
3. Contribute [New Features](DEVELOPMENT.md#contributing-features)

---

## 💡 Design Philosophy

ContextForge is built on three core principles:

1. **Declarative First** - Describe intent, not implementation
2. **Token-Aware Always** - Every decision respects budget boundaries
3. **Production-Ready** - Works seamlessly in enterprise environments

---

## 📝 Documentation License

All documentation is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Code examples are licensed under [MIT](../LICENSE).

---

**Last Updated**: May 2026 | [View History](https://github.com/contextforge/contextforge/commits/main/docs/)

For the most up-to-date information, always refer to the [GitHub repository](https://github.com/contextforge/contextforge).
