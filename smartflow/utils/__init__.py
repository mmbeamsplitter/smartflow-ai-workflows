"""
Utility functions for SmartFlow
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Optional path to config file (defaults to config.yaml)

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        # Check common config locations
        for path in ["config.yaml", "config.yml", ".smartflow/config.yaml", ".config/smartflow.yaml"]:
            if Path(path).exists():
                config_path = path
                break

    if config_path is None or not Path(config_path).exists():
        return {}

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def expand_env_vars(value: Any) -> Any:
    """
    Expand environment variables in configuration values.

    Args:
        value: Configuration value (may contain ${VAR} placeholders)

    Returns:
        Value with environment variables expanded
    """
    if isinstance(value, str):
        # Expand ${VAR} and $VAR patterns
        return os.path.expandvars(value.replace("${", "$").replace("}", ""))

    if isinstance(value, dict):
        return {k: expand_env_vars(v) for k, v in value.items()}

    if isinstance(value, list):
        return [expand_env_vars(v) for v in value]

    return value


def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable with optional default.

    Args:
        name: Environment variable name
        default: Optional default value

    Returns:
        Environment variable value or default
    """
    return os.getenv(name, default)


def validate_secrets(config: Dict[str, Any]) -> Dict[str, bool]:
    """
    Validate that required secrets are present.

    Args:
        config: Configuration dictionary

    Returns:
        Dictionary of secret presence status
    """
    secrets = {
        "openai_api_key": "OPENAI_API_KEY" in os.environ or "openai.api_key" in str(config.get("llm", {})),
        "anthropic_api_key": "ANTHROPIC_API_KEY" in os.environ or "anthropic.api_key" in str(config.get("llm", {})),
    }

    return secrets


def safe_load_json(path: str) -> Optional[Dict[str, Any]]:
    """
    Safely load JSON from file.

    Args:
        path: Path to JSON file

    Returns:
        Parsed JSON or None if error
    """
    try:
        import json
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return None