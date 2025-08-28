"""Utility functions for environment management."""
import os
from dotenv import load_dotenv

def load_env_file(filename: str, base_dir: str):
    """
    Load a .env file safely. Raise an error if the file is missing.
    """
    path = os.path.join(base_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"❌ Required environment file not found: {path}\n"
            f"Make sure {filename} exists in {base_dir}"
        )
    load_dotenv(path)
    return path
