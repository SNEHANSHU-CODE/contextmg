# Getting Started with ContextForge

This guide will get you up and running with ContextForge in 5 minutes. For more detailed information, see the [full documentation](index.md).

## Prerequisites

- **Python 3.10** or higher
- **pip** (Python package manager)
- **Virtual environment** (recommended: venv, conda, or poetry)

## Installation

### Step 1: Create Virtual Environment

```bash
# Using venv (recommended)
python -m venv .venv

# Activate environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\Activate.ps1
```

### Step 2: Install ContextForge

```bash
# Install latest version
pip install contextforge

# Or install from source with dev tools
git clone https://github.com/contextforge/contextforge.git
cd contextforge
pip install -e ".[dev]"
```

### Step 3: Verify Installation

```python
from contextforge.engine import AutomatedContextEngine
from contextforge.base import StaticContextComponent, AdaptiveContextPool

# Create an engine
engine = AutomatedContextEngine(max_tokens=2000)
print(f"✓ ContextForge {engine.__class__.__name__} initialized!")
```

Expected output:
```
✓ ContextForge AutomatedContextEngine initialized!
```

---

## Your First ContextForge Application

### Basic Example: Simple Query Processing

```python
from contextforge.engine import AutomatedContextEngine
from langchain_core.documents import Document

# 1. Initialize the engine
engine = AutomatedContextEngine(
    max_tokens=1000,
    recent_window_size=5
)

# 2. Prepare your data
payload = {
    "query": "How do I deploy to production?",
    "chat_history": [
        {"role": "user", "content": "What is deployment?"},
        {"role": "assistant", "content": "Deployment is the process of..."},
    ],
    "vector_docs": [
        Document(
            page_content="Production deployment involves multiple stages...",
            metadata={"id": "doc1", "score": 0.95}
        )
    ],
    "bm25_docs": []
}

# 3. Compile the context
result = engine.invoke(payload)

# 4. Use the compiled prompt
compiled_prompt = result.to_string()
print(compiled_prompt)

# 5. Send to your LLM
# response = llm.invoke(compiled_prompt)
```

### Key Concepts Explained

| Concept | Purpose |
|---------|---------|
| **max_tokens** | Maximum total tokens for compiled context |
| **recent_window_size** | How many recent messages to keep before archiving |
| **vector_docs** | Dense search results (from embeddings) |
| **bm25_docs** | Sparse search results (from keyword index) |

---

## Understanding the Context Engine

### What ContextForge Does

```
Your Input Data (Query + History + Documents)
           ↓
┌─────────────────────────────────────────┐
│  STAGE 1: Memory Partitioning           │
│  - Split conversation history           │
│  - Archive old messages                 │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  STAGE 2: Hybrid Document Fusion        │
│  - Merge vector + BM25 results          │
│  - Remove duplicates                    │
│  - Normalize importance scores          │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  STAGE 3: Lost-in-Middle Mitigation     │
│  - Reorder documents intelligently      │
│  - Place high-importance at boundaries  │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  STAGE 4: Token Budget Allocation       │
│  - Allocate tokens by priority          │
│  - Compress if needed                   │
│  - Guarantee system component space     │
└─────────────────────────────────────────┘
           ↓
Compiled LangChain PromptValue (Ready for LLM)
```

---

## Common Patterns

### Pattern 1: Basic RAG Pipeline

```python
from contextforge.engine import AutomatedContextEngine
from langchain.vectorstores import FAISS
from langchain.retrievers import BM25Retriever

# Setup retrievers
vector_store = FAISS.from_documents(docs, embeddings)
bm25_retriever = BM25Retriever.from_documents(docs)

engine = AutomatedContextEngine(max_tokens=4000)

def process_query(user_query, chat_history):
    # Retrieve documents
    vector_docs = vector_store.similarity_search(user_query, k=5)
    bm25_docs = bm25_retriever.get_relevant_documents(user_query)
    
    # Compile context
    payload = {
        "query": user_query,
        "chat_history": chat_history,
        "vector_docs": vector_docs,
        "bm25_docs": bm25_docs
    }
    
    prompt = engine.invoke(payload)
    
    # Send to LLM
    return llm.invoke(prompt.to_string())

# Use it
result = process_query("What is RAG?", [])
print(result)
```

### Pattern 2: Using with LangChain LCEL

```python
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Create LCEL chain
chain = (
    RunnableSequence(lambda x: {
        "query": x["query"],
        "chat_history": x.get("chat_history", []),
        "vector_docs": retrieve_vectors(x["query"]),
        "bm25_docs": retrieve_bm25(x["query"])
    })
    | engine
    | ChatOpenAI(model="gpt-4o")
    | StrOutputParser()
)

# Execute
result = chain.invoke({
    "query": "Your question here",
    "chat_history": []
})
```

