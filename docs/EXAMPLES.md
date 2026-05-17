# ContextForge Examples & Patterns

Real-world usage patterns and advanced techniques for ContextForge.

---

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [LangChain Integration](#langchain-integration)
3. [Advanced Patterns](#advanced-patterns)
4. [Custom Components](#custom-components)
5. [Performance Optimization](#performance-optimization)
6. [Integration Examples](#integration-examples)

---

## Basic Examples

### Example 1: Simple Q&A

**Use case**: Answer user questions about provided documents

```python
from contextforge.engine import AutomatedContextEngine
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

# Setup
engine = AutomatedContextEngine(max_tokens=2000)
llm = ChatOpenAI(model="gpt-4o")

# Documents
docs = [
    Document(
        page_content="Python is a high-level programming language.",
        metadata={"id": "python_101", "score": 0.95}
    ),
    Document(
        page_content="Django is a Python web framework.",
        metadata={"id": "django_intro", "score": 0.88}
    ),
]

# Ask question
payload = {
    "query": "What is Django?",
    "chat_history": [],
    "vector_docs": docs,
    "bm25_docs": []
}

result = engine.invoke(payload)
prompt = result.to_string()

# Get answer
response = llm.invoke(prompt)
print(response.content)
```

### Example 2: Conversational RAG

**Use case**: Maintain context across multi-turn conversations

```python
from contextforge.engine import AutomatedContextEngine
from langchain_openai import ChatOpenAI

engine = AutomatedContextEngine(
    max_tokens=3000,
    recent_window_size=5  # Keep last 5 messages
)
llm = ChatOpenAI(model="gpt-4o")

# Conversation history grows
messages = []

def chat(user_query, documents):
    """Single turn in multi-turn conversation."""
    
    # Add user message to history
    messages.append({
        "role": "user",
        "content": user_query
    })
    
    # Compile context with full history
    payload = {
        "query": user_query,
        "chat_history": messages,
        "vector_docs": documents,
        "bm25_docs": []
    }
    
    result = engine.invoke(payload)
    response = llm.invoke(result.to_string())
    
    # Add assistant response to history
    messages.append({
        "role": "assistant",
        "content": response.content
    })
    
    return response.content

# Multi-turn conversation
answer1 = chat("What is Python?", docs)
answer2 = chat("How do you install it?", docs)
answer3 = chat("What is Django?", docs)  # Context includes previous Q&A
```

### Example 3: Token Budget Enforcement

**Use case**: Strictly limit tokens regardless of input size

```python
from contextforge.engine import AutomatedContextEngine
from langchain_core.documents import Document

engine = AutomatedContextEngine(max_tokens=500)  # Strict budget

# Even with many large documents
large_docs = [
    Document(
        page_content="Very long content " * 100,  # 1000+ tokens
        metadata={"id": f"doc_{i}", "score": 0.95 - (i * 0.1)}
    )
    for i in range(10)
]

payload = {
    "query": "Query here",
    "chat_history": [],
    "vector_docs": large_docs,
    "bm25_docs": []
}

result = engine.invoke(payload)

# Result guaranteed to fit within 500 tokens
prompt = result.to_string()
print(f"Prompt length: {len(prompt.split())} words (approx 500 tokens)")
```

---

## LangChain Integration

### Pattern 1: LCEL Pipe Chain

**Use case**: Seamless integration with LangChain chains

```python
from contextforge.engine import AutomatedContextEngine
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

engine = AutomatedContextEngine(max_tokens=3000)
llm = ChatOpenAI(model="gpt-4o")

def prepare_payload(x):
    """Prepare context engine payload."""
    from langchain.vectorstores import FAISS
    
    # Simulate retrieval
    vector_docs = []  # Your vector search
    bm25_docs = []    # Your BM25 search
    
    return {
        "query": x["query"],
        "chat_history": x.get("chat_history", []),
        "vector_docs": vector_docs,
        "bm25_docs": bm25_docs
    }

# Create LCEL chain
chain = (
    RunnablePassthrough.assign(context_payload=prepare_payload)
    | RunnablePassthrough()
    | {"context": engine, "original_query": RunnablePassthrough()}
    | llm
    | StrOutputParser()
)

# Use chain
result = chain.invoke({
    "query": "Your question?",
    "chat_history": []
})
```

### Pattern 2: With Retriever Integration

**Use case**: Automatic document retrieval before context compilation

```python
from contextforge.engine import AutomatedContextEngine
from langchain.vectorstores import FAISS
from langchain.retrievers import BM25Retriever
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

engine = AutomatedContextEngine(max_tokens=4000)
llm = ChatOpenAI(model="gpt-4o")
embeddings = OpenAIEmbeddings()

# Setup retrievers
documents = [...]  # Your documents
vector_store = FAISS.from_documents(documents, embeddings)
bm25_retriever = BM25Retriever.from_documents(documents)

def retrieve_and_compile(query: str, chat_history: list):
    """Retrieve documents and compile context."""
    
    # Retrieve from both sources
    vector_docs = vector_store.similarity_search(query, k=5)
    bm25_docs = bm25_retriever.get_relevant_documents(query)
    
    # Compile context
    payload = {
        "query": query,
        "chat_history": chat_history,
        "vector_docs": vector_docs,
        "bm25_docs": bm25_docs
    }
    
    result = engine.invoke(payload)
    return result.to_string()

# Use function
messages = []
query = "What is RAG?"
compiled_prompt = retrieve_and_compile(query, messages)
response = llm.invoke(compiled_prompt)
```

### Pattern 3: With Tool Use/Agents

**Use case**: Use ContextForge within an agent loop

```python
from contextforge.engine import AutomatedContextEngine
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI

engine = AutomatedContextEngine(max_tokens=2000)
llm = ChatOpenAI(model="gpt-4o")

tools = [...]  # Your tools

def compile_context(query: str, retrieved_docs: list):
    """Tool for context compilation."""
    payload = {
        "query": query,
        "chat_history": [],
        "vector_docs": retrieved_docs,
        "bm25_docs": []
    }
    return engine.invoke(payload).to_string()

# Define as tool
from langchain.tools import tool

@tool
def prepare_context(query: str, document_ids: list):
    """Prepare compiled context from documents."""
    # Retrieve docs by ID
    docs = [get_doc(id) for id in document_ids]
    return compile_context(query, docs)

# Add to agent
tools.append(prepare_context)
agent = create_tool_calling_agent(llm, tools)
executor = AgentExecutor.from_agent_and_tools(agent, tools)
```

---

## Advanced Patterns

### Pattern 1: Dynamic Priority Adjustment

**Use case**: Adjust component priorities based on query type

```python
from contextforge.base import StaticContextComponent, AdaptiveContextPool
from contextforge.engine import AutomatedContextEngine

def create_specialized_engine(query: str) -> AutomatedContextEngine:
    """Create engine with dynamic priorities based on query."""
    
    is_code_query = any(kw in query.lower() for kw in ["code", "python", "function"])
    
    components = [
        StaticContextComponent(
            name="system",
            template="You are an expert assistant.",
            priority=0
        ),
        StaticContextComponent(
            name="query",
            template="Question: {query}",
            priority=10
        ),
    ]
    
    # Add context pools with query-dependent priorities
    if is_code_query:
        # Prioritize code examples
        components.append(AdaptiveContextPool(
            name="code_examples",
            priority=30,  # Higher priority for code
            input_key="fused_contexts"
        ))
        components.append(AdaptiveContextPool(
            name="general_context",
            priority=60,  # Lower priority
            input_key="general_docs"
        ))
    else:
        # Standard priority for non-code
        components.append(AdaptiveContextPool(
            name="context",
            priority=50,
            input_key="fused_contexts"
        ))
    
    return AutomatedContextEngine(max_tokens=3000)

# Use
query = "How to implement binary search in Python?"
engine = create_specialized_engine(query)
```

### Pattern 2: Adaptive Token Budgeting

**Use case**: Adjust token budget based on context complexity

```python
from contextforge.engine import AutomatedContextEngine

def calculate_budget(
    num_documents: int,
    history_length: int,
    query_complexity: str  # "simple", "medium", "complex"
) -> int:
    """Calculate appropriate token budget."""
    
    base_budget = 2000
    
    # Add tokens for documents
    document_tokens = num_documents * 150
    
    # Add tokens for history
    history_tokens = history_length * 50
    
    # Adjust for complexity
    complexity_multiplier = {
        "simple": 1.0,
        "medium": 1.2,
        "complex": 1.5
    }
    multiplier = complexity_multiplier.get(query_complexity, 1.0)
    
    total = int((base_budget + document_tokens + history_tokens) * multiplier)
    
    # Cap at reasonable limit
    return min(total, 8000)

# Use
engine = AutomatedContextEngine(
    max_tokens=calculate_budget(
        num_documents=5,
        history_length=10,
        query_complexity="complex"
    )
)
```

### Pattern 3: Cascading Context Pools

**Use case**: Multiple context pools with fallback strategy

```python
from contextforge.base import AdaptiveContextPool

# Create multiple pools with different priorities
primary_context = AdaptiveContextPool(
    name="primary_retrieval",
    priority=50,
    input_key="primary_docs"
)

secondary_context = AdaptiveContextPool(
    name="secondary_retrieval",
    priority=75,
    input_key="secondary_docs"
)

fallback_context = AdaptiveContextPool(
    name="fallback_retrieval",
    priority=100,
    input_key="fallback_docs"
)

# State with multiple document sources
state = {
    "primary_docs": [
        {"id": "p1", "text": "High-relevance document", "importance": 0.95},
        {"id": "p2", "text": "Medium-relevance", "importance": 0.80},
    ],
    "secondary_docs": [
        {"id": "s1", "text": "Lower relevance", "importance": 0.60},
    ],
    "fallback_docs": [
        {"id": "f1", "text": "Minimal relevance", "importance": 0.30},
    ]
}

# During compilation:
# 1. Primary pool gets first budget
# 2. Secondary pool uses remaining
# 3. Fallback fills gaps if budget remains
```

---

## Custom Components

### Example: Custom Analysis Component

**Use case**: Add domain-specific analysis to context

```python
from contextforge.base import BaseContextComponent
import tiktoken
from typing import Dict, Any, Tuple

class DomainAnalysisComponent(BaseContextComponent):
    """Analyzes documents for domain-specific insights."""
    
    def __init__(self, name: str, domain: str, priority: int = 40):
        super().__init__(name, priority)
        self.domain = domain
        self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def render(self, state: Dict[str, Any], token_budget: int) -> Tuple[str, int]:
        """Render domain analysis."""
        
        if token_budget <= 0:
            return "", 0
        
        documents = state.get("fused_contexts", [])
        analysis = self._analyze_domain(documents)
        
        # Enforce token budget
        tokens = len(self.encoder.encode(analysis))
        if tokens > token_budget:
            # Truncate with context
            char_limit = int(token_budget * 4 * 0.9)
            analysis = analysis[:char_limit] + "\n... [Analysis truncated]"
            tokens = len(self.encoder.encode(analysis))
        
        return analysis, tokens
    
    def _analyze_domain(self, documents: list) -> str:
        """Analyze documents for domain insights."""
        
        if not documents:
            return ""
        
        analysis_parts = [
            f"[Domain Analysis: {self.domain.upper()}]",
            f"Total documents: {len(documents)}",
            f"Domains detected: {self._detect_domains(documents)}",
            f"Key entities: {self._extract_entities(documents)}",
            f"Sentiment: {self._analyze_sentiment(documents)}"
        ]
        
        return "\n".join(analysis_parts)
    
    def _detect_domains(self, documents: list) -> str:
        """Detect document domains."""
        # Your domain detection logic
        return "Finance, Technology"
    
    def _extract_entities(self, documents: list) -> str:
        """Extract key entities."""
        # Your entity extraction logic
        return "Bitcoin, Ethereum, Smart Contracts"
    
    def _analyze_sentiment(self, documents: list) -> str:
        """Analyze document sentiment."""
        # Your sentiment analysis logic
        return "Neutral to Positive"

# Use custom component
custom = DomainAnalysisComponent(
    name="finance_analysis",
    domain="Finance",
    priority=40
)

state = {"fused_contexts": [...]}
analysis, tokens = custom.render(state, token_budget=300)
```

### Example: Caching Component

**Use case**: Cache frequently-accessed content

```python
from contextforge.base import BaseContextComponent
from functools import lru_cache
import hashlib

class CachingContextComponent(BaseContextComponent):
    """Component with intelligent caching."""
    
    def __init__(self, name: str, cache_size: int = 128, priority: int = 50):
        super().__init__(name, priority)
        self.cache_size = cache_size
    
    @lru_cache(maxsize=128)
    def render(self, state_hash: str, token_budget: int):
        """Cached render using state hash."""
        # Render logic here
        pass
    
    def render_uncached(self, state: Dict[str, Any], token_budget: int):
        """Wrapper that creates hash and caches."""
        
        # Create stable hash of state
        state_str = str(sorted(state.items()))
        state_hash = hashlib.md5(state_str.encode()).hexdigest()
        
        # Call cached method
        return self.render(state_hash, token_budget)
```

---

## Performance Optimization

### Optimization 1: Batch Processing

**Use case**: Process multiple queries efficiently

```python
from contextforge.engine import AutomatedContextEngine
from concurrent.futures import ThreadPoolExecutor

engine = AutomatedContextEngine(max_tokens=2000)

queries = [
    {"query": "Q1", "docs": [...], ...},
    {"query": "Q2", "docs": [...], ...},
    {"query": "Q3", "docs": [...], ...},
]

def process_query(payload):
    return engine.invoke(payload)

# Process in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_query, queries))
```

### Optimization 2: Document Pre-filtering

**Use case**: Reduce document count before compilation

```python
from contextforge.engine import AutomatedContextEngine

engine = AutomatedContextEngine(max_tokens=2000)

def filter_documents(documents: list, threshold: float = 0.7) -> list:
    """Filter low-relevance documents."""
    return [
        doc for doc in documents
        if doc.metadata.get("score", 0) >= threshold
    ]

# Use filter
all_docs = vector_search(query, k=100)  # Get many results
filtered_docs = filter_documents(all_docs)  # Keep only high-quality

payload = {
    "query": query,
    "chat_history": [],
    "vector_docs": filtered_docs,
    "bm25_docs": []
}

result = engine.invoke(payload)
```

### Optimization 3: Token Budget Tuning

**Use case**: Find optimal token budget for your use case

```python
from contextforge.engine import AutomatedContextEngine
import time

def benchmark_token_budget(max_tokens: int, payload: dict) -> dict:
    """Benchmark engine with specific token budget."""
    
    engine = AutomatedContextEngine(max_tokens=max_tokens)
    
    start = time.time()
    result = engine.invoke(payload)
    elapsed = time.time() - start
    
    return {
        "budget": max_tokens,
        "time_ms": elapsed * 1000,
        "output_length": len(result.to_string()),
    }

# Test different budgets
for budget in [500, 1000, 2000, 4000, 8000]:
    stats = benchmark_token_budget(budget, payload)
    print(f"Budget: {stats['budget']}, Time: {stats['time_ms']:.2f}ms")
```

---

## Integration Examples

### Integration: With Pinecone Vector DB

```python
from pinecone import Pinecone
from contextforge.engine import AutomatedContextEngine
from langchain_openai import ChatOpenAI

pc = Pinecone(api_key="...")
index = pc.Index("documents")

engine = AutomatedContextEngine(max_tokens=3000)
llm = ChatOpenAI()

def query_with_pinecone(query: str):
    # Vector search in Pinecone
    results = index.query(
        vector=[...],  # Query embedding
        top_k=10,
        include_metadata=True
    )
    
    # Convert to Documents
    vector_docs = [
        Document(
            page_content=match["metadata"]["text"],
            metadata={"id": match["id"], "score": match["score"]}
        )
        for match in results["matches"]
    ]
    
    # Compile context
    payload = {
        "query": query,
        "chat_history": [],
        "vector_docs": vector_docs,
        "bm25_docs": []
    }
    
    result = engine.invoke(payload)
    return llm.invoke(result.to_string())
```

### Integration: With Elasticsearch BM25

```python
from elasticsearch import Elasticsearch
from contextforge.engine import AutomatedContextEngine
from langchain_core.documents import Document

es = Elasticsearch(["localhost:9200"])
engine = AutomatedContextEngine(max_tokens=3000)

def query_with_elasticsearch(query: str):
    # BM25 search
    response = es.search(
        index="documents",
        body={
            "query": {"multi_match": {"query": query}},
            "size": 10
        }
    )
    
    # Convert to Documents
    bm25_docs = [
        Document(
            page_content=hit["_source"]["content"],
            metadata={
                "id": hit["_id"],
                "score": hit["_score"] / 100  # Normalize to 0-1
            }
        )
        for hit in response["hits"]["hits"]
    ]
    
    # Compile
    payload = {
        "query": query,
        "chat_history": [],
        "vector_docs": [],
        "bm25_docs": bm25_docs
    }
    
    return engine.invoke(payload).to_string()
```

---

## See Also

- [Getting Started](GETTING_STARTED.md)
- [API Reference](API_REFERENCE.md)
- [Architecture](ARCHITECTURE.md)
- [Community](COMMUNITY.md)

---

**Examples Version**: 1.0.0 | **Last Updated**: May 2026
