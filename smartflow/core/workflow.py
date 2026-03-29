"""
Workflow - Main workflow orchestration engine
"""

import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .step import Step, StepResult


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smartflow")


@dataclass
class WorkflowConfig:
    """Workflow configuration options"""
    dry_run: bool = False
    continue_on_error: bool = False
    parallel_execution: bool = False
    log_level: str = "INFO"


@dataclass
class WorkflowResult:
    """Result of executing an entire workflow"""
    success: bool
    steps_executed: int
    steps_failed: int
    total_execution_time: float
    results: Dict[str, StepResult] = field(default_factory=dict)
    final_output: Any = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow result to dictionary"""
        return {
            "success": self.success,
            "steps_executed": self.steps_executed,
            "steps_failed": self.steps_failed,
            "total_execution_time": self.total_execution_time,
            "results": {k: v.to_dict() for k, v in self.results.items()},
            "final_output": self.final_output,
            "error": self.error
        }


class Workflow:
    """
    Main workflow orchestration class.
    Manages execution of multiple steps with context sharing.
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        config: Optional[WorkflowConfig] = None
    ):
        """
        Initialize a workflow.

        Args:
            name: Workflow identifier
            description: Optional workflow description
            config: Optional workflow configuration
        """
        self.name = name
        self.description = description or f"Workflow: {name}"
        self.config = config or WorkflowConfig()
        self.steps: List[Step] = []
        self.context: Dict[str, Any] = {}
        self._created_at = datetime.now()

        # Hooks for lifecycle events
        self._on_start: Optional[Callable] = None
        self._on_complete: Optional[Callable] = None
        self._on_error: Optional[Callable] = None
        self._before_step: Optional[Callable] = None
        self._after_step: Optional[Callable] = None

    def add_step(self, step: Step) -> "Workflow":
        """
        Add a step to this workflow.

        Args:
            step: Step instance to add

        Returns:
            Self for method chaining
        """
        self.steps.append(step)
        logger.debug(f"Added step: {step.name}")
        return self

    def add_steps(self, steps: List[Step]) -> "Workflow":
        """
        Add multiple steps to this workflow.

        Args:
            steps: List of Step instances

        Returns:
            Self for method chaining
        """
        self.steps.extend(steps)
        return self

    def set_context(self, **kwargs) -> "Workflow":
        """
        Set initial context variables.

        Args:
            **kwargs: Context variables to set

        Returns:
            Self for method chaining
        """
        self.context.update(kwargs)
        return self

    def on_start(self, callback: Callable) -> "Workflow":
        """Set workflow start callback"""
        self._on_start = callback
        return self

    def on_complete(self, callback: Callable) -> "Workflow":
        """Set workflow complete callback"""
        self._on_complete = callback
        return self

    def on_error(self, callback: Callable) -> "Workflow":
        """Set workflow error callback"""
        self._on_error = callback
        return self

    def before_step(self, callback: Callable) -> "Workflow":
        """Set pre-step callback"""
        self._before_step = callback
        return self

    def after_step(self, callback: Callable) -> "Workflow":
        """Set post-step callback"""
        self._after_step = callback
        return self

    def run(self, **initial_context) -> WorkflowResult:
        """
        Execute this workflow.

        Args:
            **initial_context: Initial context variables

        Returns:
            WorkflowResult with execution details
        """
        start_time = time.time()
        results = {}
        steps_executed = 0
        steps_failed = 0
        error = None
        final_output = None

        # Update context with initial values
        self.context.update(initial_context)

        logger.info(f"Starting workflow: {self.name}")

        try:
            # Execute on_start callback
            if self._on_start:
                self._on_start(self)

            # Execute all steps
            for step in self.steps:
                if not step.enabled:
                    logger.debug(f"Skipping disabled step: {step.name}")
                    continue

                # Execute before_step callback
                if self._before_step:
                    self._before_step(self, step)

                # Execute step with retries
                step_result = self._execute_step_with_retries(step)
                results[step.name] = step_result
                steps_executed += 1

                # Update context with step output
                self.context[step.name] = step_result.output

                # Execute after_step callback
                if self._after_step:
                    self._after_step(self, step, step_result)

                if step_result.success:
                    logger.info(f"✓ Step '{step.name}' completed in {step_result.execution_time:.2f}s")
                else:
                    steps_failed += 1
                    logger.error(f"✗ Step '{step.name}' failed: {step_result.error}")

                    if not self.config.continue_on_error:
                        error = f"Step '{step.name}' failed"
                        break

            final_output = self._extract_final_output(results)

            # Execute on_complete callback
            if self._on_complete:
                self._on_complete(self, results)

            success = steps_failed == 0
            logger.info(f"Workflow completed: {steps_executed} steps, {steps_failed} failed")

        except Exception as e:
            success = False
            error = str(e)
            logger.error(f"Workflow error: {error}")

            if self._on_error:
                self._on_error(self, e)

        execution_time = time.time() - start_time

        return WorkflowResult(
            success=success,
            steps_executed=steps_executed,
            steps_failed=steps_failed,
            total_execution_time=execution_time,
            results=results,
            final_output=final_output,
            error=error
        )

    def _execute_step_with_retries(self, step: Step) -> StepResult:
        """
        Execute a step with retry logic.

        Args:
            step: Step to execute

        Returns:
            StepResult from last execution attempt
        """
        last_result = None

        for attempt in range(step.max_retries + 1):
            try:
                step_start = time.time()
                result = step.execute(self.context)
                execution_time = time.time() - step_start
                result.execution_time = execution_time

                if result.success or attempt == step.max_retries:
                    return result

                logger.warning(f"Step '{step.name}' failed, retry {attempt + 1}/{step.max_retries}")
                time.sleep(min(2 ** attempt, 10))  # Exponential backoff

            except Exception as e:
                last_result = StepResult(
                    success=False,
                    output=None,
                    error=str(e)
                )
                logger.error(f"Step '{step.name}' crashed on attempt {attempt + 1}: {e}")

                if attempt == step.max_retries:
                    return last_result

                time.sleep(min(2 ** attempt, 10))

        return StepResult(success=False, output=None, error="Max retries exceeded")

    def _extract_final_output(self, results: Dict[str, StepResult]) -> Any:
        """
        Extract final output from workflow results.

        Args:
            results: Dictionary of step results

        Returns:
            Final output (output from last successful step)
        """
        if not results:
            return None

        # Return output from the last步骤
        last_step = list(results.keys())[-1]
        return results[last_step].output

    def validate(self) -> bool:
        """
        Validate workflow configuration.

        Returns:
            True if workflow is properly configured
        """
        if not self.steps:
            logger.warning(f"Workflow '{self.name}' has no steps")
            return False

        valid = True
        for step in self.steps:
            if not step.validate():
                logger.error(f"Invalid step: {step.name}")
                valid = False

        return valid

    def __repr__(self) -> str:
        return f"<Workflow(name='{self.name}', steps={len(self.steps)})>"