"""
SmartFlow AI - Universal AI-Powered Workflow Automation Platform

Build intelligent, multi-step workflows with LLM reasoning capabilities.
"""

from .core.workflow import Workflow
from .core.step import Step
from .actions.llm_action import LLMAction
from .actions.api_action import APIAction
from .actions.conditional_action import ConditionalAction
from .actions.transform_action import TransformAction

__version__ = "0.1.0"
__all__ = [
    "Workflow",
    "Step",
    "LLMAction",
    "APIAction",
    "ConditionalAction",
    "TransformAction",
]

__doc__ = """
SmartFlow AI Platform

A universal workflow automation platform that combines traditional automation
with modern LLM intelligence for intelligent, context-aware automation.
"""

# Convenience function for quick workflow creation
def create_workflow(name: str, description: str = "") -> "Workflow":
    """
    Quick workflow creation with sensible defaults.

    Args:
        name: Workflow name
        description: Optional description

    Returns:
        Configured Workflow instance
    """
    return Workflow(name=name, description=description)