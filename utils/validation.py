"""
Input validation and sanitization utilities
"""

from pathlib import Path
from typing import Optional
from .constants import MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH, MAX_INPUT_LENGTH


def validate_path(path: str) -> Path:
    """Validate and sanitize file system paths"""
    p = Path(path).resolve()
    if ".." in str(p):
        raise ValueError("Path traversal detected")
    return p


def validate_port(port: int) -> int:
    """Validate network port number"""
    if not (1024 <= port <= 65535):
        raise ValueError(f"Port must be between 1024 and 65535")
    return port


def validate_mod_id(mod_id: str) -> bool:
    """Check if mod ID is numeric"""
    return mod_id.strip().isdigit()


def sanitize_input(value: str, max_length: int = MAX_INPUT_LENGTH) -> str:
    """Remove dangerous characters and enforce length limit"""
    dangerous_chars = ['&', '|', ';', '$', '`', '\n', '\r', '<', '>', '"', "'"]
    for char in dangerous_chars:
        value = value.replace(char, '')
    return value.strip()[:max_length]


def validate_strong_password(password: str) -> bool:
    """Check password meets minimum requirements"""
    if len(password) < MIN_PASSWORD_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
        return False
    return bool(password.strip())


def input_int(prompt: str, default: Optional[int] = None) -> int:
    """Get validated integer input"""
    while True:
        try:
            value = input(prompt).strip()
            if not value and default is not None:
                return default
            return int(value)
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def input_float(prompt: str, default: Optional[float] = None) -> float:
    """Get validated float input"""
    while True:
        try:
            value = input(prompt).strip()
            if not value and default is not None:
                return default
            return float(value)
        except ValueError:
            print("Invalid input. Please enter a valid number.")