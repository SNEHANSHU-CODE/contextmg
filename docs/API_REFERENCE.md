# ContextForge API Reference

Complete API documentation for ContextForge components and classes.

---

## Core Classes

### AutomatedContextEngine

Main orchestration engine for context compilation.

```python
from contextforge.engine import AutomatedContextEngine
```

#### Constructor

```python
AutomatedContextEngine(
    max_tokens: int = 4000,
    recent_window_size: int = 10,
    encoder_name: str = "cl100k_base"
) -> AutomatedContextEngine
```

**Parameters:**
- `max_tokens` (int): Total token budget for compiled context. Default: 4000
- `recent_window_size` (int): Number of recent messages to preserve in active window. Default: 10
- `encoder_name` (str): Tiktoken encoder name for token counting. Default: "cl100k_base"

**Returns:** Configured AutomatedContextEngine instance

**Raises:**
- `ValueError`: If max_tokens or recent_window_size are negative

**Example:**
```python
engine = AutomatedContextEngine(
    max_tokens=2000,
    recent_window_size=5,
    encoder_name="cl100k_base"
)
```

#### Methods

##### `invoke(input, config=None)`

Compiles context and returns LangChain PromptValue.

```python
def invoke(
    self,
    input: Dict[str, Any],
    config: Optional[RunnableConfig] = None
) -> StringPromptValue
```

**Parameters:**
- `input` (Dict[str, Any]): Payload dictionary containing:
  - `query` (str): Current user question
  - `chat_history` (List[Dict]): Message history with 'role' and 'content' keys
  - `vector_docs` (List[Document]): Vector search results
  - `bm25_docs` (List[Document]): BM25 search results
- `config` (Optional[RunnableConfig]): LangChain runtime config

**Returns:** StringPromptValue containing compiled prompt

**Raises:**
- `ValueError`: If state dictionary is malformed
- `TypeError`: If input types are incorrect

**Example:**
```python
payload = {
    "query": "How to deploy?",
    "chat_history": [
        {"role": "user", "content": "What is deployment?"},
        {"role": "assistant", "content": "Deployment is..."}
    ],
    "vector_docs": [
        Document(page_content="...", metadata={"id": "d1", "score": 0.95})
    ],
    "bm25_docs": []
}

result = engine.invoke(payload)
prompt_text = result.to_string()
```

##### `is_lc_serializable()`

Check if engine is serializable for LangChain.

```python
@classmethod
def is_lc_serializable(cls) -> bool
```

**Returns:** True (engine is LangChain serializable)

**Example:**
```python
if AutomatedContextEngine.is_lc_serializable():
    print("Can serialize to JSON for persistence")
```

#### Internal Methods

##### `_auto_summarize_long_memory(history)`

Partitions chat history and aggregates older messages.

```python
def _auto_summarize_long_memory(
    self,
    history: List[Dict[str, str]]
) -> str
```

**Parameters:**
- `history` (List[Dict]): Chat history with 'role' and 'content'

**Returns:** String representation of archived messages (outside recent window)

**Internal Use:** Called automatically during `invoke()`

##### `_auto_hybrid_fuse(vector_docs, bm25_docs)`

Merges and deduplicates documents from vector and BM25 sources.

```python
def _auto_hybrid_fuse(
    self,
    vector_docs: List[Document],
    bm25_docs: List[Document]
) -> List[Dict[str, Any]]
```

**Parameters:**
- `vector_docs` (List[Document]): Vector search results
- `bm25_docs` (List[Document]): BM25 search results

**Returns:** List of deduplicated documents with structure:
```python
[
    {
        "id": str,              # Document identifier
        "text": str,            # Page content
        "importance": float     # Normalized score (0.0-1.0)
    },
    ...
]
```

**Internal Use:** Called automatically during `invoke()`

---

### BaseContextComponent

Abstract base class for all context components.

```python
from contextforge.base import BaseContextComponent
```

#### Abstract Methods

##### `render(state, token_budget)`

Renders component with token budget enforcement.

```python
@abstractmethod
def render(
    self,
    state: Dict[str, Any],
    token_budget: int
) -> Tuple[str, int]
```

**Parameters:**
- `state` (Dict[str, Any]): Runtime state dictionary with variables
- `token_budget` (int): Maximum tokens allowed for this component

**Returns:** Tuple of (rendered_text, tokens_consumed)

