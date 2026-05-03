"""
Common utilities for analysis and reporting.
"""
import os
import sys
from typing import Optional, Any
from datetime import datetime


def get_system_info() -> dict:
    """Get system and environment information."""
    import platform
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": platform.python_version(),
        "cpu": platform.processor() or "Unknown",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def format_number(value: Optional[float], precision: int = 4) -> str:
    """Format a number with fixed precision."""
    if value is None:
        return "N/A"
    try:
        return f"{value:.{precision}f}"
    except:
        return str(value)


def format_percent(value: Optional[float], precision: int = 2) -> str:
    """Format a percentage."""
    if value is None:
        return "N/A"
    try:
        return f"{value * 100:.{precision}f}%"
    except:
        return str(value)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division that handles zero denominator."""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except:
        return default


def get_file_modification_time(filepath: str) -> Optional[str]:
    """Get the last modification time of a file."""
    try:
        import os
        timestamp = os.path.getmtime(filepath)
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return None


def truncate_string(text: str, max_length: int = 50) -> str:
    """Truncate a string to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def safe_import(module_name: str, alias: Optional[str] = None) -> Optional[Any]:
    """Safely import a module."""
    try:
        if alias:
            exec(f"import {module_name} as {alias}")
            return eval(alias)
        else:
            exec(f"import {module_name}")
            return eval(module_name)
    except:
        return None
