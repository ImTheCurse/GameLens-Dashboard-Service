from typing import List

from werkzeug.exceptions import BadRequest


def validate_data(required_keys: List[str], req_data):
    """
    Ensures all required keys exist in the request JSON.
    Uses Python sets for efficient comparison.
    """
    data = req_data or {}

    # Convert both to sets to use set math
    required_set = set(required_keys)
    provided_set = set(data.keys())

    # The '-' operator finds items in 'required' that are missing from 'provided'
    missing = required_set - provided_set

    if missing:
        raise BadRequest(f"Missing parameter(s): {', '.join(sorted(missing))}")
