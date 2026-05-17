"""
Base component abstractions for contextmg context engineering framework.

Defines the abstract baseline component lifecycle and concrete implementations for
static text blocks and adaptive context pools that operate with strict token budgets.
"""

import abc
import tiktoken
from typing import Dict, Any, List, Tuple, Optional


class BaseContextComponent(abc.ABC):
    """
    Abstract baseline component defining the React-like prompt element lifecycle.
    Every module must track its execution priority and manage contextual data streams.
    
    Attributes:
        name: Unique identifier for this component in the rendering pipeline.
        priority: Execution priority where lower values execute first (0 = highest priority).
    """
    
    def __init__(self, name: str, priority: int = 100):
        """
        Initialize a context component.
        
        Args:
            name: Descriptive name for the component.
            priority: Integer priority value (lower = higher priority execution).
        """
        self.name = name
        self.priority = priority

    @abc.abstractmethod
    def render(self, state: Dict[str, Any], token_budget: int) -> Tuple[str, int]:
        """
        Processes and formats raw contextual data streams within an absolute token constraint.
        
        This method must be implemented by all subclasses to provide component-specific
        rendering logic while respecting strict token allocation boundaries.
        
        Args:
            state: The current universal application runtime dictionary metadata state.
                   Contains all runtime variables needed for rendering.
            token_budget: Hard total maximum tokens allowed for this specific execution layer.
                         Rendering must not exceed this boundary.
            
        Returns:
            Tuple[str, int]: A tuple of:
                - Rendered Context Text Output String: The formatted content for this component.
                - Final Tokens Consumed: Exact token count of the rendered output.
                
        Raises:
            ValueError: If rendering fails or state validation fails.
            TypeError: If token_budget or state are invalid types.
        """
        pass


class StaticContextComponent(BaseContextComponent):
    """
    Handles absolute, non-negotiable text block insertions such as core system instructions,
    guardrails, or raw queries that must be preserved with top-tier execution priority.
    
    This component supports template variable substitution and enforces strict token limits
    with defensive fallback truncation strategies.
    
    Attributes:
        template: String template with Python format placeholders (e.g., "{variable_name}").
        priority: Execution priority (default 0 = highest, ensures system instructions run first).
    """
    
    def __init__(self, name: str, template: str, priority: int = 0):
        """
        Initialize a static context component.
        
        Args:
            name: Unique identifier for this static component.
            template: String template with {field} placeholders for state substitution.
            priority: Execution priority (default 0 for system invariants).
        """
        super().__init__(name, priority)
        self.template = template

    def render(self, state: Dict[str, Any], token_budget: int) -> Tuple[str, int]:
        """
        Render the static template with state variable substitution and token enforcement.
        
        Process:
        1. Validate input parameters and token budget.
        2. Perform safe template string interpolation with state dictionary.
        3. Count tokens using tiktoken's cl100k_base encoding.
        4. If tokens exceed budget, apply defensive character truncation.
        5. Return rendered content with accurate token count.
        
        Args:
            state: Runtime state dictionary containing template variables.
            token_budget: Maximum tokens allowed (0 = no rendering).
            
        Returns:
            Tuple[str, int]: (rendered_content, tokens_consumed).
            
        Raises:
            ValueError: If template variables are missing from state.
        """
        encoder = tiktoken.get_encoding("cl100k_base")
        
        # Handle zero or negative token budget edge case
        if token_budget <= 0:
            return "", 0
        
        # Inject state properties dynamically using formal interpolation patterns
        try:
            content = self.template.format(**state)
        except KeyError as e:
            missing_field = str(e).strip("'")
            raise ValueError(
                f"Static component '{self.name}' variable initialization failure: "
                f"required field '{missing_field}' not found in state dictionary. "
                f"Available keys: {list(state.keys())}"
            )
        except TypeError as e:
            raise ValueError(
                f"Static component '{self.name}' template formatting error: {str(e)}"
            )
            
        tokens = len(encoder.encode(content))
        
        # Enforce structural boundary safeguards: truncate if necessary
        if tokens > token_budget:
            # Estimate character to token ratio (roughly 4 chars per token for CL100K)
            char_budget = int(token_budget * 4)
            # Apply defensive character slicing with truncation marker
            content = content[:char_budget] + "\n... [Truncated Constraint]"
            tokens = len(encoder.encode(content))
            
        return content, tokens


