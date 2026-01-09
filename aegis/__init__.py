"""
Aegis - Human-in-the-loop control layer for AI agents.

Aegis wraps LangChain-style agents and intercepts risky actions,
requiring human approval before execution.
"""

from aegis.wrapper import AegisWrapper

__all__ = ["AegisWrapper"]

