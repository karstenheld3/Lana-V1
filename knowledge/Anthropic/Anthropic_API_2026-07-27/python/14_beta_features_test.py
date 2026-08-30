"""IN12, IN25, IN26, IN30, IN31, IN40, IN47, IN49: Beta/special features.
Most require beta access or special environments. Documented as stubs.
"""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _lib import test, finish

test("Batches API (IN12)", lambda: None,
   skip="Creates billable batch job; test manually with: client.batches.create()")

test("Code execution tool (IN25)", lambda: None,
   skip="Requires code_execution_20250522 beta and sandbox container")

test("Computer use tool (IN26)", lambda: None,
   skip="Requires computer_use_20250124 beta and desktop environment")

test("Files API upload (IN30)", lambda: None,
   skip="Requires files beta; endpoint: POST /v1/files")

test("Files API list (IN30)", lambda: None,
   skip="Requires files beta; endpoint: GET /v1/files")

test("Skills API (IN31)", lambda: None,
   skip="Requires skills beta; endpoint: POST /v1/skills")

test("Managed Agents (IN40)", lambda: None,
   skip="Requires agents beta; endpoint: POST /v1/agents")

test("Refusals/fallbacks (IN47)", lambda: None,
   skip="Cannot reliably trigger refusal; server-side-fallback-2026-07-01 beta")

test("Agent Memory Stores (IN49)", lambda: None,
   skip="Requires memory stores beta; endpoint: POST /v1/memory_stores")

finish(__file__)