**Raises:**
- `ValueError`: If state validation fails
- `TypeError`: If parameters are wrong type

**Example:**
```python
class MyComponent(BaseContextComponent):
    def render(self, state, token_budget):
        if token_budget <= 0:
            return "", 0
        
        text = f"Content: {state.get('query', '')}"
        tokens = len(encode(text))
        
        return text, tokens
```

---

### StaticContextComponent

Fixed text component with variable substitution.

```python
from contextforge.base import StaticContextComponent
```

#### Constructor

```python
StaticContextComponent(
    name: str,
    template: str,
    priority: int = 0
) -> StaticContextComponent
```

**Parameters:**
- `name` (str): Unique component identifier
- `template` (str): Python format string with {placeholders}
- `priority` (int): Execution priority (lower = first). Default: 0

**Returns:** Configured StaticContextComponent

**Example:**
```python
system = StaticContextComponent(
    name="system_instructions",
    template="You are a helpful assistant.\n\nContext:\n{context}",
    priority=0
)
```

#### Methods

##### `render(state, token_budget)`

Renders template with state substitution and token truncation.

```python
def render(
    self,
    state: Dict[str, Any],
    token_budget: int
) -> Tuple[str, int]
```

**Parameters:**
- `state` (Dict[str, Any]): Variables for template substitution
- `token_budget` (int): Maximum tokens (<=0 returns empty string)

**Returns:** Tuple of (rendered_template, tokens_consumed)

**Behavior:**
- Substitutes template variables from state dictionary
- Enforces token budget with character truncation fallback
- Raises ValueError if required variables missing from state

**Example:**
```python
state = {"context": "Important data", "query": "What is X?"}
text, tokens = system.render(state, token_budget=500)
# text = "You are a helpful assistant.\n\nContext:\nImportant data\nWhat is X?"
# tokens = 23
```

---

### AdaptiveContextPool

Dynamic document context pool with intelligent allocation.

```python
from contextforge.base import AdaptiveContextPool
```

#### Constructor

```python
AdaptiveContextPool(
    name: str,
    priority: int = 50,
    input_key: str = "fused_contexts"
) -> AdaptiveContextPool
```

**Parameters:**
- `name` (str): Unique component identifier
- `priority` (int): Execution priority. Default: 50 (elastic)
- `input_key` (str): State key containing document list. Default: "fused_contexts"

**Returns:** Configured AdaptiveContextPool

**Example:**
```python
pool = AdaptiveContextPool(
    name="knowledge_base",
    priority=50,
    input_key="fused_contexts"
)
```

#### Methods

##### `render(state, token_budget)`

Renders document pool with Lost-in-Middle mitigation.

```python
def render(
    self,
    state: Dict[str, Any],
    token_budget: int
) -> Tuple[str, int]
```

**Parameters:**
- `state` (Dict[str, Any]): Must contain key (input_key) with document list:
  ```python
  state[input_key] = [
      {"id": "doc1", "text": "Content", "importance": 0.95},
      {"id": "doc2", "text": "Content", "importance": 0.70},
  ]
  ```
- `token_budget` (int): Maximum tokens for all documents

**Returns:** Tuple of (rendered_xml, tokens_consumed)

**Behavior:**
- Sorts documents by importance (descending)
- Uses alternating placement: high importance at start/end
- Applies word-level compression if document exceeds budget
- Stops adding documents when budget exhausted
- Returns XML-formatted context blocks

**Document Format:**
```python
{
    "id": str,              # Unique document identifier
    "text": str,            # Document content (required)
    "importance": float     # Relevance score 0.0-1.0 (required)
}
```

**Example:**
```python
state = {
    "fused_contexts": [
        {"id": "doc1", "text": "Python is...", "importance": 0.95},
        {"id": "doc2", "text": "Django is...", "importance": 0.70},
    ]
}

xml, tokens = pool.render(state, token_budget=500)
# xml = """<context_pool>
# <context_block id='doc1'>
# Python is...
# </context_block>
# ...
# </context_pool>"""
```

---

## Type Definitions

### Document (from langchain_core)

LangChain document object used for retrieval results.

```python
from langchain_core.documents import Document

document = Document(
    page_content: str,      # Document text content
    metadata: Dict[str, Any] # Document metadata
)
```

**Required Metadata:**
- `id` (str): Unique document identifier
- `score` or `relevance` (float): Importance score (0.0-1.0)

