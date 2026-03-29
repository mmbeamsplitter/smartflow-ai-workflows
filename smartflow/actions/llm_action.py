"""
LLM Action - Execute LLM (Large Language Model) operations
"""

import os
import time
from typing import Any, Dict, Optional
from dataclasses import dataclass

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from ..core.step import Step, StepResult


@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: str = "openai"  # "openai" or "anthropic"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1000
    api_key: Optional[str] = None
    timeout: float = 30.0


class LLMAction(Step):
    """
    Execute LLM-powered operations for intelligent responses.
    Supports OpenAI and Anthropic models.
    """

    def __init__(
        self,
        name: str,
        prompt: str,
        config: Optional[LLMConfig] = None,
        description: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize an LLM action.

        Args:
            name: Action name
            prompt: The prompt template to send to the LLM
            config: LLM configuration options
            description: Optional description
            **kwargs: Additional Step parameters
        """
        super().__init__(name, description, **kwargs)
        self.prompt_template = prompt
        self.config = config or LLMConfig()

        # Get API key from config or environment
        if not self.config.api_key:
            self.config.api_key = self._get_api_key()

        self._client = None

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment based on provider"""
        if self.config.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif self.config.provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        return None

    def _get_client(self):
        """Get or create the LLM client"""
        if self._client is not None:
            return self._client

        if not self.config.api_key:
            raise ValueError(f"No API key provided for {self.config.provider}")

        if self.config.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI library not installed")
            self._client = openai.OpenAI(api_key=self.config.api_key)
            return self._client

        elif self.config.provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic library not installed")
            self._client = anthropic.Anthropic(api_key=self.config.api_key)
            return self._client

        raise ValueError(f"Unsupported provider: {self.config.provider}")

    def _format_prompt(self, context: Dict[str, Any]) -> str:
        """
        Format prompt template with context variables.

        Args:
            context: Workflow context with variables

        Returns:
            Formatted prompt string
        """
        try:
            # Simple string formatting
            return self.prompt_template.format(**context)
        except KeyError as e:
            raise ValueError(f"Missing context variable in prompt: {e}")

    def _execute_openai(self, prompt: str) -> str:
        """Execute prompt with OpenAI"""
        client = self._get_client()

        response = client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            timeout=self.config.timeout
        )

        return response.choices[0].message.content

    def _execute_anthropic(self, prompt: str) -> str:
        """Execute prompt with Anthropic Claude"""
        client = self._get_client()

        response = client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def execute(self, context: Dict[str, Any]) -> StepResult:
        """
        Execute this LLM action.

        Args:
            context: Workflow context

        Returns:
            StepResult with LLM response
        """
        start_time = time.time()

        try:
            # Format prompt with context
            formatted_prompt = self._format_prompt(context)

            # Execute with appropriate provider
            if self.config.provider == "openai":
                output = self._execute_openai(formatted_prompt)
            elif self.config.provider == "anthropic":
                output = self._execute_anthropic(formatted_prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")

            execution_time = time.time() - start_time

            return StepResult(
                success=True,
                output=output,
                execution_time=execution_time,
                metadata={
                    "provider": self.config.provider,
                    "model": self.config.model,
                    "prompt_tokens": len(formatted_prompt.split()),
                    "output_tokens": len(output.split())
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
        """Validate LLM action configuration"""
        if not super().validate():
            return False

        if not self.prompt_template:
            return False

        return bool(self.config.api_key or self._get_api_key())