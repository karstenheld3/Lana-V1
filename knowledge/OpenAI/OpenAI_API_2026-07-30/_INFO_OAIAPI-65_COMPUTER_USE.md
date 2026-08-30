# Computer Use (CUA)

**Doc ID**: OAIAPI-IN65
**Goal**: Document the computer_use tool for UI-based agent automation - screenshots, clicks, typing, scrolling
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Computer Use Agent (CUA) enables models to operate software through the user interface. The `computer_use` tool in the Responses API lets models inspect screenshots and return interface actions (click, type, scroll, keypress, etc.) for the developer's code to execute. The model receives a screenshot, analyzes visible UI elements, and returns the next action. The developer executes the action on the target environment and sends back a new screenshot. Loop continues until task is complete. Built-in `computer_use` tool in GPT-5.4/5.5 replaces deprecated `computer-use-preview`. [VERIFIED] (OAIAPI-SC-OAI-GCUA, OAIAPI-SC-OAI-GCMPTU)

## Key Facts

- **Tool type**: `computer_use` in Responses API [VERIFIED] (OAIAPI-SC-OAI-GCUA)
- **Models**: GPT-5.4, GPT-5.5 (built-in); computer-use-preview deprecated [VERIFIED] (OAIAPI-SC-OAI-GCMPTU)
- **Loop pattern**: Screenshot -> model analyzes -> returns action -> execute -> screenshot [VERIFIED] (OAIAPI-SC-OAI-GCUA)
- **Actions**: click, type, scroll, keypress, drag, double_click, screenshot [VERIFIED] (OAIAPI-SC-OAI-GCUA)
- **Display config**: Must specify width and height for coordinate system [VERIFIED] (OAIAPI-SC-OAI-GCUA)
- **GPT-5.4-nano**: Does NOT support computer use [VERIFIED] (OAIAPI-SC-OAI-GCHLOG)

## Use Cases

- **UI testing**: Automated visual testing of web/desktop applications
- **Data entry**: Fill forms across applications that lack APIs
- **Process automation**: Automate multi-step workflows in legacy systems
- **Web scraping**: Navigate dynamic sites with JS rendering
- **Application monitoring**: Check UI state and capture screenshots

## Action Types

- **click**: Click at coordinates (x, y). Options: left/right/middle button
- **double_click**: Double-click at coordinates
- **type**: Type text string
- **keypress**: Press key combination (e.g., "ctrl+c", "enter")
- **scroll**: Scroll at coordinates (x, y) with direction (up/down/left/right)
- **drag**: Drag from (x1, y1) to (x2, y2)
- **screenshot**: Request a new screenshot (no action, just observe)
- **wait**: Wait for specified duration

## CUA Loop Pattern

```
1. Send task + initial screenshot to model
2. Model returns computer_use action (e.g., click at 640,360)
3. Execute action on environment
4. Capture new screenshot
5. Send screenshot back to model
6. Model returns next action or final response
7. Repeat 3-6 until task complete
```

## SDK Examples (Python)

### Basic CUA

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Open the settings app and change the display brightness to 50%.",
    tools=[{
        "type": "computer_use",
        "display_width": 1920,
        "display_height": 1080,
    }],
)

for item in response.output:
    if item.type == "computer_call":
        action = item.action
        print(f"Action: {action.type}")
        if hasattr(action, 'x'):
            print(f"  Coordinates: ({action.x}, {action.y})")
        if hasattr(action, 'text'):
            print(f"  Text: {action.text}")
```

### Full CUA Loop

```python
from openai import OpenAI
import base64
import time

client = OpenAI()

