"""PromptQueueFile parser: ordered prompt queue from fenced markdown (LANAACPB-SP01 FR-12, IP01 IS-14).

Format (authority: docs/PROMPT_FILE_FORMAT.md - keep in sync):
- first non-empty line MUST open a fence: 3..9 backticks, optional info string (ignored)
- a prompt closes at the next line of >= N backticks (CommonMark fence semantics)
- consecutive prompts are separated by one '---' line; commentary is allowed only between
  the separator and the next opening fence and is never returned
"""
import re

FENCE_MIN, FENCE_MAX = 3, 9
OPENING_FENCE = re.compile(r"^(`{3,})([^`]*)$")  # backticks + optional info string
SEPARATOR = "---"


class PromptQueueError(Exception):
  """Malformed PromptQueueFile - the message names the violated rule (EC-25)."""


def parse_queue(text: str) -> list[str]:
  prompts: list[str] = []
  state = "expect_first_fence"  # -> in_prompt -> expect_separator -> expect_next_fence -> in_prompt ...
  fence_length = 0
  body: list[str] = []
  for position, line in enumerate(text.splitlines(), 1):
    stripped = line.rstrip()
    if state in ("expect_first_fence", "expect_next_fence"):
      if not stripped: continue
      match = OPENING_FENCE.match(stripped)
      if match is None:
        if state == "expect_first_fence":
          raise PromptQueueError(f"line {position}: the file must start with an opening fence of {FENCE_MIN}-{FENCE_MAX} backticks (found other content first)")
        continue  # commentary between '---' and the next opening fence
      if len(match.group(1)) > FENCE_MAX:
        raise PromptQueueError(f"line {position}: opening fence has {len(match.group(1))} backticks - the maximum is {FENCE_MAX}")
      fence_length = len(match.group(1))
      body = []
      state = "in_prompt"
    elif state == "in_prompt":
      if re.fullmatch("`{%d,}" % fence_length, stripped):  # closing fence: >= N backticks, nothing else
        prompts.append("\n".join(body).strip())
        state = "expect_separator"
      else:
        body.append(line)
    elif state == "expect_separator":
      if not stripped: continue
      if stripped != SEPARATOR:
        raise PromptQueueError(f"line {position}: expected a '---' separator between prompts (found other content after a closing fence)")
      state = "expect_next_fence"
  if state == "in_prompt":
    raise PromptQueueError(f"unclosed fence: the prompt opened with {fence_length} backticks is never closed")
  if state == "expect_next_fence":
    raise PromptQueueError("trailing '---' separator without a following prompt")
  if not prompts:
    raise PromptQueueError("the file contains zero prompts - at least one fenced prompt is required")
  return prompts
