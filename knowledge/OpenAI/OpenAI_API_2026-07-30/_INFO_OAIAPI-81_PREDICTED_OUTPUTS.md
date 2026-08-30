# Predicted Outputs

**Doc ID**: OAIAPI-IN81
**Goal**: Document Predicted Outputs latency optimization feature
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Predicted Outputs is a latency optimization feature that speeds up model responses when most of the output is known in advance (e.g., code editing, document revision). By providing a prediction of the expected output, the API can skip generating tokens that match the prediction, significantly reducing latency. Supported in Chat Completions and Responses API. Useful for code refactoring, template-based generation, and iterative editing where the output is similar to a known baseline. [VERIFIED] (OAIAPI-SC-OAI-GPROUT)

## REST API

### Chat Completions with Prediction

**Endpoint**: `POST /v1/chat/completions`

```json
{
  "model": "gpt-5.5",
  "messages": [
    {"role": "user", "content": "Add error handling to this function:\n```python\ndef fetch_data(url):\n    response = requests.get(url)\n    return response.json()\n```"}
  ],
  "prediction": {
    "type": "content",
    "content": "def fetch_data(url):\n    response = requests.get(url)\n    return response.json()"
  }
}
```

**Parameters**:

- **prediction** (object, optional)
  - **type** (string, required) - Always `"content"`
  - **content** (string, required) - Expected output text (the baseline prediction)

## SDK Examples (Python)

```python
from openai import OpenAI

client = OpenAI()

# Original code that needs modification
original_code = """def fetch_data(url):
    response = requests.get(url)
    return response.json()"""

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[
        {"role": "user", "content": f"Add try/except error handling:\n```python\n{original_code}\n```"}
    ],
    prediction={"type": "content", "content": original_code},
)
print(response.choices[0].message.content)
```

## Use Cases

- **Code refactoring**: Provide current code as prediction, ask for modifications
- **Document editing**: Provide current document, request specific changes
- **Template completion**: Provide template with known structure

## Limitations

- **Not all models**: Check model support documentation
- **Accuracy dependent**: Prediction must be close to actual output for latency savings
- **No streaming benefit**: Latency savings mainly visible in TTFT (time to first token)

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

- OAIAPI-SC-OAI-GPROUT - Predicted Outputs guide (https://developers.openai.com/api/docs/guides/predicted-outputs)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 13:00]**
- Initial documentation (gap found during /improve review)
