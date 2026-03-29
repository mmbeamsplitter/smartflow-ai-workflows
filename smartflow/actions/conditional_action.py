"""
Conditional Action - Execute logic with conditional branching
"""

import time
from typing import Any, Dict, Callable, Optional

from ..core.step import Step, StepResult


class ConditionalAction(Step):
    """
    Execute conditional logic based on context variables.
    Allows for dynamic workflow behavior and branching.
    """

    def __init__(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], Any],
        true_action: Callable[[Dict[str, Any]], Any],
        false_action: Optional[Callable[[Dict[str, Any]], Any]] = None,
        description: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize a conditional action.

        Args:
            name: Action name
            condition: Function that evaluates to boolean based on context
            true_action: Function to execute if condition is true
            false_action: Optional function to execute if condition is false
            description: Optional description
            **kwargs: Additional Step parameters
        """
        super().__init__(name, description, **kwargs)
        self.condition = condition
        self.true_action = true_action
        self.false_action = false_action

    def execute(self, context: Dict[str, Any]) -> StepResult:
        """
        Execute this conditional action.

        Args:
            context: Workflow context

        Returns:
            StepResult with conditional execution output
        """
        start_time = time.time()

        try:
            # Evaluate condition
            condition_result = self.condition(context)
            is_true = bool(condition_result)

            # Execute appropriate branch
            if is_true:
                output = self.true_action(context)
            elif self.false_action:
                output = self.false_action(context)
            else:
                output = None

            execution_time = time.time() - start_time

            return StepResult(
                success=True,
                output={
                    "condition_result": condition_result,
                    "branch": "true" if is_true else "false",
                    "action_output": output
                },
                execution_time=execution_time,
                metadata={
                    "condition_evaluated": True,
                    "branch_taken": "true" if is_true else "false"
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
        """Validate conditional action configuration"""
        if not super().validate():
            return False

        return callable(self.condition) and callable(self.true_action)


def simple_condition(variable_name: str, operator: str, value: Any) -> Callable[[Dict[str, Any]], bool]:
    """
    Create a simple condition function.

    Args:
        variable_name: Context variable name to check
        operator: Comparison operator (==, !=, >, <, >=, <=, in, not in)
        value: Value to compare against

    Returns:
        Condition function
    """
    def condition(context: Dict[str, Any]) -> bool:
        if variable_name not in context:
            return False

        var_value = context[variable_name]

        if operator == "==":
            return var_value == value
        elif operator == "!=":
            return var_value != value
        elif operator == ">":
            return var_value > value
        elif operator == "<":
            return var_value < value
        elif operator == ">=":
            return var_value >= value
        elif operator == "<=":
            return var_value <= value
        elif operator == "in":
            return var_value in value
        elif operator == "not in":
            return var_value not in value
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    return condition