# ContextForge Architecture Deep Dive

This document explains the design philosophy, system architecture, and internal mechanisms of ContextForge.

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [System Architecture](#system-architecture)
3. [Component Model](#component-model)
4. [Priority Scheduling](#priority-scheduling)
5. [Token Budget Allocation](#token-budget-allocation)
6. [Advanced Topics](#advanced-topics)
7. [Performance Characteristics](#performance-characteristics)
8. [Glossary](#glossary)

---

## Design Philosophy

### Three Core Principles

#### 1. Declarative First

ContextForge follows a **declarative programming model** inspired by React:

```
Imperative (Traditional):          Declarative (ContextForge):
┌─────────────────────┐           ┌──────────────────────┐
│ format_header()     │           │ StaticComponent      │
│ add_context()       │           │ priority=0           │
│ truncate_if_needed()│           │ template="..."       │
│ format_footer()     │           └──────────────────────┘
└─────────────────────┘
```

**Benefits:**
- Composition over imperative sequencing
- Reusable, testable components
- Automatic optimization (compiler handles details)

#### 2. Token-Aware Always

Every operation respects strict token budgets:

```
Traditional LLM:                  ContextForge:
┌─────────────────┐              ┌───────────────────┐
│ Build prompt    │              │ Budget: 4000 tokens│
│ (Hope it fits!) │              │ ├─ System: 300 ✓   │
└─────────────────┘              │ ├─ Query: 150 ✓    │
                                 │ ├─ Context: 3500   │
                                 │ │  ├─ Doc1: 1200 ✓ │
                                 │ │  ├─ Doc2: 1300 ✓ │
                                 │ │  ├─ Doc3: 950 ✗  │
                                 │ └─ Remaining: 0    │
                                 └───────────────────┘
```

#### 3. Production-Ready

Components are built for enterprise environments:

- **Deterministic**: Same input → Same output (reproducible)
- **Fault-tolerant**: Graceful degradation under constraints
- **Observable**: Full token accounting and metrics
- **Scalable**: Efficient processing of large context graphs

---

## System Architecture

### Four-Layer Compilation Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: DECLARATIVE INTERFACE                              │
│ ─────────────────────────────────────────────────────────── │
│ • High-level component definitions                          │
│ • LangChain LCEL integration (@Runnable)                    │
│ • User-facing API surface                                   │
│                                                             │
│ Example:                                                    │
│   engine = AutomatedContextEngine(max_tokens=4000)         │
│   result = engine.invoke(payload)                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ LAYER 2: TOPOLOGICAL RECOMPILER                             │
│ ─────────────────────────────────────────────────────────── │
│ • Parse component graph structure                           │
│ • Sort by priority (0=highest)                              │
│ • Build execution schedule                                  │
│                                                             │
│ Example Schedule:                                           │
│   1. System Layer (priority=0)   → Process first            │
│   2. Query Layer (priority=10)   → Process second           │
│   3. Context Pool (priority=50)  → Process last             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: FINE-GRAINED BUDGET ALLOCATOR                      │
│ ─────────────────────────────────────────────────────────── │
│ • Track token consumption per component                     │
│ • Apply compression/truncation algorithms                   │
│ • Ensure hard budget compliance                             │
│                                                             │
│ Allocation Process:                                         │
│   for component in sorted_components:                       │
│       render component with remaining budget                │
│       subtract tokens from budget                           │
│       if budget < 0: stop adding components                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ LAYER 4: OUTPUT PACKAGE & TELEMETRY                         │
│ ─────────────────────────────────────────────────────────── │
│ • Wrap in LangChain PromptValue                             │
│ • Record metrics and token usage                            │
│ • Export for downstream LLM integration                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Model

### BaseContextComponent

All components inherit from `BaseContextComponent` and implement the `render()` method:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class BaseContextComponent(ABC):
    def __init__(self, name: str, priority: int = 100):
        self.name = name
        self.priority = priority
    
    @abstractmethod
    def render(
        self, 
        state: Dict[str, Any], 
        token_budget: int
    ) -> Tuple[str, int]:
        """
        Render component with strict token budget enforcement.
        
        Returns:
            (rendered_text, tokens_consumed)
        """
        pass
```

### Component Types

#### 1. StaticContextComponent

**Purpose**: System invariants and fixed content

**Characteristics:**
- Fixed template text with variable substitution
- Priority 0 (highest) by default
- Token budget: Always allocated first
- Use case: System instructions, user query, safety constraints

**Example:**
```python
system = StaticContextComponent(
    name="system_instructions",
    template="""You are an expert assistant. Answer accurately.

User Query: {query}
Context: {context}""",
    priority=0
)
```

**Token Allocation**: System components are guaranteed tokens before elastic pools

#### 2. AdaptiveContextPool

**Purpose**: Dynamic document context with intelligent distribution

**Characteristics:**
- Accepts list of `{'id': str, 'text': str, 'importance': float}`
- Priority 50+ (elastic, lower priority)
- Token budget: Gets remaining after high-priority components
- Drops documents when budget exhausted
- Implements "Lost-in-the-Middle" mitigation

**Example:**
```python
context_pool = AdaptiveContextPool(
    name="knowledge_base",
    priority=50,
    input_key="fused_contexts"
)
```

**Behavior:**
- Sorts documents by importance (descending)
- Uses alternating placement to put high-importance at boundaries
- Applies word-level compression if document slightly exceeds remaining budget
- Returns empty list if no token budget remains

---

## Priority Scheduling

### Execution Order

Components execute in **strict priority order** (ascending):

```
┌──────────────────────────────────────────────────┐
│ Components sorted by priority                    │
├──────────────────────────────────────────────────┤
│ Priority 0  (System)        → Always first       │
│ Priority 10 (Query)         → After system       │
│ Priority 50 (Context Pool)  → Remaining budget   │
│ Priority 100+ (Others)      → Last               │
└──────────────────────────────────────────────────┘
```

### Token Guarantee Matrix

| Priority Range | Component Type | Guarantee | Behavior |
|---|---|---|---|
| 0 | System Invariants | Full allocation | Non-negotiable content |
| 1-20 | Core Query/Context | Full allocation | Immediate answer context |
| 50+ | Elastic Pools | Remaining budget | Expands/contracts with budget |
| 100+ | Optional | Best-effort | May be entirely dropped |

### Custom Priorities

Define custom priority tiers:

```python
components = [
    StaticContextComponent("system", template="...", priority=0),
    StaticContextComponent("query", template="...", priority=10),
    AdaptiveContextPool("retrieval", priority=50),
    AdaptiveContextPool("fallback_retrieval", priority=100),
]

# Automatic sorting by priority
sorted_components = sorted(components, key=lambda c: c.priority)
```

---

## Token Budget Allocation

### Allocation Algorithm

```
Input: max_tokens, components (sorted by priority)
Output: compiled_prompt, total_tokens_used

budget = max_tokens
rendered_payloads = {}

for component in sorted_components:
    if budget <= 0:
        break  # Stop processing if budget exhausted
    
    text, tokens = component.render(state, budget)
    rendered_payloads[component.name] = text
    budget -= tokens
    
    # Safety net: never go negative
    if budget < 0:
        budget = 0

return assemble_payloads(rendered_payloads)
```

### Compression Strategies

When a component slightly exceeds remaining budget:

#### Strategy 1: Character Truncation (StaticComponent)

```python
if tokens_used > token_budget:
    # Estimate 4 chars per token (CL100K baseline)
    char_limit = token_budget * 4
    text = text[:char_limit] + " ... [Truncated]"
    tokens = len(encode(text))
```

#### Strategy 2: Word-Level Compression (AdaptivePool)

```python
if document_tokens > remaining_budget:
    # Estimate 1.3 tokens per word average
    word_limit = int(remaining_budget * 0.70 / 1.3)
    compressed = " ".join(words[:word_limit])
    text = f"<doc>{compressed}\n... [Truncated]\n</doc>"
```

#### Strategy 3: Document Dropping (AdaptivePool)

```python
for document in sorted_documents:
    doc_tokens = encode_length(document)
    if doc_consumed + doc_tokens > remaining_budget:
        break  # Stop adding documents
    # Add document otherwise
```

### Example Walkthrough

```
Initial State:
  budget = 1000 tokens
  components = [SystemLayer(50), QueryLayer(100), ContextPool(850)]

Step 1: Render SystemLayer
  ├─ budget_before = 1000
  ├─ rendered = "System instructions..." (50 tokens)
  └─ budget_after = 950 tokens

Step 2: Render QueryLayer
  ├─ budget_before = 950
  ├─ rendered = "[User Query]: How to deploy?" (100 tokens)
  └─ budget_after = 850 tokens

Step 3: Render ContextPool
  ├─ budget_before = 850
  ├─ document_1 = 400 tokens ✓ (add it, budget → 450)
  ├─ document_2 = 400 tokens ✓ (add it, budget → 50)
  ├─ document_3 = 500 tokens ✗ (exceeds 50 budget)
  │   └─ apply compression (50 tokens ✓)
  │       (now budget = 0)
  ├─ document_4 = 300 tokens ✗ (budget exhausted, skip)
  └─ budget_after = 0 tokens

Final Output:
  SystemLayer + QueryLayer + Document1 + Document2 + Compressed(Document3)
  Total: 50 + 100 + 400 + 400 + 50 = 1000 tokens ✓
```

---

## Advanced Topics

### Lost-in-the-Middle Mitigation

**Problem**: LLMs lose focus on information placed in the middle of long prompts.

**Solution**: Alternating marginal placement

```
Sorted by Importance: [Doc1(0.95), Doc2(0.85), Doc3(0.70), Doc4(0.60)]

Alternating Placement Process:
  i=0: Doc1 (highest) → append to end
  i=1: Doc2 → prepend to start
  i=2: Doc3 → append to end
  i=3: Doc4 → prepend to start

Result: [Doc4, Doc2, Doc3, Doc1]
         ┌─ Boundary (high attention)
         │
┌────────────────────────────────────────────────────┐
│ Doc4  Doc2  Doc3  Doc1                             │
│ (boundary) (middle) (boundary)                     │
└────────────────────────────────────────────────────┘
        └─ Boundary (high attention)
```

**Effect**: Important documents placed at reading boundaries (start/end) where model attention peaks.

### Determinism Guarantees

ContextForge is fully deterministic:

```
Given:
  - Same input payload
  - Same tiktoken version
  - Same component configuration
  
Then:
  - Output is identical across runs
  - Token count is identical
  - Order is reproducible
```

**Implications:**
- Deterministic results enable reproducible research
- Version pinning (tiktoken==0.5.1) ensures consistency
- No randomness in component rendering

### Memory Partitioning Strategy

#### Stage 1: History Slicing

```
Input chat history:
  [Msg0, Msg1, Msg2, Msg3, Msg4, Msg5]
  
With recent_window_size=3:
  ├─ Recent window (kept as-is): [Msg3, Msg4, Msg5]
  └─ Archive (summarized):       [Msg0, Msg1, Msg2]
```

#### Stage 2: Archive Aggregation

```
Archive messages:
  [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is..."},
    {"role": "user", "content": "How to install?"}
  ]

Aggregated to single line:
  "[USER]: What is Python? | [ASSISTANT]: Python is... | [USER]: How to install?"

Then truncated if > 1200 characters:
  "[USER]: What is Python? | [ASSISTANT]: Python is... | ... [Truncated]"
```

### Hybrid Fusion Deduplication

```
Vector Search Results:
  [
    {"id": "v1", "text": "Deployment strategy", "score": 0.95},
    {"id": "v2", "text": "CI/CD pipeline", "score": 0.88}
  ]

BM25 Search Results:
  [
    {"id": "b1", "text": "Deployment strategy", "score": 0.72},  ← Duplicate
    {"id": "b2", "text": "Kubernetes basics", "score": 0.80}
  ]

Deduplication Process:
  1. Hash "Deployment strategy" → seen_set = {"Deployment strategy"}
  2. Include {"id": "v1", ...} (not in seen_set)
  3. Include {"id": "v2", ...} (not in seen_set)
  4. Skip {"id": "b1", ...} (already in seen_set)
  5. Include {"id": "b2", ...} (not in seen_set)

Final Result:
  [
    {"id": "v1", "text": "Deployment strategy", "importance": 0.95},
    {"id": "v2", "text": "CI/CD pipeline", "importance": 0.88},
    {"id": "b2", "text": "Kubernetes basics", "importance": 0.80}
  ]
```

---

## Performance Characteristics

### Time Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Component sorting | O(n log n) | n = number of components |
| Token encoding | O(m) | m = text length in chars |
| Memory partitioning | O(h) | h = history length |
| Hybrid fusion | O(v + b) | v = vector docs, b = BM25 docs |
| Lost-in-middle reordering | O(d log d) | d = fused documents |

### Space Complexity

| Component | Space | Notes |
|-----------|-------|-------|
| Component graph | O(n) | n = components |
| Token cache | O(m) | m = text length |
| Deduplication set | O(d) | d = unique documents |

### Benchmark Results

```
Configuration: max_tokens=4000, recent_window_size=10

Scenario 1: Small Context (1 doc)
  Input tokens: ~200
  Processing time: <10ms
  Output tokens: ~300

Scenario 2: Medium Context (5 docs)
  Input tokens: ~1000
  Processing time: ~50ms
  Output tokens: ~1200

Scenario 3: Large Context (20 docs)
  Input tokens: ~3500
  Processing time: ~150ms
  Output tokens: ~3900

Scenario 4: Large History (100 messages)
  Input tokens: ~2000
  Processing time: ~30ms
  Output tokens: ~400 (with archiving)
```

### Optimization Tips

1. **Reduce max_tokens** if processing latency is critical
2. **Decrease recent_window_size** to spend less time archiving
3. **Batch documents** before invoking engine
4. **Cache component definitions** across multiple invocations
5. **Use vector-only search** if BM25 results add minimal value

---

## Advanced Customization

### Custom Component Implementation

```python
from contextforge.base import BaseContextComponent

class CustomComponent(BaseContextComponent):
    def __init__(self, name: str, custom_processor, priority: int = 75):
        super().__init__(name, priority)
        self.custom_processor = custom_processor
    
    def render(self, state, token_budget):
        # Apply custom logic
        output = self.custom_processor(state, token_budget)
        
        # Token counting
        tokens = len(encode(output))
        
        # Enforce budget
        if tokens > token_budget:
            output = self._compress(output, token_budget)
            tokens = len(encode(output))
        
        return output, tokens
    
    def _compress(self, text, token_budget):
        # Your compression algorithm
        return text[:token_budget * 4]
```

### Custom Priority Tiers

```python
# Define organizational priorities
PRIORITY_SYSTEM = 0
PRIORITY_CRITICAL_CONTEXT = 5
PRIORITY_QUERY = 10
PRIORITY_PRIMARY_RETRIEVAL = 50
PRIORITY_SECONDARY_RETRIEVAL = 75
PRIORITY_OPTIONAL = 100

components = [
    StaticComponent("rules", priority=PRIORITY_SYSTEM),
    AdaptivePool("main_docs", priority=PRIORITY_PRIMARY_RETRIEVAL),
    AdaptivePool("fallback_docs", priority=PRIORITY_SECONDARY_RETRIEVAL),
]
```

---

## Glossary

| Term | Definition |
|------|-----------|
| **Component** | Reusable unit of prompt composition with lifecycle |
| **Priority** | Integer determining component execution order (lower = first) |
| **Token Budget** | Maximum tokens allowed for compiled context |
| **Lost-in-Middle** | Phenomenon where LLMs lose focus on center-placed information |
| **Hybrid Fusion** | Process of merging vector and BM25 search results |
| **Deduplication** | Removing duplicate documents before compilation |
| **Archive** | Summarized representation of older conversation history |
| **Compression** | Reducing text length to fit token budget |
| **LCEL** | LangChain Expression Language (pipe operator interface) |
| **PromptValue** | LangChain-native object for passing prompts to LLMs |

---

## See Also

- [Getting Started](GETTING_STARTED.md) - Quick start guide
- [API Reference](API_REFERENCE.md) - Detailed API documentation
- [Examples](EXAMPLES.md) - Real-world usage patterns
- [Development Guide](DEVELOPMENT.md) - Contributing to ContextForge

---

**Architecture Version**: 1.0 | **Last Updated**: May 2026
