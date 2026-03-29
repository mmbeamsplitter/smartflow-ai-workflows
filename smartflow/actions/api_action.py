"""
API Action - Execute HTTP API calls
"""

import time
import json
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from ..core.step import Step, StepResult


@dataclass
class APIConfig:
    """Configuration for API actions"""
    base_url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    timeout: float = 30.0
    verify_ssl: bool = True
    default_method: str = "GET"


class APIAction(Step):
    """
    Execute HTTP API operations for integrating with external services.
    Supports GET, POST, PUT, DELETE methods.
    """

    def __init__(
        self,
        name: str,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        config: Optional[APIConfig] = None,
        description: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize an API action.

        Args:
            name: Action name
            endpoint: API endpoint URL or path (can use {variable} placeholders)
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            params: URL query parameters (can use {variable} placeholders)
            data: Request body for POST/PUT/PATCH (can use {variable} placeholders)
            headers: HTTP headers (can use {variable} placeholders)
            config: API configuration options
            description: Optional description
            **kwargs: Additional Step parameters
        """
        super().__init__(name, description, **kwargs)
        self.endpoint_template = endpoint
        self.method = method.upper()
        self.params_template = params or {}
        self.data_template = data
        self.headers_template = headers or {}
        self.config = config or APIConfig()
        self.config.default_method = self.method

    def _format_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """
        Format a template value with context variables.

        Args:
            value: Template value (string with placeholders)
            context: Workflow context

        Returns:
            Formatted value
        """
        if value is None:
            return None

        if isinstance(value, str):
            try:
                return value.format(**context)
            except (KeyError, ValueError):
                # If formatting fails, return original
                return value

        if isinstance(value, dict):
            return {k: self._format_value(v, context) for k, v in value.items()}

        if isinstance(value, list):
            return [self._format_value(v, context) for v in value]

        return value

    def _build_url(self, context: Dict[str, Any]) -> str:
        """Build full URL from endpoint and config"""
        endpoint = self._format_value(self.endpoint_template, context)

        if self.config.base_url:
            return f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        return endpoint

    def _build_headers(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Build request headers with defaults and user headers"""
        headers = {}

        # Add content-type for JSON data
        if self.data_template and "Content-Type" not in self.headers_template:
            if "Content-Type" not in (self.config.headers or {}):
                headers["Content-Type"] = "application/json"

        # Add config headers if present
        if self.config.headers:
            headers.update(self.config.headers)

        # Add action headers
        user_headers = self._format_value(self.headers_template, context)
        if user_headers:
            headers.update(user_headers)

        return headers

    def _build_params(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build query parameters"""
        return self._format_value(self.params_template, context)

    def _build_body(self, context: Dict[str, Any]) -> Optional[Union[Dict, str]]:
        """Build request body"""
        data = self._format_value(self.data_template, context)

        # Convert dict to JSON if content-type is JSON
        if isinstance(data, dict):
            headers = self._build_headers(context)
            content_type = headers.get("Content-Type", "").lower()

            if "application/json" in content_type:
                return json.dumps(data)

        return data

    def execute(self, context: Dict[str, Any]) -> StepResult:
        """
        Execute this API action.

        Args:
            context: Workflow context

        Returns:
            StepResult with API response data
        """
        if not REQUESTS_AVAILABLE:
            return StepResult(
                success=False,
                output=None,
                error="requests library not installed"
            )

        start_time = time.time()

        try:
            # Build request components
            url = self._build_url(context)
            headers = self._build_headers(context)
            params = self._build_params(context)
            body = self._build_body(context)

            # Execute request
            response = requests.request(
                method=self.method,
                url=url,
                headers=headers,
                params=params,
                data=body,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )

            execution_time = time.time() - start_time

            # Parse response
            try:
                response_data = response.json()
            except (json.JSONDecodeError, ValueError):
                response_data = response.text

            success = response.status_code < 400

            return StepResult(
                success=success,
                output={
                    "status_code": response.status_code,
                    "data": response_data,
                    "headers": dict(response.headers)
                },
                error=response.text if not success else None,
                execution_time=execution_time,
                metadata={
                    "url": url,
                    "method": self.method,
                    "status": response.status_code
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
        """Validate API action configuration"""
        if not super().validate():
            return False

        if not self.endpoint_template:
            return False

        if REQUESTS_AVAILABLE:
            return True

        return False