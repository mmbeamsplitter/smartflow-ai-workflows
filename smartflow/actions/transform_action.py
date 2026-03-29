"""
Transform Action - Transform and process data within workflows
"""

import time
import json
import re
from typing import Any, Dict, Callable, Union, Optional, List

from ..core.step import Step, StepResult


class TransformAction(Step):
    """
    Execute data transformations and processing operations.
    Supports multiple built-in transformation types and custom functions.
    """

    TRANSFORMS = {
        "to_upper": lambda x: str(x).upper(),
        "to_lower": lambda x: str(x).lower(),
        "to_int": lambda x: int(x),
        "to_float": lambda x: float(x),
        "to_string": lambda x: str(x),
        "to_list": lambda x: list(x) if not isinstance(x, list) else x,
        "length": lambda x: len(x),
        "strip": lambda x: str(x).strip(),
        "reverse": lambda x: x[::-1] if isinstance(x, str) else list(x)[::-1],
    }

    def __init__(
        self,
        name: str,
        source: str,
        operation: str,
        target: Optional[str] = None,
        custom_function: Optional[Callable] = None,
        description: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize a transform action.

        Args:
            name: Action name
            source: Source variable name (or template)
            operation: Transformation operation name or custom function
            target: Target variable name to store result (defaults to source)
            custom_function: Optional custom transformation function
            description: Optional description
            **kwargs: Additional Step parameters
        """
        super().__init__(name, description, **kwargs)
        self.source = source
        self.operation = operation
        self.target = target or source
        self.custom_function = custom_function

    def _get_value(self, context: Dict[str, Any]) -> Any:
        """
        Get source value from context.

        Args:
            context: Workflow context

        Returns:
            Source value
        """
        # Check if source is a template
        if "{" in self.source and "}" in self.source:
            try:
                return self.source.format(**context)
            except (KeyError, ValueError):
                return self.source

        # Direct variable access
        if self.source in context:
            return context[self.source]

        return self.source

    def _apply_operation(self, value: Any) -> Any:
        """
        Apply transformation operation.

        Args:
            value: Value to transform

        Returns:
            Transformed value
        """
        # Use custom function if provided
        if self.custom_function:
            return self.custom_function(value)

        # Use built-in operation
        if self.operation in self.TRANSFORMS:
            return self.TRANSFORMS[self.operation](value)

        # Try regex operations
        if self.operation.startswith("regex_"):
            pattern = self.operation[6:]
            return re.findall(pattern, str(value))

        # Try JSON parsing
        if self.operation == "parse_json":
            if isinstance(value, str):
                return json.loads(value)
            return value

        # Try JSON serialization
        if self.operation == "to_json":
            return json.dumps(value, indent=2)

        # Raise error for unknown operation
        raise ValueError(f"Unknown transform operation: {self.operation}")

    def execute(self, context: Dict[str, Any]) -> StepResult:
        """
        Execute this transform action.

        Args:
            context: Workflow context

        Returns:
            StepResult with transformed data
        """
        start_time = time.time()

        try:
            # Get source value
            source_value = self._get_value(context)

            # Apply transformation
            result = self._apply_operation(source_value)

            execution_time = time.time() - start_time

            return StepResult(
                success=True,
                output=result,
                execution_time=execution_time,
                metadata={
                    "source": self.source,
                    "operation": self.operation,
                    "target": self.target,
                    "input_type": type(source_value).__name__,
                    "output_type": type(result).__name__
                }
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return StepResult(
                success=False,
                output=None,
                error=str(e),
                execution_time=execution_time
            )

    def validate(self) -> bool:
        """Validate transform action configuration"""
        if not super().validate():
            return False

        if not self.source:
            return False

        has_operation = (
            callable(self.custom_function) or
            self.operation in self.TRANSFORMS or
            self.operation.startswith("regex_") or
            self.operation in ["parse_json", "to_json"]
        )

        return bool(has_operation)


def extract_field(source: str, field: str, default: Any = None) -> TransformAction:
    """
    Create an action to extract a field from a dictionary.

    Args:
        source: Source variable name
        field: Field to extract
        default: Default value if field not found

    Returns:
        TransformAction instance
    """
    def extract_func(value: Any, f: str = field, d: Any = default) -> Any:
        if isinstance(value, dict):
            return value.get(f, d)
        if hasattr(value, f):
            return getattr(value, f)
        return d

    return TransformAction(
        name=f"extract_{field}",
        source=source,
        operation="custom",
        custom_function=extract_func
    )


def format_string(source: str, template: str) -> TransformAction:
    """
    Create an action to format a string.

    Args:
        source: Source variable name
        template: Format template (use {value} for the value)

    Returns:
        TransformAction instance
    """
    def format_func(value: Any, t: str = template) -> str:
        return t.format(value=value)

    return TransformAction(
        name=f"format_{source}",
        source=source,
        operation="custom",
        custom_function=format_func
    )