**Example:**
```python
doc = Document(
    page_content="Python is a high-level programming language.",
    metadata={
        "id": "doc_1",
        "source": "wikipedia",
        "score": 0.95,
        "date": "2024-01-15"
    }
)
```

### StringPromptValue (from langchain_core)

LangChain's native prompt value wrapper.

```python
from langchain_core.prompt_values import StringPromptValue

prompt = StringPromptValue(text="Your compiled prompt text")
```

**Methods:**
- `to_string()`: Get prompt as string
- `to_messages()`: Convert to message format

**Example:**
```python
result = engine.invoke(payload)  # Returns StringPromptValue
prompt_text = result.to_string()
```

### RunnableConfig (from langchain_core)

LangChain runtime configuration.

```python
from langchain_core.runnables import RunnableConfig

config = RunnableConfig(
    tags=["tag1", "tag2"],
    metadata={"key": "value"},
    callbacks=[]
)
```

---

## Constants

### Default Token Encodings

```python
# CL100K encoding (default for GPT-4, GPT-3.5)
encoder_name = "cl100k_base"

# Alternative encodings
"cl100k_base"  # GPT-4, GPT-3.5 (default)
"p50k_base"    # Text-davinci-002, text-davinci-003
"p50k_edit"    # Text-davinci-edit models
"r50k_base"    # Codex, text-davinci-001, text-davinci-002
```

### Priority Tier Recommendations

```python
PRIORITY_SYSTEM = 0           # System instructions
PRIORITY_CRITICAL = 5         # Critical context
PRIORITY_QUERY = 10           # User query
PRIORITY_PRIMARY = 50         # Main retrieval
PRIORITY_SECONDARY = 75       # Secondary retrieval
PRIORITY_OPTIONAL = 100       # Optional data
```

---

## Common Patterns

### Pattern: Creating a Simple Component

```python
from contextforge.base import BaseContextComponent
import tiktoken

class CustomComponent(BaseContextComponent):
    def __init__(self, name: str, priority: int = 75):
        super().__init__(name, priority)
        self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def render(self, state, token_budget):
        if token_budget <= 0:
            return "", 0
        
        # Your rendering logic
        text = "Your custom content"
        tokens = len(self.encoder.encode(text))
        
        # Enforce budget
        if tokens > token_budget:
            text = text[:token_budget * 4] + "..."
            tokens = len(self.encoder.encode(text))
        
        return text, tokens
```

### Pattern: Token Counting

```python
import tiktoken

encoder = tiktoken.get_encoding("cl100k_base")
text = "Hello world"
tokens = len(encoder.encode(text))
print(f"'{text}' = {tokens} tokens")
```

### Pattern: Handling Missing State Variables

```python
def render(self, state, token_budget):
    query = state.get("query", "")  # Safe access with default
    
    if not query:
        return "No query provided", 0
    
    # Continue processing
    ...
```

---

## Error Handling

### Common Exceptions

| Exception | Cause | Solution |
|-----------|-------|----------|
| `ValueError` | Missing template variable | Provide all {variables} in state |
| `ValueError` | Invalid component structure | Verify document format: `{'id', 'text', 'importance'}` |
| `TypeError` | Wrong parameter type | Check parameter types in method signature |
| `ImportError` | Missing dependency | `pip install langchain-core tiktoken` |

### Example Error Handling

```python
from contextforge.engine import AutomatedContextEngine
from contextforge.base import StaticContextComponent

try:
    component = StaticContextComponent(
        name="test",
        template="Hello {name}",
        priority=0
    )
    
    # Missing 'name' variable
    text, tokens = component.render({}, 500)
    
except ValueError as e:
    print(f"Template variable error: {e}")
```

---

## Performance Notes

- Token counting is O(m) where m = text length
- Component sorting is O(n log n) where n = number of components
- Document fusion is O(v + b) where v,b = doc counts
- See [Architecture Guide](ARCHITECTURE.md#performance) for benchmarks

---

## See Also

- [Getting Started](GETTING_STARTED.md) - Quick start
- [Architecture Guide](ARCHITECTURE.md) - Design details
- [Examples](EXAMPLES.md) - Usage patterns
- [Community](COMMUNITY.md) - Support and contributions

---

**API Version**: 0.1.0 | **Last Updated**: May 2026
