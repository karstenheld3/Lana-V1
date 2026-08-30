"""Shared test infrastructure for OpenAI API documentation verification.

SDK version: openai 2.45.0
API key source: e:\\Dev\\.tools\\.api-keys.txt
"""

import json
import os
import sys
import time
from pathlib import Path

# Load API keys from .api-keys.txt
API_KEYS_PATH = Path(r"e:\Dev\.tools\.api-keys.txt")


def load_api_keys():
    """Load API keys from the shared keys file."""
    keys = {}
    if API_KEYS_PATH.exists():
        for line in API_KEYS_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                keys[key.strip()] = value.strip()
    return keys


def get_client():
    """Create an OpenAI client with API key from .api-keys.txt."""
    from openai import OpenAI

    keys = load_api_keys()
    api_key = keys.get("OPENAI_API_KEY")
    org = keys.get("OPENAI_ORGANIZATION")
    if not api_key:
        raise RuntimeError(f"OPENAI_API_KEY not found in {API_KEYS_PATH}")
    return OpenAI(api_key=api_key, organization=org)


def get_async_client():
    """Create an async OpenAI client."""
    from openai import AsyncOpenAI

    keys = load_api_keys()
    api_key = keys.get("OPENAI_API_KEY")
    org = keys.get("OPENAI_ORGANIZATION")
    if not api_key:
        raise RuntimeError(f"OPENAI_API_KEY not found in {API_KEYS_PATH}")
    return AsyncOpenAI(api_key=api_key, organization=org)


class TestResult:
    """Track individual test results."""

    def __init__(self, name: str, topic: str):
        self.name = name
        self.topic = topic
        self.status = "pending"  # passed, failed, skipped, error
        self.duration_ms = 0
        self.error = None
        self.details = None
        self._start = None

    def start(self):
        self._start = time.time()

    def passed(self, details=None):
        self.status = "passed"
        self.duration_ms = int((time.time() - self._start) * 1000) if self._start else 0
        self.details = details

    def failed(self, error: str, details=None):
        self.status = "failed"
        self.duration_ms = int((time.time() - self._start) * 1000) if self._start else 0
        self.error = error
        self.details = details

    def skipped(self, reason: str):
        self.status = "skipped"
        self.error = reason

    def to_dict(self):
        d = {
            "name": self.name,
            "topic": self.topic,
            "status": self.status,
            "duration_ms": self.duration_ms,
        }
        if self.error:
            d["error"] = self.error
        if self.details:
            d["details"] = self.details
        return d


class TestRunner:
    """Aggregate test results for a topic file."""

    def __init__(self, topic_id: str, description: str):
        self.topic_id = topic_id
        self.description = description
        self.results: list[TestResult] = []

    def add_test(self, name: str) -> TestResult:
        t = TestResult(name, self.topic_id)
        self.results.append(t)
        return t

    def summary(self):
        passed = sum(1 for r in self.results if r.status == "passed")
        failed = sum(1 for r in self.results if r.status == "failed")
        skipped = sum(1 for r in self.results if r.status == "skipped")
        errors = sum(1 for r in self.results if r.status == "error")
        return {
            "topic_id": self.topic_id,
            "description": self.description,
            "total": len(self.results),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "total_duration_ms": sum(r.duration_ms for r in self.results),
        }

    def save_results(self, output_path: Path):
        data = {
            "topic_id": self.topic_id,
            "description": self.description,
            "sdk_version": "openai 2.45.0",
            "summary": self.summary(),
            "tests": [r.to_dict() for r in self.results],
        }
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data


# Default model for tests (cost-efficient)
DEFAULT_MODEL = "gpt-4o-mini"
REASONING_MODEL = "o4-mini"
