"""Shared utilities for ACP Python SDK verification tests.

ACP is a protocol specification, not a hosted API. These tests verify
that the SDK can be imported, schema models instantiate correctly, and
helper builders produce valid protocol messages. No API keys or network
access required (unlike traditional API SDK tests).
"""
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class TestResult:
    name: str
    status: str  # "pass", "fail", "skip"
    duration_ms: float = 0.0
    detail: str = ""
    error: str = ""

@dataclass
class TestSuite:
    name: str
    results: list[TestResult] = field(default_factory=list)

    def run_test(self, name: str, fn, *, skip_reason: str = ""):
        if skip_reason:
            self.results.append(TestResult(name=name, status="skip", detail=skip_reason))
            print(f"  SKIP  {name}: {skip_reason}")
            return
        t0 = time.perf_counter()
        try:
            detail = fn()
            dur = (time.perf_counter() - t0) * 1000
            self.results.append(TestResult(name=name, status="pass", duration_ms=dur, detail=str(detail or "")))
            print(f"  PASS  {name} ({dur:.0f}ms)")
        except Exception as exc:
            dur = (time.perf_counter() - t0) * 1000
            self.results.append(TestResult(name=name, status="fail", duration_ms=dur, error=str(exc)))
            print(f"  FAIL  {name}: {exc}")

    def summary(self) -> dict:
        passed = sum(1 for r in self.results if r.status == "pass")
        failed = sum(1 for r in self.results if r.status == "fail")
        skipped = sum(1 for r in self.results if r.status == "skip")
        return {
            "suite": self.name,
            "total": len(self.results),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "duration_ms": round(r.duration_ms, 1),
                    "detail": r.detail,
                    "error": r.error,
                }
                for r in self.results
            ],
        }

    def save(self, path: Path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.summary(), f, indent=2, ensure_ascii=False)

    def print_summary(self):
        s = self.summary()
        print(f"\n{'='*60}")
        print(f"{s['suite']}: {s['passed']} passed, {s['failed']} failed, {s['skipped']} skipped ({s['total']} total)")
        print(f"{'='*60}")
        return s["failed"]
