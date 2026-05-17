"""
Automated context engineering compilation engine for LangChain LCEL integration.

The AutomatedContextEngine orchestrates the complete context lifecycle using React-like
component architecture with deterministic token budgeting and priority-based scheduling.
"""

from typing import Dict, Any, Optional, List
from langchain_core.runnables import RunnableSerializable, RunnableConfig
from langchain_core.prompt_values import PromptValue, StringPromptValue
from langchain_core.documents import Document
from contextmg.base import StaticContextComponent, AdaptiveContextPool
import tiktoken


class AutomatedContextEngine(RunnableSerializable[Dict[str, Any], PromptValue]):
    """
    Automated context engineering compiler engine.
    Inherits cleanly from LangChain's RunnableSerializable primitive to operate natively
    within standard LangChain Expression Language (LCEL) chain pipe flows (|).
    
    This engine orchestrates the complete context lifecycle:
    1. Memory Partitioning: Splits chat history into active window and archive summary
    2. Hybrid Fusion: Merges vector and BM25 documents with deduplication
    3. Lost-in-the-Middle Mitigation: Reorders documents using alternating marginal placement
    4. Token-Aware Allocation: Distributes budget across components by priority
    5. Output Packaging: Returns LangChain PromptValue for downstream LLM integration
    
    Attributes:
        max_tokens: Maximum total token budget for compiled context (default 4000).
        recent_window_size: Number of recent messages to keep in active window (default 10).
        encoder_name: Tiktoken encoding name (default "cl100k_base").
    """
    
    max_tokens: int = 4000
    recent_window_size: int = 10
    encoder_name: str = "cl100k_base"

    def __init__(self, max_tokens: int = 4000, recent_window_size: int = 10, encoder_name: str = "cl100k_base"):
        """
        Initialize the AutomatedContextEngine.
        
        Args:
            max_tokens: Maximum token budget for the entire compiled context.
            recent_window_size: Number of recent messages to retain in active conversation window.
            encoder_name: Name of the tiktoken encoding to use for token counting.
        """
        super().__init__(max_tokens=max_tokens, recent_window_size=recent_window_size, encoder_name=encoder_name)

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Indicate that this Runnable is serializable for LangChain integration."""
        return True

    def _auto_summarize_long_memory(self, history: List[Dict[str, str]]) -> str:
        """
        Automated Sliding Window Partitioning. Captures everything outside the immediate 
        recent chat conversation history limits and aggregates it linearly to prevent token blowouts.
        
        This method splits the conversation history into two logical segments:
        - Active Window: Most recent N messages preserved as-is for immediate context
        - Archive Summary: Older messages condensed into a single background trace block
        
        Args:
            history: List of message dictionaries with 'role' and 'content' keys.
                    Example: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        
        Returns:
            String representation of archived messages outside the active window.
            Returns "No historical conversation records archived." if history fits in window.
        """
        if not history or len(history) <= self.recent_window_size:
            return "No historical conversation records archived."
            
        # Extract the deep long-term history layers sitting past the boundary window limit
        archive_stack = history[:-self.recent_window_size]
        summary_acc = []
        
        for interaction in archive_stack:
            role = interaction.get("role", "user").upper()
            content = interaction.get("content", "").strip()
            if content:  # Skip empty messages
                summary_acc.append(f"[{role}]: {content}")
            
        raw_archive_string = " | ".join(summary_acc)
        
        # Fine-grained safeguard truncation boundary logic: cap at 1200 chars
        if len(raw_archive_string) > 1200:
            return f"{raw_archive_string[:1200]}... [Automated Context Trace Truncation Applied]"
        return raw_archive_string

    def _auto_hybrid_fuse(self, vector_docs: List[Document], bm25_docs: List[Document]) -> List[Dict[str, Any]]:
        """
        Fuses, deduplicates, and structures documents returned simultaneously from different
        data structures (e.g., Vector DB dense embeddings and BM25 sparse index matches).
        
        This method:
        1. Deduplicates documents by comparing page_content
        2. Normalizes importance scores from vector and BM25 sources
        3. Structures output as list of dicts with id, text, importance
        
        Args:
            vector_docs: List of Document objects from vector search (typically higher scores).
            bm25_docs: List of Document objects from BM25 keyword search (typically lower scores).
        
        Returns:
            List of deduplicated document dictionaries with structure:
            [
                {
                    'id': str,           # Document identifier
                    'text': str,         # Page content
                    'importance': float  # Normalized importance score (0.0-1.0)
                },
                ...
            ]
        """
        seen_contents = set()
        fused_collection = []
        
        # De-duplicate dense semantic documents from vector search (priority)
        for idx, doc in enumerate(vector_docs):
            cleaned_content = doc.page_content.strip()
            if cleaned_content and cleaned_content not in seen_contents:
                seen_contents.add(cleaned_content)
                # Extract importance score with fallback chain: 'score' → 'relevance' → 0.90
                importance = float(doc.metadata.get("score", doc.metadata.get("relevance", 0.90)))
                # Clamp importance to valid range [0.0, 1.0]
                importance = max(0.0, min(1.0, importance))
                
                fused_collection.append({
                    "id": str(doc.metadata.get("id", f"vec_doc_{idx}")),
                    "text": cleaned_content,
                    "importance": importance
                })
                
        # Fill remaining slots with unique structural keyword search tracking data (secondary)
        for idx, doc in enumerate(bm25_docs):
            cleaned_content = doc.page_content.strip()
            if cleaned_content and cleaned_content not in seen_contents:
                seen_contents.add(cleaned_content)
                # BM25 scores typically lower, default to 0.70
                importance = float(doc.metadata.get("score", doc.metadata.get("relevance", 0.70)))
                # Clamp importance to valid range [0.0, 1.0]
                importance = max(0.0, min(1.0, importance))
                
                fused_collection.append({
                    "id": str(doc.metadata.get("id", f"bm25_doc_{idx}")),
                    "text": cleaned_content,
                    "importance": importance
                })
                
        return fused_collection

    def invoke(self, input: Dict[str, Any], config: Optional[RunnableConfig] = None) -> PromptValue:
        """
        Orchestrates and compiles the context lifecycle tree dynamically during standard LCEL executions.
        
        This is the main entry point called when the engine is used in a LangChain pipeline.
        It executes all four stages of context compilation:
        
        Stage 1: Memory Partitioning
            - Extract chat history and split into active window + archive summary
        
        Stage 2: Hybrid Retrieval Fusion
            - Merge vector and BM25 documents with importance normalization
        
        Stage 3: Component Graph Compilation
            - Instantiate component tree with system invariants and elastic pools
        
        Stage 4: Token-Aware Budget Allocation
            - Process components by priority, allocate tokens, apply fallback compression
        
        Stage 5: Output Packaging
            - Wrap final structured prompt in LangChain StringPromptValue
        
        Args:
            input: Dictionary containing:
                - 'query' (str): Current user question
                - 'chat_history' (list): Message history [{"role": "user"|"assistant", "content": "..."}]
                - 'vector_docs' (list): Document objects from vector search
                - 'bm25_docs' (list): Document objects from BM25 search
            config: Optional LangChain RunnableConfig for execution context.
        
        Returns:
            StringPromptValue: LangChain-compatible prompt value ready for LLM invocation.
        """
        encoder = tiktoken.get_encoding(self.encoder_name)
        remaining_budget = self.max_tokens
        
        # Extract primitive execution tokens from input payload
        query_text = input.get("query", "").strip()
        chat_history = input.get("chat_history", [])
        vector_docs = input.get("vector_docs", [])
        bm25_docs = input.get("bm25_docs", [])
        
        # Validate input types
        if not isinstance(chat_history, list):
            chat_history = []
        if not isinstance(vector_docs, list):
            vector_docs = []
        if not isinstance(bm25_docs, list):
            bm25_docs = []
        
        # ===== STAGE 1: MEMORY PARTITIONING =====
        # Run automated memory partitioning & background aggregation loops
        recent_history_window = chat_history[-self.recent_window_size:] if chat_history else []
        archived_summary_block = self._auto_summarize_long_memory(chat_history)
        
        # ===== STAGE 2: HYBRID RETRIEVAL FUSION =====
        # Run hybrid metadata fusion processing
        fused_contexts = self._auto_hybrid_fuse(vector_docs, bm25_docs)
        
        # Format conversation lines into structured, predictable text strings
        history_lines = [
            f"[{m.get('role', 'user').upper()}]: {m.get('content', '')}"
            for m in recent_history_window
            if m.get('content', '').strip()  # Skip empty messages
        ]
        formatted_history_str = "\\n".join(history_lines) if history_lines else "No recent conversations logged."
        
        # ===== STAGE 3: COMPONENT GRAPH COMPILATION =====
        # Formulate runtime dictionary state mapping variables
        runtime_state = {
            "query": query_text,
            "archive_summary_block": archived_summary_block,
            "chat_history_window": formatted_history_str,
            "fused_contexts": fused_contexts
        }
        
        # Instantiate declarative layout context component tree
        # Priority rules ensure that base systems and direct questions are allocated tokens first
        component_tree = [
            StaticContextComponent(
                name="system_layer", 
                template=(
                    "System Instructions: Operate as an authoritative enterprise engineering assistant. "
                    "Use the archived logs and context blocks to answer with precision.\\n\\n"
                    "[Long-Term Archived Memory]: {archive_summary_block}"
                ), 
                priority=0
            ),
            StaticContextComponent(
                name="user_query_layer", 
                template=(
                    "[Recent Conversations Window]:\\n{chat_history_window}\\n\\n"
                    "[Current User Question]: {query}"
                ), 
                priority=10
            ),
            AdaptiveContextPool(
                name="knowledge_pool_layer", 
                priority=20, 
                input_key="fused_contexts"
            )
        ]
        
        # Process the pipeline components strictly according to their priority ordering
        sorted_pipeline = sorted(component_tree, key=lambda c: c.priority)
        compiled_payloads = {}
        
        # ===== STAGE 4: TOKEN-AWARE BUDGET ALLOCATION =====
        # Execute the token-aware budget allocation engine loop
        for component in sorted_pipeline:
            try:
                rendered_text, tokens_consumed = component.render(runtime_state, remaining_budget)
                compiled_payloads[component.name] = rendered_text
                remaining_budget -= tokens_consumed
                if remaining_budget < 0:
                    remaining_budget = 0
            except Exception as e:
                # Log component rendering errors but continue with other components
                compiled_payloads[component.name] = f"[Component {component.name} Error: {str(e)}]"
                
        # ===== STAGE 5: OUTPUT PACKAGING =====
        # Compile the final structured prompt layout payload string
        final_prompt_output = (
            f"{compiled_payloads.get('system_layer', '')}\\n\\n"
            f"=== START RETRIEVED DATA CONTEXT ===\\n"
            f"{compiled_payloads.get('knowledge_pool_layer', '')}\\n"
            f"=== END RETRIEVED DATA CONTEXT ===\\n\\n"
            f"{compiled_payloads.get('user_query_layer', '')}"
        )
        
        # Return packaged PromptValue for downstream LLM compatibility
        return StringPromptValue(text=final_prompt_output.strip())
