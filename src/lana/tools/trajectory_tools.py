"""trajectory_search executor: lexical search over session JSONL files (LANAAGNT-FR-15, IS-23, DD-21).

Lana's session files ARE the trajectories. Scoring is case-insensitive query-term overlap
per event chunk, sorted descending (stable by position); empty query returns all chunks
chronologically; maximum 50 chunks per the verbatim tool contract.
"""
from pathlib import Path
from lana.events import from_jsonl
from lana.tools import ToolContext, ToolError

CHUNK_CAP = 50
EXCERPT_CHARS = 200
LISTED_SESSIONS_CAP = 10


def sessions_directory(context: ToolContext) -> Path:
  return Path(context.workspace) / ".lana" / "sessions"


# Resolve ID against session files: exact filename, stem, or unique prefix (EC-27 on failure)
def resolve_session_file(session_id: str, context: ToolContext) -> Path:
  directory = sessions_directory(context)
  if not directory.is_dir(): raise ToolError(f"No sessions folder at '{directory}' - no trajectories exist in this workspace yet.")
  candidates = sorted(directory.glob("*.jsonl"))
  if not candidates: raise ToolError(f"No session files in '{directory}' - no trajectories exist in this workspace yet.")
  for candidate in candidates:
    if session_id in (candidate.name, candidate.stem): return candidate
  prefix_matches = [candidate for candidate in candidates if candidate.name.startswith(session_id)]
  if len(prefix_matches) == 1: return prefix_matches[0]
  available = ", ".join(candidate.stem for candidate in candidates[-LISTED_SESSIONS_CAP:])
  if len(prefix_matches) > 1: raise ToolError(f"Trajectory ID '{session_id}' is ambiguous ({len(prefix_matches)} matches). Use a longer prefix. Available: {available}")
  raise ToolError(f"Unknown trajectory ID '{session_id}'. Available session ids (newest {LISTED_SESSIONS_CAP}): {available}")


# One chunk per event line: "[NNN] compact-json-without-ts" truncated to EXCERPT_CHARS
def render_chunks(session_file: Path) -> list[str]:
  chunks = []
  for index, line in enumerate(session_file.read_text(encoding="utf-8").splitlines(), start=1):
    if not line.strip(): continue
    try:
      event = from_jsonl(line)
      payload = event.to_jsonl()
    except Exception:
      payload = line  # corrupt line still searchable as raw text
    excerpt = payload[:EXCERPT_CHARS] + ("..." if len(payload) > EXCERPT_CHARS else "")
    chunks.append(f"[{index:03d}] {excerpt}")
  return chunks


def score_chunk(chunk: str, query_terms: list[str]) -> int:
  lowered = chunk.casefold()
  return sum(1 for term in query_terms if term in lowered)


def execute_trajectory_search(args: dict, context: ToolContext) -> str:
  if args["SearchType"] == "user": raise ToolError("SearchType 'user' is not supported - Lana has no user-activity index. The tool contract already forbids calling with SearchType 'user' (FR-15).")
  session_file = resolve_session_file(args["ID"], context)
  chunks = render_chunks(session_file)
  query_terms = [term for term in args["Query"].casefold().split() if term]
  if not query_terms:
    selected = chunks[:CHUNK_CAP]  # contract: empty query returns all trajectory steps (chronological, capped)
    ranking_note = "chronological (empty query)"
  else:
    scored = [(score_chunk(chunk, query_terms), index, chunk) for index, chunk in enumerate(chunks)]
    matching = [(score, index, chunk) for score, index, chunk in scored if score > 0]
    matching.sort(key=lambda entry: (-entry[0], entry[1]))  # score descending, stable by position
    selected = [chunk for _, _, chunk in matching[:CHUNK_CAP]]
    ranking_note = f"scored by term overlap, query terms: {len(query_terms)}"
  if not selected: return f"Trajectory '{session_file.stem}': no chunks match the query ({len(chunks)} chunks total)."
  header = f"Trajectory '{session_file.stem}': {len(selected)} of {len(chunks)} chunks ({ranking_note}, cap {CHUNK_CAP}):\n"
  return header + "\n".join(selected)
