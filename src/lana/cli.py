"""CLI entry point: arg parsing, startup sequence, REPL (IS-15, IS-21). Phase A stub - grows in Phase E."""
import argparse, sys


def build_arg_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(prog="lana", description="Lana MVP-1 - CLI agent running a prompt system (rules/workflows/skills) on OpenAI/Anthropic backends.")
  parser.add_argument("-p", "--prompt", help="headless mode: run this single prompt and exit (FR-14)")
  parser.add_argument("--output-format", choices=["text", "jsonl"], default="text", help="headless output: final text (default) or AgentEvent JSON Lines")
  parser.add_argument("--resume", metavar="SESSION_FILE", help="resume a session from its JSONL file")
  parser.add_argument("--config", metavar="PATH", help="config file override (env LANA_CONFIG)")
  parser.add_argument("--policy", choices=["manual", "auto", "turbo"], help="execution policy override")
  parser.add_argument("--debug", action="store_true", help="write redacted request/response JSON to .lana/logs/")
  return parser


def main() -> int:
  args = build_arg_parser().parse_args()
  print("Lana MVP-1 - implementation in progress (Phase A skeleton).")
  return 0


if __name__ == "__main__": sys.exit(main())
