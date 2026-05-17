"""
First-class package integration workspace ecosystem module hooks.

This module exposes core interface layers clearly to top-level package boundaries,
enabling clean integration with LangChain LCEL pipelines and external orchestration systems.
"""

from contextforge.engine import AutomatedContextEngine
from contextforge.base import BaseContextComponent, StaticContextComponent, AdaptiveContextPool

__all__ = [
    "AutomatedContextEngine",
    "BaseContextComponent",
    "StaticContextComponent",
    "AdaptiveContextPool"
]
