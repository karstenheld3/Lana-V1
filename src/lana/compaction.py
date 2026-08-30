"""Checkpoint compaction: usage-anchored projection, one Summarizer call, deterministic todo splice (LANAAGNT-FR-07, IS-17).

IG-04: the todo state is extracted deterministically and spliced byte-verbatim - the Summarizer NEVER touches it.
Fail-safe: on any Summarizer failure no truncation happens - warn and continue uncompacted (EC-17).
"""
import json
from typing import AsyncIterator, Optional
from lana.config import AppConfig
from lana.events import CheckpointCreated, ErrorEvent
from lana.models import Message
from lana.providers import get_adapter

KEEP_TAIL_MESSAGES = 6

CHECKPOINT_HEADER = "The following is a summary of important context from your previous session.\n{{ CHECKPOINT 1 }}"
ANCHOR_TODO_TITLE = "# Current working TODO list (keep this up to date with todo_list tool):"
ANCHOR_TODO_FOOTER = "Make sure to continue working off of this TODO list"
ANCHOR_NO_ACK = "DO NOT ACKNOWLEDGE THIS CHECKPOINT MESSAGE."

SUMMARIZER_SYSTEM = "You are a conversation summarizer. Produce exactly three labeled Markdown sections: '# Objective:', '# Session Summary:', '# Code Interaction Summary:'. Be factual and concise; never invent content."


# Usage-anchored projection: last provider-reported input count + chars/4 of content added since (FR-07, RF-05)
def projected_tokens(anchor_tokens: int, chars_since_anchor: int) -> int:
  return anchor_tokens + chars_since_anchor // 4


def compaction_threshold(app: AppConfig) -> int:
  generator = app.roles["generator"]
  return min(int(app.lana.compaction_threshold_fraction * generator.max_input), app.lana.compaction_threshold_max_tokens)


# Anchor = usage of the last assistant message carrying usage; delta = chars of messages after it
def project_from_messages(messages: list[Message]) -> int:
  anchor_tokens, anchor_index = 0, -1
  for index, message in enumerate(messages):
    if message.role == "assistant" and message.usage is not None: anchor_tokens, anchor_index = message.usage.input_tokens + message.usage.output_tokens, index
  chars_since = sum(len(message.content) for message in messages[anchor_index + 1:])
  return projected_tokens(anchor_tokens, chars_since)


# Deterministic extraction: byte-verbatim JSON of the last todo state (IG-04)
def extract_todo_json(todo_state: Optional[list[dict]]) -> Optional[str]:
  if not todo_state: return None
  return json.dumps(todo_state, indent=2, ensure_ascii=False, sort_keys=True)


def build_checkpoint(objective: str, summary: str, code_history: str, todo_json: Optional[str]) -> str:
  parts = [CHECKPOINT_HEADER, "# Objective:", objective.strip()]
  if todo_json is not None: parts += [ANCHOR_TODO_TITLE, todo_json, ANCHOR_TODO_FOOTER]  # EC-12: omitted when no todo state
  parts += ["# Session Summary:", summary.strip(), "# Code Interaction Summary:", code_history.strip(), ANCHOR_NO_ACK]
  return "\n".join(parts)


def split_sections(text: str) -> tuple[str, str, str]:
  sections = {"objective": "", "session summary": "", "code interaction summary": ""}
  current = None
  for line in text.splitlines():
    lowered = line.strip().lstrip("#").strip().rstrip(":").lower()
    if lowered in sections: current = lowered; continue
    if current: sections[current] += line + "\n"
  if not any(sections.values()): sections["session summary"] = text  # lenient fallback
  return sections["objective"], sections["session summary"], sections["code interaction summary"]


def render_transcript(messages: list[Message], limit_chars: int = 100000) -> str:
  lines = []
  for message in messages:
    prefix = message.role.upper()
    lines.append(f"[{prefix}] {message.content[:2000]}")
    for call in message.tool_calls: lines.append(f"  [TOOL_CALL] {call.name} {call.args_json[:300]} -> {str(call.result)[:300]}")
  text = "\n".join(lines)
  return text[-limit_chars:]


async def run_summarizer(agent) -> str:
  role = agent.app.roles["summarizer"]
  adapter = get_adapter(role, agent.app)
  request = Message(role="user", content=f"Summarize this agent conversation into the three required sections.\n\nTranscript:\n{render_transcript(agent.messages)}")
  parts = []
  usage = None
  async for delta in adapter.stream_turn(SUMMARIZER_SYSTEM, [], [request], role):
    if delta.kind == "text": parts.append(delta.text)
    elif delta.kind == "usage": usage = delta.usage
  if usage is not None and agent.cost_fn: agent.cost_fn("summarizer", usage)
  return "".join(parts)


# Post-turn compaction hook wired into Agent (async generator over events)
def make_compactor(app: AppConfig):
  async def compact(agent) -> AsyncIterator:
    threshold = compaction_threshold(app)
    projected = project_from_messages(agent.messages)
    if projected < threshold: return
    yield ErrorEvent(message=f"NOTICE: Compacting context (~{projected} tokens, threshold {threshold})...")  # FR-16 UX-04: announce BEFORE the paid call
    try:
      summary_text = await run_summarizer(agent)
    except Exception as error:  # EC-17: fail-safe, no truncation
      yield ErrorEvent(message=f"WARNING: Summarizer call failed ({error}). Continuing uncompacted - next turn may be expensive.")
      return
    try:  # FR-16 CR-04: the whole compact body shares the EC-17 warn-and-continue semantics
      objective, summary, code_history = split_sections(summary_text)
      todo_json = extract_todo_json(agent.tool_context.todo_state)
      checkpoint_text = build_checkpoint(objective, summary, code_history, todo_json)
      tail = agent.messages[-KEEP_TAIL_MESSAGES:] if len(agent.messages) > KEEP_TAIL_MESSAGES else list(agent.messages)
      while tail and tail[0].role == "tool": tail = tail[1:]  # never keep a tool result whose tool_use partner was truncated (provider 400 guard)
      truncated_count = len(agent.messages) - len(tail)
      agent.messages = [Message(role="user", content=checkpoint_text)] + tail
    except Exception as error:
      yield ErrorEvent(message=f"WARNING: Compaction failed after the Summarizer call ({type(error).__name__}: {error}). Continuing uncompacted - next turn may be expensive.")
      return
    yield CheckpointCreated(text=checkpoint_text, truncated_messages=truncated_count, kept_messages=len(tail))
  return compact
