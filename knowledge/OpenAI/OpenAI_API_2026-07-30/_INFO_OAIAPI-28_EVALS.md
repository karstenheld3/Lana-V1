# Evaluations (Evals) API [DEPRECATED]

**Doc ID**: OAIAPI-IN28
**Goal**: Document Evals API for model quality assessment, dataset management, and eval runs
**Version scope**: API v1, Documentation date 2026-07-30
**Status**: **DEPRECATED** (announced 2026-06-03). Migrate to Promptfoo. See https://developers.openai.com/cookbook/examples/evaluation/moving-from-openai-evals-to-promptfoo

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

**DEPRECATED**: The Evals platform was deprecated on 2026-06-03. Graders documented for eval workflows are part of this transition. Migrate to Promptfoo or equivalent external evaluation framework.

The Evals API provided systematic model quality assessment through datasets and evaluation runs. Create evals with test schemas and testing criteria (POST /v1/evals), run evaluations against models, and retrieve results. Metrics: exact match, semantic similarity, LLM-as-judge, custom graders. Runs execute in background (async). SDK v2.29.0 uses `evals.create(data_source_config=..., testing_criteria=[...])`, not `evals.datasets`. [VERIFIED] (OAIAPI-SC-OAI-EVLCRT, OAIAPI-SC-OAI-GEVAL)

## Key Facts

- **Purpose**: Systematic model quality assessment [VERIFIED]
- **Components**: Evals (test schemas + criteria), Runs (executions), Results (metrics) [VERIFIED]
- **Metrics**: Exact match, semantic similarity, LLM judges, custom [VERIFIED]
- **Async**: Runs execute in background, poll for completion [VERIFIED]
- **SDK note**: `evals.create()` with `data_source_config` + `testing_criteria` (not `evals.datasets`) [VERIFIED]

## Evaluation Metrics

- **exact_match**: Score 1.0 if match, 0.0 otherwise - for deterministic outputs
- **semantic_similarity**: 0.0-1.0 cosine similarity - for flexible matching
- **llm_judge**: 0.0-1.0 LLM judgment - for complex evaluation
- **custom**: User-defined scoring - for domain-specific metrics

## SDK Examples (Python)

### Create Eval (SDK v2.29.0 verified)

```python
from openai import OpenAI

client = OpenAI()

eval_obj = client.evals.create(
    name="math_problems",
    data_source_config={
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "problem": {"type": "string"},
                "expected_output": {"type": "string"}
            },
            "required": ["problem", "expected_output"]
        }
    },
    testing_criteria=[
        {
            "type": "string_check",
            "input": "{{sample.output_text}}",
            "reference": "{{item.expected_output}}",
            "name": "exact_match",
            "operation": "eq"
        }
    ]
)
print(f"Eval created: {eval_obj.id}")
```

### Run Evaluation (SDK v2.29.0 verified)

```python
from openai import OpenAI
import time

client = OpenAI()

eval_id = "eval_abc123"

run = client.evals.runs.create(
    eval_id,
    data_source={
        "type": "completions",
        "source": {
            "type": "file_content",
            "content": [
                {"item": {"problem": "What is 15 + 27?", "expected_output": "42"}}
            ]
        },
        "input_messages": {
            "type": "template",
            "template": [
                {"type": "message", "role": "user", "content": "Solve: {{item.problem}}"}
            ]
        },
        "model": "gpt-5.5",
        "sampling_params": {"temperature": 0.0}
    },
    name="math_eval_run"
)

while run.status in ("queued", "in_progress"):
    time.sleep(5)
    run = client.evals.runs.retrieve(eval_id, run.id)
    print(f"Status: {run.status}")
```

### Compare Models

