# Community Guidelines for ContextForge

Welcome to the ContextForge community! This document outlines our values, expectations, and how to get involved.

---

## Table of Contents

1. [Our Mission](#our-mission)
2. [Code of Conduct](#code-of-conduct)
3. [Community Values](#community-values)
4. [How to Get Help](#how-to-get-help)
5. [Ways to Contribute](#ways-to-contribute)
6. [Communication Channels](#communication-channels)
7. [Recognition](#recognition)
8. [FAQ](#faq)

---

## Our Mission

ContextForge exists to democratize prompt engineering for production AI systems. We believe:

- **Context engineering should be declarative**, not imperative string concatenation
- **Token budgets should be respected**, eliminating runaway costs and information loss
- **Open source is better**, built collaboratively by the community
- **Production matters**, so reliability and performance are non-negotiable

Together, we're building the **React of prompt engineering**.

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all, regardless of:
- Age, body size, visible or invisible disability
- Ethnicity, sex characteristics, gender identity and expression
- Level of experience, education, socio-economic status
- Nationality, personal appearance, race, religion
- Sexual identity and orientation, or other characteristics

### Our Standards

**Positive behaviors include:**
- Using welcoming and inclusive language
- Being respectful of differing opinions and experiences
- Giving and gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- The use of sexualized language or imagery
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Violations can be reported to [conduct@contextforge.dev](mailto:conduct@contextforge.dev). All reports are confidential and investigated promptly.

**Consequences range from:**
1. Warning and conversation with the person
2. Temporary muting or suspension
3. Permanent removal from community spaces

---

## Community Values

### 1. **Collaboration Over Competition**

We succeed together. Share ideas, help others, and celebrate collective wins.

```
✓ "I built X. What do you think? How can we improve it?"
✗ "My solution is obviously better than yours"
```

### 2. **Transparency First**

Be honest about limitations, challenges, and decisions.

```
✓ "This feature didn't work because of X. Here's how we're fixing it."
✗ "Don't worry about it, it's fine"
```

### 3. **Quality Matters**

We prioritize doing things well over doing things fast.

```
✓ Thorough PRs with tests and documentation
✗ Quick hacks with "I'll fix it later"
```

### 4. **Documentation is Code**

Good docs are as important as good code.

```
✓ Examples, use cases, and comprehensive docstrings
✗ "The code is self-documenting"
```

### 5. **Learning is Welcome**

This is a space for growing together. Questions are valued.

```
✓ "I don't understand this part, can someone explain?"
✗ Silence, not asking questions to avoid "looking dumb"
```

---

## How to Get Help

### Ask a Question

**GitHub Discussions** (Recommended)
- Best for: General questions, design discussions, best practices
- [Ask a Question](https://github.com/contextforge/contextforge/discussions/new?category=q-a)

**GitHub Issues** (For Bugs)
- Best for: Reporting bugs with reproducible examples
- [Report an Issue](https://github.com/contextforge/contextforge/issues/new)

**Discord/Slack** (When Available)
- Best for: Real-time chat and community
- Join our [Discord Server](https://discord.gg/contextforge)

### Getting Your Question Answered

**To maximize response time:**
1. Search existing discussions/issues first
2. Provide minimal reproducible example
3. Include Python version, OS, dependency versions
4. Describe what you expected vs. what happened

**Example Good Question:**
```
## Issue
When I use AdaptiveContextPool with large documents,
the output is sometimes truncated unexpectedly.

## Steps to reproduce
1. Create engine with max_tokens=500
2. Add 5 documents of ~500 tokens each
3. Call invoke()

## Expected
All 5 documents included (with compression if needed)

## Actual
Only 2 documents appear in output

## Environment
- Python 3.10.5
- contextforge==0.1.0
- tiktoken==0.5.1
```

### Common Questions (FAQ)

**Q: Is ContextForge production-ready?**
A: Yes! We follow semantic versioning and maintain >85% test coverage. Version 1.0.0+ recommended for production.

**Q: Can I use ContextForge with LLM X?**
A: ContextForge is LLM-agnostic. It works with OpenAI, Anthropic, Cohere, open-source models, etc. It outputs `StringPromptValue` compatible with any LLM.

**Q: What Python versions are supported?**
A: Python 3.10+ is required. We test on 3.10, 3.11, 3.12.

**Q: How does ContextForge handle multilingual text?**
A: Tiktoken's CL100K encoding supports UTF-8. Token counts are accurate for most languages.

**Q: Can I customize the token budget allocation?**
A: Yes! Create custom `BaseContextComponent` subclasses with your own allocation logic.

**Q: Is ContextForge's output reproducible?**
A: Completely! Given same input + same tiktoken version = identical output.

**Q: Can I contribute to ContextForge?**
A: Absolutely! See [Ways to Contribute](#ways-to-contribute) section.

---

## Ways to Contribute

### 1. **Code Contributions** 👨‍💻

**Good for:** Developers who want to build features

```bash
git clone https://github.com/contextforge/contextforge.git
cd contextforge
pip install -e ".[dev]"

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes, test, commit
pytest -v
black .

# Push and create PR
git push origin feature/amazing-feature
```

**Issues to start with:**
- Look for "good-first-issue" label
- Check [Roadmap](ROADMAP.md) for planned features
- See [Development Guide](DEVELOPMENT.md)

### 2. **Documentation** 📚

**Good for:** Writers, teachers, and detail-oriented folks

**Opportunities:**
- Improve existing docs (spelling, clarity, examples)
- Write tutorials for common use cases
- Create community guides and recipes
- Translate documentation

**How to contribute:**
```bash
# Fork, edit docs/*.md, commit, PR
# All edits go to docs/ folder
```

### 3. **Examples & Recipes** 🍳

**Good for:** Users who've found cool patterns

**Opportunities:**
- Create example applications
- Write blog posts about use cases
- Build integration examples (with Pinecone, Weaviate, etc.)
- Create video tutorials

**Repository:**
- [ContextForge Examples](https://github.com/contextforge/contextforge-examples)

### 4. **Bug Reports** 🐛

**Good for:** Thorough testers

**What helps:**
- Minimal reproducible example
- Clear expected vs. actual behavior
- Environment details (Python, OS, versions)
- Stack trace if applicable

**Template:**
```markdown
## Describe the bug
What happened?

## Steps to reproduce
1. ...
2. ...

## Expected behavior
What should happen?

## Environment
- Python version: 
- OS: 
- contextforge version: 
```

### 5. **Feature Requests** ✨

**Good for:** Users with ideas

**Template:**
```markdown
## Feature request
Clear, descriptive title

## Problem
What problem does this solve?

## Solution
How should this work?

## Examples
How would someone use it?

## Alternatives
Other solutions you considered?
```

### 6. **Community Support** 🤝

**Good for:** Experienced users and maintainers

**Opportunities:**
- Answer questions on GitHub Discussions
- Help new contributors get started
- Review PRs and provide feedback
- Mentor newcomers

### 7. **Testing & Quality Assurance** ✅

**Good for:** Attention-to-detail folks

**Opportunities:**
- Run ContextForge on edge cases
- Test across different Python versions
- Try unusual combinations
- Report performance issues

---

## Communication Channels

### Official Channels

| Channel | Best For | Link |
|---------|----------|------|
| **GitHub Discussions** | Q&A, design discussions | [Link](https://github.com/contextforge/contextforge/discussions) |
| **GitHub Issues** | Bug reports, feature requests | [Link](https://github.com/contextforge/contextforge/issues) |
| **Discord** | Community chat, real-time | [Link](https://discord.gg/contextforge) |
| **Email** | Private issues, conduct | conduct@contextforge.dev |
| **X/Twitter** | Announcements | [@contextforge](https://twitter.com/contextforge) |

### Response Times

We aim for:
- **GitHub Discussions/Issues**: 24-48 hours
- **Discord**: Real-time (during business hours)
- **Email**: 48 hours for sensitive issues

---

## Recognition

### Contributors Hall of Fame

We celebrate all contributions! Contributors are recognized in:
- README.md
- [Contributors Page](https://github.com/contextforge/contextforge/graphs/contributors)
- Monthly community newsletter

### Levels of Contribution

| Level | Criteria | Recognition |
|-------|----------|-------------|
| 🌟 Core | 50+ commits, active maintenance | Maintainer badge |
| 💎 Major | 10+ merged PRs | Contributor badge |
| 🚀 Active | 3+ merged PRs | Listed in README |
| 🎯 Contributor | 1+ merged PR | Added to contributors |

### Acknowledgments

In every release, we:
- Thank all contributors
- Highlight major contributions
- Share success stories

---

## Governance

### Decision Making

**Small decisions** (bugs, docs):
- Made by maintainers + community feedback
- ~2-3 day discussion period

**Medium decisions** (features, architecture):
- RFC (Request for Comments) posted to Discussions
- 1-week community input period
- Maintainers decide with community input

**Large decisions** (direction, breaking changes):
- Public RFC
- 2-week discussion
- Consensus building with maintainers

### Maintainers

Current maintainers (alphabetical):
- Your Name (Core maintainer)
- Contributor Name (Maintainer)

[See full list](GOVERNANCE.md)

---

## Frequently Asked Questions

### How do I suggest a feature?

1. Search existing [GitHub Issues](https://github.com/contextforge/contextforge/issues)
2. If not found, create new issue with "enhancement" label
3. Join [GitHub Discussions](https://github.com/contextforge/contextforge/discussions) to discuss
4. Maintainers will evaluate and prioritize

### Can I be a maintainer?

Yes! Active contributors can become maintainers. Criteria:
- 10+ merged PRs over 3+ months
- Demonstrated expertise
- Agreement with code of conduct
- Time commitment to project

Contact: [maintainers@contextforge.dev](mailto:maintainers@contextforge.dev)

### How do you decide what to build?

We prioritize based on:
1. Community need (discussions, issues)
2. Strategic alignment with vision
3. Implementation complexity
4. Maintainability long-term

See [Roadmap](ROADMAP.md) for current priorities.

### How can I stay updated?

- ⭐ Star the repository
- 👀 Watch for releases
- 📰 Subscribe to [announcements](https://github.com/contextforge/contextforge/releases)
- 🐦 Follow [@contextforge](https://twitter.com/contextforge)

### What's your release schedule?

We follow semantic versioning:
- **Patch** (0.1.x): ~weekly (bug fixes)
- **Minor** (0.x.0): ~monthly (features)
- **Major** (x.0.0): ~quarterly (breaking changes)

---

## Support & Resources

### Learning Resources

- 📖 [Official Docs](https://contextforge.dev/docs)
- 📚 [Getting Started Guide](GETTING_STARTED.md)
- 🎓 [Architecture Deep Dive](ARCHITECTURE.md)
- 💡 [Examples](EXAMPLES.md)

### Community Projects

- [ContextForge Examples](https://github.com/contextforge/contextforge-examples)
- [Community Recipes](https://github.com/contextforge/contextforge-recipes)
- [Integrations](https://github.com/topics/contextforge)

### External Help

- Stack Overflow: Tag [#contextforge](https://stackoverflow.com/questions/tagged/contextforge)
- Discussions: [GitHub Discussions](https://github.com/contextforge/contextforge/discussions)

---

## Code of Conduct - Enforcement

If you witness or experience violations:

1. **Report** to [conduct@contextforge.dev](mailto:conduct@contextforge.dev)
2. **Include** details and context
3. **Trust** that we'll handle it confidentially
4. **Know** that retaliation is not tolerated

**All reports are taken seriously and investigated promptly.**

---

## Thank You! 🙏

Every contribution matters. Thank you for being part of the ContextForge community!

Together, we're making AI context engineering better for everyone.

---

**Last Updated**: May 2026 | **Version**: 1.0.0
