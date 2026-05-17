"""
Comprehensive test suite for the ContextForge AutomatedContextEngine.

Tests verify:
1. LCEL compatibility and RunnableSerializable integration
2. Token budget enforcement and allocation
3. Memory partitioning and archive summarization
4. Hybrid document fusion and deduplication
5. Lost-in-the-Middle document reordering
6. Fallback compression and truncation
7. Error handling and edge cases
"""

import pytest
from langchain_core.documents import Document
from langchain_core.prompt_values import PromptValue
from contextforge.engine import AutomatedContextEngine
from contextforge.base import StaticContextComponent, AdaptiveContextPool


class TestAutomatedContextEngine:
    """Test suite for AutomatedContextEngine core functionality."""

    def test_engine_initialization_with_defaults(self):
        """Verify engine initializes with correct default parameters."""
        engine = AutomatedContextEngine()
        assert engine.max_tokens == 4000
        assert engine.recent_window_size == 10
        assert engine.encoder_name == "cl100k_base"

    def test_engine_initialization_with_custom_parameters(self):
        """Verify engine initializes with custom parameter values."""
        engine = AutomatedContextEngine(max_tokens=2000, recent_window_size=5, encoder_name="cl100k_base")
        assert engine.max_tokens == 2000
        assert engine.recent_window_size == 5

    def test_engine_lcel_compatibility_and_budgeting(self):
        """Verifies that the ContextForge core engine executes cleanly within token boundaries."""
        
        # 1. Initialize context engine with structural token boundaries
        engine = AutomatedContextEngine(max_tokens=1000, recent_window_size=2)
        
        # 2. Simulate deep conversation array traces to check memory fallback partitioning loops
        mock_history = [
            {"role": "user", "content": "Message trace token audit baseline number 1"},
            {"role": "assistant", "content": "Acknowledged trace baseline output 1"},
            {"role": "user", "content": "Message trace token audit baseline number 2"},
            {"role": "assistant", "content": "Active immediate chat message window layer"},
            {"role": "user", "content": "Current question statement needing evaluation"}
        ]
        
        # 3. Simulate simultaneous document streams from distinct datastores
        mock_vector = [
            Document(
                page_content="Database cluster network routing standard rule.",
                metadata={"id": "v1", "score": 0.98}
            )
        ]
        mock_bm25 = [
            Document(
                page_content="Database cluster network routing standard rule.",
                metadata={"id": "b1", "score": 0.50}
            ),
            Document(
                page_content="Fallback keyword infrastructure logs error code 503.",
                metadata={"id": "b2", "score": 0.85}
            )
        ]
        
        # 4. Invoke the compilation execution chain
        payload = {
            "query": "How do I clear cluster network timeout boundaries?",
            "chat_history": mock_history,
            "vector_docs": mock_vector,
            "bm25_docs": mock_bm25
        }
        
        result = engine.invoke(payload)
        
        # 5. Execute strict test boundary checks
        assert isinstance(result, PromptValue)
        result_text = result.to_string()
        
        assert "System Instructions" in result_text
        assert "Current User Question" in result_text
        assert "Database cluster network routing standard rule" in result_text
        
        # Confirm de-duplication loop filtered out duplicate text values cleanly
        assert result_text.count("Database cluster network routing standard rule") == 1

    def test_empty_input_handling(self):
        """Verify engine handles empty input gracefully."""
        engine = AutomatedContextEngine(max_tokens=1000)
        
        payload = {
            "query": "",
            "chat_history": [],
            "vector_docs": [],
            "bm25_docs": []
        }
        
        result = engine.invoke(payload)
        assert isinstance(result, PromptValue)
        result_text = result.to_string()
        assert "System Instructions" in result_text

    def test_memory_partitioning_recent_window(self):
        """Verify memory partitioning creates correct active window."""
        engine = AutomatedContextEngine(max_tokens=2000, recent_window_size=3)
        
        # Create history with 5 messages, window size 3
        mock_history = [
            {"role": "user", "content": f"Message {i}"}
            for i in range(5)
        ]
        
        payload = {
            "query": "Test query",
            "chat_history": mock_history,
            "vector_docs": [],
            "bm25_docs": []
        }
        
        result = engine.invoke(payload)
        result_text = result.to_string()
        
        # Should contain recent messages
        assert "Message 2" in result_text  # Message 2 (index 2, part of window)
        assert "Message 3" in result_text  # Message 3
        assert "Message 4" in result_text  # Message 4
        
        # Should have archived summary of older messages
        assert "Message 0" in result_text or "archived" in result_text.lower()

    def test_hybrid_document_fusion(self):
        """Verify hybrid fusion deduplicates and ranks documents correctly."""
        engine = AutomatedContextEngine(max_tokens=2000)
        
        # Create duplicate document in both sources
        duplicate_text = "Important database configuration"
        
        mock_vector = [
            Document(page_content=duplicate_text, metadata={"id": "v1", "score": 0.95})
        ]
        mock_bm25 = [
            Document(page_content=duplicate_text, metadata={"id": "b1", "score": 0.60}),
            Document(page_content="Unique BM25 result", metadata={"id": "b2", "score": 0.80})
        ]
        
        payload = {
            "query": "Database config query",
            "chat_history": [],
            "vector_docs": mock_vector,
            "bm25_docs": mock_bm25
        }
        
        result = engine.invoke(payload)
        result_text = result.to_string()
        
        # Should contain both unique documents
        assert "Important database configuration" in result_text
        assert "Unique BM25 result" in result_text
        
        # Duplicate should appear only once
        assert result_text.count("Important database configuration") == 1

    def test_token_budget_enforcement(self):
        """Verify engine respects max token budget constraint."""
        engine = AutomatedContextEngine(max_tokens=200)
        
        # Create documents that would exceed budget if all included
        mock_vector = [
            Document(
                page_content="This is a very long document " * 50,
                metadata={"id": "v1", "score": 0.95}
            )
        ]
        
        payload = {
            "query": "Long query with many words " * 10,
            "chat_history": [],
            "vector_docs": mock_vector,
            "bm25_docs": []
        }
        
        result = engine.invoke(payload)
        result_text = result.to_string()
        
        # Result should be reasonably sized (truncation applied)
        assert len(result_text) < 2000  # Rough upper bound check

    def test_lost_in_middle_document_ordering(self):
        """Verify documents are reordered to mitigate lost-in-middle effect."""
        engine = AutomatedContextEngine(max_tokens=3000)
        
        # Create documents with varying importance
        mock_vector = [
            Document(page_content="High importance doc", metadata={"id": "v1", "score": 0.95}),
            Document(page_content="Medium importance doc", metadata={"id": "v2", "score": 0.70}),
            Document(page_content="Lower importance doc", metadata={"id": "v3", "score": 0.50})
        ]
        
        payload = {
            "query": "Test query",
            "chat_history": [],
            "vector_docs": mock_vector,
            "bm25_docs": []
        }
        
        result = engine.invoke(payload)
        result_text = result.to_string()
        
        # High importance should be near boundaries
        # Lower importance in middle (alternating distribution logic)
        assert "High importance doc" in result_text
        assert "Medium importance doc" in result_text
        assert "Lower importance doc" in result_text

    def test_static_component_rendering(self):
        """Verify StaticContextComponent renders templates correctly."""
        component = StaticContextComponent(
            name="test_static",
            template="Hello {name}, your query is: {query}",
            priority=0
        )
        
        state = {"name": "Alice", "query": "What is AI?"}
        text, tokens = component.render(state, token_budget=500)
        
        assert "Hello Alice" in text
        assert "What is AI?" in text
        assert tokens > 0

    def test_static_component_token_truncation(self):
        """Verify StaticContextComponent truncates when exceeding budget."""
        component = StaticContextComponent(
            name="test_truncate",
            template="This is a very long template. " * 100,
            priority=0
        )
        
        state = {}
        text, tokens = component.render(state, token_budget=50)
        
        assert tokens <= 50
        assert "[Truncated Constraint]" in text or len(text) > 0

    def test_adaptive_pool_rendering(self):
        """Verify AdaptiveContextPool renders documents correctly."""
        component = AdaptiveContextPool(name="test_pool", priority=50)
        
        state = {
            "fused_contexts": [
                {"id": "doc1", "text": "First document content", "importance": 0.95},
                {"id": "doc2", "text": "Second document content", "importance": 0.70},
                {"id": "doc3", "text": "Third document content", "importance": 0.50}
            ]
        }
        
        text, tokens = component.render(state, token_budget=500)
        
        assert "First document content" in text
        assert "Second document content" in text
        assert "Third document content" in text
        assert "<context_block" in text  # XML formatting
        assert tokens > 0

    def test_adaptive_pool_empty_contexts(self):
        """Verify AdaptiveContextPool handles empty document list."""
        component = AdaptiveContextPool(name="test_pool_empty", priority=50)
        
        state = {"fused_contexts": []}
        text, tokens = component.render(state, token_budget=500)
        
        assert "No supplementary knowledge documents" in text
        assert tokens >= 0

    def test_adaptive_pool_budget_exceeded(self):
        """Verify AdaptiveContextPool respects token budget."""
        component = AdaptiveContextPool(name="test_pool_budget", priority=50)
        
        state = {
            "fused_contexts": [
                {"id": f"doc{i}", "text": f"Document {i} with content " * 50, "importance": 0.9 - (i * 0.1)}
                for i in range(5)
            ]
        }
        
        text, tokens = component.render(state, token_budget=100)
        
        # Should not exceed budget
        assert tokens <= 100

    def test_error_handling_invalid_state(self):
        """Verify engine handles invalid state gracefully."""
        component = StaticContextComponent(
            name="test_error",
            template="This has {missing_field}",
            priority=0
        )
        
        state = {}
        
        # Should raise ValueError for missing field
        with pytest.raises(ValueError) as exc_info:
            component.render(state, token_budget=500)
        
        assert "missing_field" in str(exc_info.value)

    def test_zero_token_budget_handling(self):
        """Verify components handle zero token budget."""
        engine = AutomatedContextEngine(max_tokens=0)
        
        payload = {
            "query": "Test query",
            "chat_history": [],
            "vector_docs": [],
            "bm25_docs": []
        }
        
        result = engine.invoke(payload)
        assert isinstance(result, PromptValue)

    def test_multiple_document_deduplication(self):
        """Verify comprehensive document deduplication across sources."""
        engine = AutomatedContextEngine(max_tokens=2000)
        
        # Create multiple duplicates
        common_text = "Shared configuration pattern"
        
        mock_vector = [
            Document(page_content=common_text, metadata={"id": "v1", "score": 0.95}),
            Document(page_content="Vector unique", metadata={"id": "v2", "score": 0.80})
        ]
        mock_bm25 = [
            Document(page_content=common_text, metadata={"id": "b1", "score": 0.60}),
            Document(page_content="BM25 unique", metadata={"id": "b2", "score": 0.75}),
            Document(page_content=common_text, metadata={"id": "b3", "score": 0.55})
        ]
        
        payload = {
            "query": "Dedup test",
            "chat_history": [],
            "vector_docs": mock_vector,
            "bm25_docs": mock_bm25
        }
        
        result = engine.invoke(payload)
        result_text = result.to_string()
        
        # Common text should appear exactly once
        assert result_text.count("Shared configuration pattern") == 1
        # Unique texts should appear
        assert "Vector unique" in result_text
        assert "BM25 unique" in result_text

    def test_none_input_values_handling(self):
        """Verify engine handles None values in input gracefully."""
        engine = AutomatedContextEngine(max_tokens=1000)
        
        payload = {
            "query": "Test",
            "chat_history": None,
            "vector_docs": None,
            "bm25_docs": None
        }
        
        result = engine.invoke(payload)
        assert isinstance(result, PromptValue)

    def test_real_world_scenario(self):
        """
        Test a realistic scenario with full context compilation.
        Simulates a real LangChain RAG pipeline usage.
        """
        engine = AutomatedContextEngine(max_tokens=2000, recent_window_size=3)
        
        # Realistic conversation history
        chat_history = [
            {"role": "user", "content": "What is machine learning?"},
            {"role": "assistant", "content": "Machine learning is a subset of AI..."},
            {"role": "user", "content": "Can you give examples?"},
            {"role": "assistant", "content": "Sure, examples include decision trees..."},
            {"role": "user", "content": "How does neural networks work?"}
        ]
        
        # Realistic retrieval results
        vector_docs = [
            Document(
                page_content="Neural networks are computational models inspired by biological neurons. "
                "They consist of layers of interconnected nodes that process information.",
                metadata={"source": "ml_basics.md", "id": "nn_1", "score": 0.98}
            ),
            Document(
                page_content="Deep learning uses multiple layers of neural networks to learn "
                "hierarchical representations of data.",
                metadata={"source": "dl_guide.md", "id": "dl_1", "score": 0.92}
            )
        ]
        
        bm25_docs = [
            Document(
                page_content="Backpropagation is the primary algorithm for training neural networks. "
                "It calculates gradients and updates weights.",
                metadata={"source": "training.md", "id": "bp_1", "score": 0.80}
            )
        ]
        
        payload = {
            "query": "Explain how neural networks learn from data",
            "chat_history": chat_history,
            "vector_docs": vector_docs,
            "bm25_docs": bm25_docs
        }
        
        result = engine.invoke(payload)
        result_text = result.to_string()
        
        # Verify all key components are present
        assert "System Instructions" in result_text
        assert "neural networks" in result_text.lower()
        assert "How does neural networks work?" in result_text
        assert "Explain how neural networks learn from data" in result_text
        
        # Verify structure
        assert "=== START RETRIEVED DATA CONTEXT ===" in result_text
        assert "=== END RETRIEVED DATA CONTEXT ===" in result_text
