# Graders API [ALPHA]

**Doc ID**: OAIAPI-IN31
**Goal**: Document the Graders API - run, validate grader definitions for evaluations and fine-tuning
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Graders API [ALPHA] provides endpoints to run and validate grader definitions for evaluations and reinforcement fine-tuning. Grader types: score (numeric 0-1), label (categorical pass/fail), string match (pattern matching), custom. Graders can use LLM-as-judge patterns. Two contexts: evaluations (measure performance) and RFT (reward signals). SDK v2.29.0 path: `client.fine_tuning.alpha.graders.run/validate`. Alpha status means API may change. [VERIFIED] (OAIAPI-SC-OAI-FTGRAD)

## Key Facts

- **Status**: ALPHA - API may change [VERIFIED]
- **Endpoints**: `POST /v1/graders/run`, `POST /v1/graders/validate` [VERIFIED]
- **Types**: Score (numeric), Label (categorical), String match, Custom [VERIFIED]
- **SDK path**: `client.fine_tuning.alpha.graders.*` (v2.29.0) [VERIFIED]
- **Param**: `model_sample` (not `model_input`/`model_output`) [VERIFIED]

## Grader Types

### Score Grader

```json
{
  "type": "score", "name": "accuracy_check", "model": "gpt-5.5",
  "input": "Rate factual accuracy from 0 to 1.", "pass_threshold": 0.7
}
```

### Label Grader

```json
{
  "type": "label", "name": "safety_check", "model": "gpt-5.5",
  "input": "Is this response safe? Reply 'pass' or 'fail'.",
  "labels": ["pass", "fail"], "pass_label": "pass"
}
```

### String Match Grader

```json
{"type": "string_match", "name": "exact_answer", "expected": "42", "case_sensitive": false}
```

## SDK Examples (Python)

### Run a Grader (SDK v2.29.0 verified)

```python
from openai import OpenAI

client = OpenAI()

result = client.fine_tuning.alpha.graders.run(
    grader={
        "type": "score", "name": "helpfulness", "model": "gpt-5.5",
        "input": "Rate helpfulness from 0 to 1."
    },
    model_sample="Click 'Forgot Password' on the login page, enter your email, follow the reset link."
)
print(f"Score: {result.score}, Passed: {result.passed}")
```

### Validate Grader Definition (SDK v2.29.0 verified)

```python
from openai import OpenAI

client = OpenAI()

validation = client.fine_tuning.alpha.graders.validate(
    grader={
        "type": "score", "name": "code_quality", "model": "gpt-5.5",
        "input": "Evaluate Python code quality. Score 0-1.", "pass_threshold": 0.8
    }
)
if validation.valid:
    print("Grader definition is valid")
else:
    print(f"Errors: {validation.errors}")
```

### Batch Evaluation with Grader

```python
from openai import OpenAI

client = OpenAI()

grader_def = {
    "type": "score", "name": "response_quality", "model": "gpt-5.5",
    "input": "Rate overall response quality from 0 to 1.", "pass_threshold": 0.7
}

test_cases = [
    {"input": "What is Python?", "output": "Python is a programming language."},
    {"input": "Explain REST APIs", "output": "REST is an architectural style for web services."},
    {"input": "What is 2+2?", "output": "The answer is 4."}
]

scores = []
for tc in test_cases:
    result = client.fine_tuning.alpha.graders.run(
        grader=grader_def, model_sample=tc["output"]
    )
    scores.append(result.score)
    print(f"  [{tc['input'][:30]}] Score: {result.score:.2f} Pass: {result.passed}")

avg_score = sum(scores) / len(scores)
print(f"Average: {avg_score:.2f}, Pass rate: {sum(1 for s in scores if s >= 0.7)/len(scores):.0%}")
```

## Error Responses

- **400 Bad Request** - Invalid grader definition
- **401 Unauthorized** - Invalid API key
- **422 Unprocessable Entity** - Grader validation failed

## Differences from Other APIs

- **vs Anthropic**: No grader/evaluation API
- **vs Gemini**: Evaluation tools in Vertex AI, different surface
- **vs OpenAI Evals**: Graders are lower-level primitives used within Evals

## Limitations and Known Issues

- **Alpha status**: API surface may change without notice [VERIFIED]
- **LLM grader cost**: Each run using LLM consumes tokens [VERIFIED]
- **Determinism**: LLM-based graders may vary slightly on same input [ASSUMED]

## TypeScript Examples

### Fine-tuning Operations

```typescript
import OpenAI from "openai";

const client = new OpenAI();

// List fine-tuning jobs
for await (const job of await client.fineTuning.jobs.list({ limit: 5 })) {
  console.log(`${job.id}: ${job.status}`);
}
```

## Sources

- OAIAPI-SC-OAI-FTGRAD - Graders API Reference

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 15:40]**
- Enriched: Full grader types, SDK examples (run, validate, batch) from 2026-03-20
- Updated: Model refs to gpt-5.5, SDK v2.29.0 verified paths

**[2026-05-22 11:40]**
- Stub created
