"""
contextmg: A declarative, fine-grained automated context engineering framework for LLMs.

This module provides a React-like component-driven architecture for managing prompt context
with deterministic token budgeting and dynamic allocation strategies.
"""

from contextmg.engine import AutomatedContextEngine
from contextmg.base import BaseContextComponent, StaticContextComponent, AdaptiveContextPool

__all__ = [
    "AutomatedContextEngine",
    "BaseContextComponent",
    "StaticContextComponent",
    "AdaptiveContextPool"
]

__version__ = "0.1.0"
