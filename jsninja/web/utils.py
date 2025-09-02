"""Utility functions for the web interface."""
import hashlib
from typing import Dict, Any
from datetime import datetime, timedelta

from .config import RESULTS_EXPIRATION_SECONDS

# In-memory storage for scan results
results_store: Dict[str, Dict[str, Any]] = {}

def store_result(ip_address: str, result: Dict[str, Any]) -> str:
    """Store a scan result with IP address as key."""
    result_id = hashlib.sha256(f"{ip_address}:{datetime.now()}".encode()).hexdigest()
    results_store[result_id] = {
        "ip": ip_address,
        "result": result,
        "timestamp": datetime.now()
    }
    cleanup_old_results()
    return result_id

def get_result(result_id: str) -> Dict[str, Any]:
    """Retrieve a scan result by ID."""
    return results_store.get(result_id, {}).get("result", {})

def cleanup_old_results() -> None:
    """Remove expired results."""
    expiration = datetime.now() - timedelta(seconds=RESULTS_EXPIRATION_SECONDS)
    expired = [
        k for k, v in results_store.items()
        if v["timestamp"] < expiration
    ]
    for key in expired:
        results_store.pop(key, None)