class CUAAgent:
    """Computer Use Agent with loop execution"""
    
    def __init__(self, environment="browser", width=1280, height=720, max_steps=20):
        self.environment = environment
        self.width = width
        self.height = height
        self.max_steps = max_steps
    
    def run(self, task: str, screenshot_provider, action_executor):
        """
        Execute CUA task.
        screenshot_provider: callable returning screenshot bytes
        action_executor: callable(action) that executes the action
        """
        screenshot = screenshot_provider()
        screenshot_b64 = base64.b64encode(screenshot).decode()
        
        input_messages = [
            {
                "type": "message",
                "role": "user",
                "content": [
                    {"type": "text", "text": task},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{screenshot_b64}"
                        }
                    }
                ]
            }
        ]
        
        for step in range(self.max_steps):
            response = client.responses.create(
                model="gpt-5.6-sol",
                tools=[{
                    "type": "computer_use",
                    "display_width": self.width,
                    "display_height": self.height,
                    "environment": self.environment
                }],
                input=input_messages
            )
            
            computer_calls = [o for o in response.output if o.type == "computer_call"]
            
            if not computer_calls:
                print(f"Task complete after {step + 1} steps")
                return response.output_text
            
            for call in computer_calls:
                action = call.action
                print(f"Step {step + 1}: {action.type}", end="")
                if hasattr(action, 'x'):
                    print(f" at ({action.x}, {action.y})", end="")
                print()
                
                action_executor(action)
                time.sleep(0.5)
            
            screenshot = screenshot_provider()
            screenshot_b64 = base64.b64encode(screenshot).decode()
            
            input_messages = [{
                "type": "computer_call_output",
                "call_id": computer_calls[-1].call_id,
                "output": {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{screenshot_b64}"
                    }
                }
            }]
        
        print(f"Max steps ({self.max_steps}) reached")
        return None
```

## Error Responses

- **400 Bad Request** - Invalid display dimensions or action type
- **422 Unprocessable Entity** - Screenshot not provided when expected
- **429 Too Many Requests** - Rate limit exceeded

## Differences from Other APIs

- **vs Anthropic Computer Use**: Very similar concept. Anthropic launched computer use first (2024). Different action format but same loop pattern
- **vs Gemini**: No equivalent computer use tool
- **vs Playwright/Selenium**: CUA uses visual understanding; Playwright uses DOM selectors. CUA works on any visual interface

## Limitations and Known Issues

- **Coordinate accuracy**: Model may occasionally click wrong coordinates [VERIFIED] (OAIAPI-SC-OAI-GCUA)
- **Speed**: Each step requires model inference + screenshot capture [VERIFIED] (OAIAPI-SC-OAI-GCUA)
- **No direct DOM access**: Works purely from screenshots, no HTML inspection [VERIFIED] (OAIAPI-SC-OAI-GCUA)

## Gotchas and Quirks

- **computer-use-preview deprecated**: Use built-in tool in GPT-5.4/5.5 instead [VERIFIED] (OAIAPI-SC-OAI-GCMPTU)
- **Display dimensions must match**: Specified width/height must match actual screenshot dimensions [VERIFIED] (OAIAPI-SC-OAI-GCUA)
- **Wait after actions**: UI may need time to update after action execution [VERIFIED] (OAIAPI-SC-OAI-GCUA)
- **Max steps**: Always set a max step limit to prevent infinite loops [VERIFIED] (OAIAPI-SC-OAI-GCUA)
- **Sandbox recommended**: Run in containers for safety [VERIFIED] (OAIAPI-SC-OAI-GCUA)

## TypeScript Examples

### Basic Response

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Explain this concept briefly.",
});

console.log(response.output_text);
```

### With Instructions

```typescript
const response = await client.responses.create({
  model: "gpt-4o-mini",
  instructions: "You are a helpful assistant.",
  input: "What is 2+2?",
});

console.log(response.output_text);
```

## Sources

- OAIAPI-SC-OAI-GCUA - Computer Use Guide
- OAIAPI-SC-OAI-GCMPTU - Computer Use Tool Reference
- OAIAPI-SC-OAI-GCHLOG - Changelog

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 17:50]**
- Enriched from 2026-03-20 IN65 (46 -> 230 lines)
- Updated model refs to GPT-5.5, computer-use-preview deprecation

**[2026-05-22 11:30]**
- Stub created
