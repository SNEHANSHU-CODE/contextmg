# ContextForge 🛠️

ContextForge is a declarative, fine-grained automated context engineering framework designed for LLM production applications. It brings React's component-driven lifecycle architecture and deterministic state rendering natively into the LangChain ecosystem.

## 🌟 Why ContextForge?

In production, context engineering fails when it operates as an unmonitored string-concatenation black box. Static prompts lead to context overflow, "Lost-in-the-Middle" retrieval drops, and runaway token expenses.

ContextForge solves this by shifting prompt management from **static string building** to a dynamic, token-aware **Context Directed Acyclic Graph (DAG)**.

[ 1. DEVELOPER DECLARATIVE INTENT ]- LCEL Pipe Operators (Runnable)- High-Level User State Request│▼[ 2. GRAPH COMPILATION ENGINE ]- Priority-Based Topological Sorter│▼[ 3. BUDGET ALLOCATION RUNTIME ]- Token-Aware Budget Injector- Truncation & Middle-Out Layout Pipelines


### 🛠️ High-Level Automated Architecture

Developers specify high-level declarative parameters. The underlying engine automatically handles the underlying context logic:
1. **Automated Sliding Window & Summary Fallback**: Isolates the most recent conversations while continuously summarizing previous messages in the background to prevent immediate context degradation.
2. **Hybrid Retrieval Fusion**: Merges Vector DB collections and BM25 index hits seamlessly via dynamic rank logic.
3. **Lost-in-the-Middle Layout Pipelines**: Alternates the position of retrieved documents to place critical contexts at the margins, where LLM attention peaks.
4. **Linguistic Prompt Compression**: Automatically strips low-entropy tokens and fillers when system token budgets tighten.

---

## 🚀 Declarative Usage (LCEL Native)

ContextForge inherits directly from LangChain's `Runnable` wrapper primitives, integrating out of the box with the pipe (`|`) operator:

```python
from contextforge.engine import AutomatedContextEngine
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# 1. Declare intent: request automated summary fallbacks & hybrid optimization
context_automator = AutomatedContextEngine(
    max_tokens=4000,
    recent_window_size=10
)

# 2. Pipe context directly into standard LangChain flows
llm = ChatOpenAI(model="gpt-4o")
automated_chain = context_automator | llm | StrOutputParser()

# 3. Stream runtime data directly from application layers
response = automated_chain.invoke({
    "query": "Fix the cluster connection timeout issue.",
    "chat_history": past_chat_array,
    "vector_docs": vector_db_matches,
    "bm25_docs": keyword_index_matches
})
```

