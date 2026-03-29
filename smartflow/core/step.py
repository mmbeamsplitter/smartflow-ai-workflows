"""
Step - Individual workflow step abstraction
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class StepResult:
    """Result of executing a workflow step"""
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata or {}
        }


class Step(ABC):
    """
    Abstract base class for workflow steps.
    All specific action types inherit from this.
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        enabled: bool = True,
        max_retries: int = 3,
        timeout: Optional[float] = None
    ):
        """
        Initialize a workflow step.

        Args:
            name: Step identifier
            description: Optional step description
            enabled: Whether this step is active
            max_retries: Maximum retry attempts on failure
            timeout: Optional timeout in seconds
        """
        self.name = name
        self.description = description or f"Execute {name}"
        self.enabled = enabled
        self.max_retries = max_retries
        self.timeout = timeout
        self._created_at = datetime.now()

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> StepResult:
        """
        Execute this step with given context.

        Args:
            context: Workflow execution context with variables

        Returns:
            StepResult containing success status and output
        """
        pass

    def validate(self) -> bool:
        """
        Validate this step's configuration.

        Returns:
            True if configuration is valid
        """
        return bool(self.name and self.enabled)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"