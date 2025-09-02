import os
from pathlib import Path
from typing import Optional, TypedDict
import logging

logger = logging.getLogger(__name__)
def _get_first_env(names, default_value=""):
    """
    Return the first non-empty environment variable from the list of names.
    """
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return default_value