### Pattern 3: Custom Component Priority

```python
from contextforge.base import StaticContextComponent

# Create components with different priorities
system_comp = StaticContextComponent(
    name="system_instructions",
    template="You are a helpful assistant.\n\nContext:\n{fused_contexts}",
    priority=0  # Highest priority - always allocates first
)

# System component content is guaranteed tokens
# Other components (elastic pools) get remaining budget
```

---

## Configuration Options

### AutomatedContextEngine Parameters

```python
engine = AutomatedContextEngine(
    max_tokens=4000,              # Total token budget (default: 4000)
    recent_window_size=10,         # Recent messages to preserve (default: 10)
    encoder_name="cl100k_base"     # Tiktoken encoding (default: "cl100k_base")
)
```

### Tuning for Your Use Case

| Use Case | max_tokens | recent_window_size |
|----------|------------|-------------------|
| Customer Support | 2000 | 5 |
| Research Assistant | 4000 | 10 |
| Code Copilot | 6000 | 15 |
| Lightweight Chat | 1000 | 3 |

---

## Troubleshooting

### Issue: "ImportError: No module named 'contextforge'"

**Solution**: Ensure ContextForge is installed
```bash
pip install contextforge
# Or verify current installation
pip list | grep contextforge
```

### Issue: "Token limit exceeded"

**Solution**: Reduce `max_tokens` or `recent_window_size`
```python
# Option 1: Reduce token budget
engine = AutomatedContextEngine(max_tokens=2000)

# Option 2: Keep fewer recent messages
engine = AutomatedContextEngine(recent_window_size=3)
```

### Issue: "No retrieved documents showing in output"

**Solution**: Verify document format and scores
```python
# Documents must have metadata with 'score' field
doc = Document(
    page_content="Your content",
    metadata={"id": "doc1", "score": 0.95}  # score is required
)

# Verify non-empty documents
assert len(vector_docs) > 0, "No vector documents retrieved"
```

### Issue: "Inconsistent results between runs"

**Solution**: ContextForge is deterministic. If results vary:
- Check if input data (documents, query) is changing
- Verify tiktoken version consistency: `pip list | grep tiktoken`
- See [Determinism Guide](ARCHITECTURE.md#determinism) for details

---

## Next Steps

### Learn More
- 📖 Read the [Architecture Guide](ARCHITECTURE.md) to understand internals
- 🔧 Explore the [API Reference](API_REFERENCE.md) for all available classes
- 💡 Check [Examples](EXAMPLES.md) for advanced patterns

### Get Help
- 💬 Ask questions on [GitHub Discussions](https://github.com/contextforge/contextforge/discussions)
- 🐛 Report bugs on [GitHub Issues](https://github.com/contextforge/contextforge/issues)
- 📚 Browse [FAQ](COMMUNITY.md#faq)

### Contribute
- Ready to contribute? See [Contributing Guide](../CONTRIBUTING.md)
- Want to help with docs? See [Documentation Contributing](COMMUNITY.md#documentation)
- Have ideas? Check [Roadmap](ROADMAP.md) and start a discussion

---

## Example: Complete Application

Here's a complete working example you can copy and run:

```python
"""
Complete ContextForge example: Simple Document Q&A System
"""

from contextforge.engine import AutomatedContextEngine
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

# Initialize
engine = AutomatedContextEngine(max_tokens=2000)
llm = ChatOpenAI(model="gpt-4o")

# Sample documents
documents = [
    Document(
        page_content="Python is a high-level programming language known for its simplicity.",
        metadata={"id": "doc1", "source": "wiki", "score": 0.95}
    ),
    Document(
        page_content="Django is a Python web framework for building scalable applications.",
        metadata={"id": "doc2", "source": "wiki", "score": 0.92}
    ),
]

# Simulate conversation
chat_history = [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language..."},
]

# User question
user_query = "What web frameworks use Python?"

# Compile context
payload = {
    "query": user_query,
    "chat_history": chat_history,
    "vector_docs": documents,
    "bm25_docs": []
}

prompt_value = engine.invoke(payload)
compiled_prompt = prompt_value.to_string()

# Send to LLM
print("=" * 60)
print("COMPILED PROMPT:")
print("=" * 60)
print(compiled_prompt)
print()

# Get response (uncomment to use real LLM)
# response = llm.invoke(compiled_prompt)
# print("LLM RESPONSE:")
# print(response.content)
```

**Save this as `example.py` and run:**
```bash
python example.py
```

---

## Questions?

- Check the [FAQ](COMMUNITY.md#faq)
- Browse [existing discussions](https://github.com/contextforge/contextforge/discussions)
- Open a [new discussion](https://github.com/contextforge/contextforge/discussions/new)

**Happy coding with ContextForge!** 🚀