class AdaptiveContextPool(BaseContextComponent):
    """
    Dynamic context storage buffer that automatically distributes its calculated 
    token allowance budget among retrieved documents using importance-weighted ranking.
    
    This component implements the "Lost-in-the-Middle" mitigation strategy by placing
    high-importance documents at the start and end of the pool (where LLM attention peaks)
    and lower-importance documents in the middle.
    
    Document format expected in state[input_key]:
        [
            {
                'id': str,           # Unique document identifier
                'text': str,         # Document content
                'importance': float  # Relevance score (higher = more important)
            },
            ...
        ]
    
    Attributes:
        input_key: State dictionary key where document list is stored (default "fused_contexts").
        priority: Execution priority (typically 50+ to allow elastic allocation after system blocks).
    """
    
    def __init__(self, name: str, priority: int = 50, input_key: str = "fused_contexts"):
        """
        Initialize an adaptive context pool.
        
        Args:
            name: Unique identifier for this context pool.
            priority: Execution priority (higher values = lower execution priority).
            input_key: State dictionary key containing the document list.
        """
        super().__init__(name, priority)
        self.input_key = input_key

    def render(self, state: Dict[str, Any], token_budget: int) -> Tuple[str, int]:
        """
        Render the context pool with intelligent document ordering and token allocation.
        
        Process:
        1. Validate token budget and retrieve document fragments from state.
        2. Sort documents by importance in descending order.
        3. Apply "Middle-Out" alternating distribution: place high importance at margins.
        4. Iteratively add documents while tracking token consumption.
        5. If a document exceeds remaining budget, attempt word-level compression.
        6. Stop adding documents once budget is exhausted.
        7. Return formatted context blocks with total token count.
        
        Document Ordering Strategy (Lost-in-the-Middle Mitigation):
        For documents sorted by importance [D1, D2, D3, D4, D5]:
        - D1 (highest) → append to end
        - D2 → prepend to start
        - D3 (middle, lowest attention) → append to end
        - D4 → prepend to start
        - D5 (second highest) → append to end
        Result: [D2, D4] + [D5, D3, D1] = D2, D4, D5, D3, D1
        This creates peak attention at both boundaries.
        
        Args:
            state: Runtime state dictionary containing document list at state[input_key].
            token_budget: Maximum tokens allowed for this component.
            
        Returns:
            Tuple[str, int]: (rendered_context_xml, tokens_consumed).
        """
        encoder = tiktoken.get_encoding("cl100k_base")
        
        if token_budget <= 0:
            return "", 0

        # Retrieve documents structural pool schema: [{'id': str, 'text': str, 'importance': float}]
        fragments = state.get(self.input_key, [])
        if not fragments:
            empty_message = "<context_pool>\nNo supplementary knowledge documents injected.\n</context_pool>"
            tokens = len(encoder.encode(empty_message))
            return empty_message, min(tokens, token_budget)

        # Validate fragment structure
        for idx, frag in enumerate(fragments):
            if not isinstance(frag, dict):
                raise ValueError(
                    f"Context pool fragment at index {idx} must be a dictionary. "
                    f"Got {type(frag).__name__}"
                )
            if "text" not in frag or "importance" not in frag:
                raise ValueError(
                    f"Context pool fragment at index {idx} missing required keys. "
                    f"Must contain 'text' and 'importance'. Got keys: {list(frag.keys())}"
                )

        # Execute absolute deterministic ranking sorted descending by algorithmic importance
        sorted_frags = sorted(fragments, key=lambda x: float(x.get("importance", 1.0)), reverse=True)
        
        rendered_blocks = []
        consumed_tokens = 0
        
        # Counteract 'Lost-in-the-Middle' LLM behavior using an alternating marginal placement pattern
        # High importance → start/end, Low importance → middle
        for i, frag in enumerate(sorted_frags):
            block_id = frag.get("id", f"idx_{i}")
            block_content = frag.get("text", "").strip()
            
            # Skip empty fragments
            if not block_content:
                continue
            
            # Format fragment with XML-style tags for explicit structure
            block_text = f"<context_block id='{block_id}'>\n{block_content}\n</context_block>"
            block_tokens = len(encoder.encode(block_text))
            
            # If a block breaches the remaining budget space, attempt fine-grained word compression
            if consumed_tokens + block_tokens > token_budget:
                remaining_allowance = token_budget - consumed_tokens
                
                # Only attempt compression if meaningful allowance exists (>30 tokens)
                if remaining_allowance > 30:
                    # Estimate word count using character-based heuristic (roughly 5 chars per word)
                    words = block_content.split()
                    # Fractional word budget estimation: use ~70% of remaining tokens for words
                    estimated_words_available = int(remaining_allowance * 0.70 / 1.3)  # 1.3 tokens per word average
                    
                    if estimated_words_available > 5:  # Only compress if at least 5 words fit
                        compressed_text_subset = " ".join(words[:max(5, estimated_words_available)])
                        compressed_block = (
                            f"<context_block id='{block_id}' format='compressed'>\n"
                            f"{compressed_text_subset}\n... [Content Truncated Due to Token Budget]\n"
                            f"</context_block>"
                        )
                        compressed_tokens = len(encoder.encode(compressed_block))
                        
                        # Add compressed block if it fits
                        if consumed_tokens + compressed_tokens <= token_budget:
                            # Alternating placement: even indices go to end, odd to start
                            if i % 2 == 0:
                                rendered_blocks.append(compressed_block)
                            else:
                                rendered_blocks.insert(0, compressed_block)
                            consumed_tokens += compressed_tokens
                
                # Halt further context injection processing completely once budget bounds saturate
                break
            
            # Distribute chunks alternatingly (highest priority split between start and end)
            # Even indices: append to end (boundary high attention)
            # Odd indices: prepend to start (boundary high attention)
            if i % 2 == 0:
                rendered_blocks.append(block_text)
            else:
                rendered_blocks.insert(0, block_text)
                
            consumed_tokens += block_tokens

        # Wrap all context blocks in a structured XML container
        if rendered_blocks:
            final_payload = "<context_pool>\n" + "\n\n".join(rendered_blocks) + "\n</context_pool>"
        else:
            final_payload = "<context_pool>\nNo documents fit within token budget.\n</context_pool>"
        
        # Final token count of the complete payload
        final_tokens = len(encoder.encode(final_payload))
        
        return final_payload, min(final_tokens, token_budget)
