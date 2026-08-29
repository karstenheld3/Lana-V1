"""ask_user_question executor: blocks on frontend answer via context callback (IS-10, FR-14 non-interactive fallback)."""
from lana.tools import ToolContext


def execute_ask_user_question(args: dict, context: ToolContext) -> str:
  ask_callback = getattr(context, "ask_user", None)
  if ask_callback is None: return "no answer (non-interactive session)"
  return ask_callback(args)
