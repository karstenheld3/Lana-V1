"""ACP frontend package: JSON-RPC 2.0 over stdio per LANAACPB-SP01 (protocol v1)."""
import datetime, sys


# App-Level logging: stderr only, one timestamped line per key operation (SP01 section 11, IG-01)
def log(text: str) -> None:
  print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {text}", file=sys.stderr, flush=True)
