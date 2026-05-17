import abc
from typing import Dict, Any, List
from langchain_core.runnables import RunnableSerializable
from langchain_core.prompt_values import PromptValue

class BaseContextComponent(abc.ABC):
    """Abstract interface defining the React-like prompt component lifecycle."""
    
    def __init__(self, name: str, priority: int = 100):
        self.name = name
        self.priority = priority

    @abc.abstractmethod
    def render(self, state: Dict[str, Any], token_budget: int) -> tuple[str, int]:
        """
        Calculates and formats data inputs into clean text blocks.
        
        Returns:
            tuple: (Rendered Context Substring, Actual Tokens Consumed)
        """
        pass
