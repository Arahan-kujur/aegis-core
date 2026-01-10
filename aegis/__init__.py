"""
Aegis - Human-in-the-loop control layer for AI agents.

Aegis wraps LangChain-style agents and intercepts risky actions,
requiring human approval before execution.
"""

VERSION = "1.0.0"

from aegis.wrapper import AegisWrapper

__all__ = ["AegisWrapper", "VERSION"]

