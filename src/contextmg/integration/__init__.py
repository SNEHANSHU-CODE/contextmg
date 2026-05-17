"""
First-class package integration workspace ecosystem module hooks.

This module exposes core interface layers clearly to top-level package boundaries,
enabling clean integration with LangChain LCEL pipelines and external orchestration systems.
"""

from contextmg.engine import AutomatedContextEngine
from contextmg.base import BaseContextComponent, StaticContextComponent, AdaptiveContextPool

__all__ = [
    "AutomatedContextEngine",
    "BaseContextComponent",
    "StaticContextComponent",
    "AdaptiveContextPool"
]