```python
from openai import OpenAI
import time

client = OpenAI()

dataset_id = "dataset_abc123"
models = ["gpt-5.5", "gpt-4.1-mini", "gpt-4.1-nano"]

results = {}
for model in models:
    run = client.evals.runs.create(
        dataset_id=dataset_id, model=model, metric="semantic_similarity"
    )
    while run.status == "running":
        time.sleep(5)
        run = client.evals.runs.retrieve(run.id)
    results[model] = run.results.accuracy

for model, accuracy in sorted(results.items(), key=lambda x: x[1], reverse=True):
    print(f"{model}: {accuracy:.2%}")
```

### Compare Models (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/evals/runs/runs.py
# Note: SDK runs.create uses (eval_id, data_source=, name=), not (dataset_id, model, metric)
#       Model is specified inside data_source, not as top-level param
from openai import OpenAI
import time

client = OpenAI()

eval_id = "eval_abc123"
models = ["gpt-5.5", "gpt-4.1-mini", "gpt-4.1-nano"]

results = {}
for model in models:
    run = client.evals.runs.create(
        eval_id,
        data_source={
            "type": "completions",
            "source": {"type": "file_content", "content": [
                {"item": {"question": "What is 15+27?", "expected": "42"}}
            ]},
            "input_messages": {"type": "template", "template": [
                {"type": "message", "role": "user", "content": "{{item.question}}"}
            ]},
            "model": model,
            "sampling_params": {"temperature": 0.0}
        },
        name=f"compare_{model}"
    )
    while run.status in ("queued", "in_progress"):
        time.sleep(5)
        run = client.evals.runs.retrieve(eval_id, run.id)
    results[model] = run

for model, run in results.items():
    print(f"{model}: {run.status}")
```

### Regression Testing

```python
from openai import OpenAI
import time

class RegressionTester:
    def __init__(self, dataset_id: str, baseline_threshold: float = 0.90):
        self.client = OpenAI()
        self.dataset_id = dataset_id
        self.baseline_threshold = baseline_threshold
    
    def test_change(self, model: str, config: dict) -> bool:
        run = self.client.evals.runs.create(
            dataset_id=self.dataset_id, model=model,
            metric="semantic_similarity", config=config
        )
        while run.status == "running":
            time.sleep(5)
            run = self.client.evals.runs.retrieve(run.id)
        
        accuracy = run.results.accuracy
        passed = accuracy >= self.baseline_threshold
        print(f"Accuracy: {accuracy:.2%} ({'PASS' if passed else 'FAIL'})")
        return passed

tester = RegressionTester("dataset_abc123", baseline_threshold=0.90)
tester.test_change("gpt-5.5", {"temperature": 0.5, "prompt_template": "New: {{question}}"})
```

## Error Responses

- **404 Not Found** - Dataset or run not found
- **400 Bad Request** - Invalid dataset format or config
- **429 Too Many Requests** - Rate limit exceeded

## Differences from Other APIs

- **vs Weights & Biases**: OpenAI integrated, W&B more features
- **vs MLflow**: Similar eval tracking, different ecosystem
- **vs Custom scripts**: OpenAI managed infrastructure

## Limitations and Known Issues

- **Dataset size limits**: Max examples per dataset [ASSUMED]
- **Metric customization**: Limited custom metric support [ASSUMED]
- **No historical comparison**: Cannot easily track over time [ASSUMED]

## Gotchas and Quirks

- **Async execution**: Runs don't block, must poll [VERIFIED]
- **Cost accumulation**: Each run generates API calls [ASSUMED]
- **SDK API mismatch**: `evals.datasets` does not exist in SDK v2.29.0, use `evals.create()` [VERIFIED]

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

- OAIAPI-SC-OAI-EVLCRT - POST Create eval
- OAIAPI-SC-OAI-EVLRUN - POST Create eval run
- OAIAPI-SC-OAI-GEVAL - Evaluations guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Changed: Marked as DEPRECATED (announced 2026-06-03)
- Added: Migration guidance to Promptfoo
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 15:30]**
- Enriched: Full metrics, SDK examples (create, run, compare, regression) from 2026-03-20
- Updated: Model refs to gpt-5.5
- Changed: Doc ID from IN25 to IN28 per renumbering

**[2026-05-22 11:40]**
- Stub created
