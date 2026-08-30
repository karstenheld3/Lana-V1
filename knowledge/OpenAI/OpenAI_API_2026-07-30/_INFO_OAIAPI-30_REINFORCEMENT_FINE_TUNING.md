# Reinforcement Fine-Tuning

**Doc ID**: OAIAPI-IN30
**Goal**: Document reinforcement fine-tuning (RFT), DPO, grader-based training, and training metrics
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Reinforcement Fine-Tuning (RFT) extends supervised fine-tuning with preference-based optimization. DPO trains models to prefer certain outputs using chosen/rejected pairs. RFT uses graders to automatically evaluate outputs during training, enabling reward-based optimization. Supported models: gpt-4.1, gpt-4.1-mini, gpt-4.1-nano for DPO. Training metrics include reward accuracy, loss curves, and grader scores. Checkpoints saved during training. [VERIFIED] (OAIAPI-SC-OAI-GRFT, OAIAPI-SC-OAI-FTGRAD)

## Key Facts

- **DPO**: Direct Preference Optimization with chosen/rejected pairs [VERIFIED]
- **Graders**: Automated output evaluation for reward signals [VERIFIED]
- **Models**: gpt-4.1, gpt-4.1-mini, gpt-4.1-nano support DPO [VERIFIED]
- **Data format**: JSONL with messages, chosen, rejected [VERIFIED]
- **Metrics**: Reward accuracy, loss, grader scores [VERIFIED]

## DPO Training Data Format

```jsonl
{"messages": [{"role": "user", "content": "Write a Python sort function"}], "chosen": {"role": "assistant", "content": "def sort_list(items):\n    return sorted(items)"}, "rejected": {"role": "assistant", "content": "items.sort()\nreturn items"}}
```

Fields: **messages** (conversation context), **chosen** (preferred response), **rejected** (dispreferred response)

## Grader-Based Training

Grader types:
- **Score grader**: Numeric score (0-1)
- **Label grader**: Categorical (pass/fail)
- **Custom grader**: User-defined logic

```json
{
  "type": "score",
  "name": "code_quality",
  "model": "gpt-5.5",
  "input": "Rate the code quality from 0 to 1: readability, correctness, efficiency",
  "pass_threshold": 0.7
}
```

## SDK Examples (Python)

### Create DPO Fine-Tuning Job

```python
from openai import OpenAI

client = OpenAI()

with open("dpo_training.jsonl", "rb") as f:
    training_file = client.files.create(file=f, purpose="fine-tune")

job = client.fine_tuning.jobs.create(
    model="gpt-4.1",
    training_file=training_file.id,
    method={
        "type": "dpo",
        "dpo": {
            "hyperparameters": {"n_epochs": 3, "beta": 0.1}
        }
    },
    suffix="my-dpo-model"
)
print(f"Job: {job.id}, Status: {job.status}")
```

### RFT with Graders

```python
from openai import OpenAI

client = OpenAI()

with open("rft_training.jsonl", "rb") as f:
    training_file = client.files.create(file=f, purpose="fine-tune")

job = client.fine_tuning.jobs.create(
    model="gpt-4.1-mini",
    training_file=training_file.id,
    method={
        "type": "reinforcement",
        "reinforcement": {
            "grader": {
                "type": "score", "name": "quality_check",
                "model": "gpt-5.5",
                "input": "Evaluate for accuracy and helpfulness. Score 0-1.",
                "pass_threshold": 0.7
            },
            "hyperparameters": {"n_epochs": 2, "reasoning_effort": "medium"}
        }
    }
)
print(f"Job: {job.id}, Status: {job.status}")
```

### Monitor Training Metrics

```python
from openai import OpenAI

client = OpenAI()

def monitor_rft_job(job_id: str):
    job = client.fine_tuning.jobs.retrieve(job_id)
    print(f"Status: {job.status}")
    
    events = client.fine_tuning.jobs.list_events(job_id, limit=20)
    for event in events.data:
        print(f"  [{event.created_at}] {event.message}")
        if event.data:
            if "reward_accuracy" in event.data:
                print(f"    Reward accuracy: {event.data['reward_accuracy']:.3f}")
    
    checkpoints = client.fine_tuning.jobs.checkpoints.list(job_id)
    for cp in checkpoints.data:
        print(f"  Checkpoint: {cp.id} (step {cp.step_number})")

monitor_rft_job("ftjob-abc123")
```

## Error Responses

- **400 Bad Request** - Invalid training data format or DPO configuration
- **404 Not Found** - Training file not found
- **429 Too Many Requests** - Concurrent fine-tuning limit

## Differences from Other APIs

- **vs Anthropic**: No public RFT/DPO API
- **vs Gemini**: Fine-tuning via Vertex AI, no public DPO
- **vs Grok**: No public fine-tuning API

## Limitations and Known Issues

- **DPO data quality**: Chosen/rejected pairs must be clearly differentiated [VERIFIED]
- **Grader cost**: Grader evaluations consume tokens during training [VERIFIED]
- **Model support**: Not all models support DPO/RFT [VERIFIED]

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

- OAIAPI-SC-OAI-GRFT - Reinforcement Fine-Tuning Guide
- OAIAPI-SC-OAI-FTGRAD - Fine-Tuning Graders API
- OAIAPI-SC-OAI-FTCKPT - Fine-Tuning Checkpoints

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 15:35]**
- Enriched: Full DPO format, graders, SDK examples from 2026-03-20
- Updated: Model refs to gpt-5.5 in grader examples

**[2026-05-22 11:40]**
- Stub created
