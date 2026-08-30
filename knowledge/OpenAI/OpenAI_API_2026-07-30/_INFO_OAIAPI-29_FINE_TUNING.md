# Fine-Tuning

**Doc ID**: OAIAPI-IN29
**Goal**: Document fine-tuning jobs API and self-serve changes
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Fine-tuning customizes models on your data via `POST /v1/fine_tuning/jobs`. Supports supervised fine-tuning with JSONL training data. Jobs can be created, listed, retrieved, cancelled, paused, and resumed. Checkpoints with permissions enable model sharing. **2026-05 changes**: Self-serve fine-tuning availability updated; inference on fine-tuned models continues until base model deprecation. GPT-5.5 does NOT support fine-tuning. Fine-tuned versions of deprecated base models (ft-gpt-3.5-turbo, ft-gpt-4, ft-gpt-4.1-nano) are being retired with replacement mappings. [VERIFIED] (OAIAPI-SC-OAI-FTJOBS, OAIAPI-SC-OAI-GFNTN, OAIAPI-SC-OAI-GDEPR)

## Use Cases

- **Domain adaptation**: Medical, legal, technical domains
- **Style matching**: Brand voice, writing style consistency
- **Task specialization**: Specific workflows, custom instructions
- **Cost optimization**: Use smaller fine-tuned model instead of larger general model

## REST API

**Create**: `POST /v1/fine_tuning/jobs`
**Retrieve**: `GET /v1/fine_tuning/jobs/{job_id}`
**List**: `GET /v1/fine_tuning/jobs`
**Cancel**: `POST /v1/fine_tuning/jobs/{job_id}/cancel`
**Pause**: `POST /v1/fine_tuning/jobs/{job_id}/pause`
**Resume**: `POST /v1/fine_tuning/jobs/{job_id}/resume`
**Events**: `GET /v1/fine_tuning/jobs/{job_id}/events`
**Checkpoints**: `GET /v1/fine_tuning/jobs/{job_id}/checkpoints`

### Create Job Parameters

**Required:**
- **model** (string) - Base model ID (gpt-5.4-mini, o4-mini-2025-04-16)
- **training_file** (string) - File ID from Files API

**Optional:**
- **validation_file** (string) - Validation data file ID
- **hyperparameters** (object) - Training configuration
  - **n_epochs** (integer) - Training epochs (1-50, auto by default)
  - **batch_size** (integer) - Batch size (auto by default)
  - **learning_rate_multiplier** (number) - Learning rate multiplier (auto by default)
- **suffix** (string) - Custom suffix for model ID (max 40 chars)
- **seed** (integer) - Random seed for reproducibility

### Job Status Values

- **validating_files** - Checking uploaded data
- **queued** - Waiting to start
- **running** - Training in progress
- **succeeded** - Completed successfully
- **failed** - Training failed
- **cancelled** - User cancelled job

### Fine-Tuned Model ID Format

```
ft:{base_model}:{org_id}:{suffix}:{job_id}
```

Example: `ft:gpt-5.4-mini:org-abc:customer-support:ftjob-123`

### Checkpoints

Saved periodically during training. Use for:
- Resume from checkpoint if job fails
- Evaluate intermediate models
- Early stopping if validation metrics degrade

## Training Data Format (JSONL)

Each line in the training file:

```json
{"messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is 2+2?"}, {"role": "assistant", "content": "4"}]}
```

**Requirements:**
- JSONL format (one JSON object per line)
- At least 10 training examples (50+ recommended)
- Each example: system (optional) + user + assistant messages
- Maximum tokens per example depends on model context window

## SDK Examples (Python)

### Create Fine-Tuning Job

```python
from openai import OpenAI

client = OpenAI()

# Upload training data
training_file = client.files.create(
    file=open("training_data.jsonl", "rb"),
    purpose="fine-tune",
)

# Create fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file=training_file.id,
    model="gpt-5.4-mini",
    hyperparameters={"n_epochs": 3},
)
print(f"Job: {job.id}, Status: {job.status}")
```

### Monitor and Use Fine-Tuned Model

```python
from openai import OpenAI
import time

client = OpenAI()

job_id = "ftjob_abc123"

# Poll job status
while True:
    job = client.fine_tuning.jobs.retrieve(job_id)
    print(f"Status: {job.status}")
    if job.status in ("succeeded", "failed", "cancelled"):
        break
    time.sleep(60)

# Use fine-tuned model
if job.status == "succeeded":
    response = client.chat.completions.create(
        model=job.fine_tuned_model,
        messages=[{"role": "user", "content": "Hello"}]
    )
    print(response.choices[0].message.content)
```

### List and Manage Jobs

```python
from openai import OpenAI

client = OpenAI()

# List jobs
for job in client.fine_tuning.jobs.list(limit=5).data:
    print(f"{job.id}: {job.status} ({job.model})")

# View training events
events = client.fine_tuning.jobs.list_events(job_id="ftjob_abc123", limit=10)
for event in events.data:
    print(f"{event.created_at}: {event.message}")

# Cancel a running job
client.fine_tuning.jobs.cancel("ftjob_abc123")
```

### With Validation Data

```python
from openai import OpenAI

client = OpenAI()

# Upload validation file
val_file = client.files.create(
    file=open("validation_data.jsonl", "rb"),
    purpose="fine-tune",
)

# Create job with validation
job = client.fine_tuning.jobs.create(
    model="gpt-5.4-mini",
    training_file="file_train_abc",
    validation_file=val_file.id,
    hyperparameters={"n_epochs": 5},
    suffix="customer-support",
)
print(f"Job created: {job.id}")
```

## Error Responses

- **400 Bad Request** - Invalid training data or parameters
- **404 Not Found** - File or job not found
- **429 Too Many Requests** - Rate limit for concurrent jobs exceeded

## Deprecation Impact

Fine-tuned model replacements (2026-04-22 wave):
- `ft-gpt-3.5-turbo` -> retrain on `gpt-5.4-mini`
- `ft-gpt-4` -> retrain on `gpt-5.5`
- `ft-gpt-4.1-nano-*` -> retrain on `gpt-5.4-nano`
- `ft-babbage-002`, `ft-davinci-002` -> retrain on `gpt-5.4-mini`

**Inference continues** on fine-tuned models until the base model is deprecated.

## Fine-Tuning Sub-Guides

- **Model optimization overview**: https://developers.openai.com/api/docs/guides/model-optimization
- **Supervised fine-tuning**: https://developers.openai.com/api/docs/guides/supervised-fine-tuning
- **Vision fine-tuning**: https://developers.openai.com/api/docs/guides/vision-fine-tuning (IN90)
- **DPO**: https://developers.openai.com/api/docs/guides/direct-preference-optimization (IN30)
- **Reinforcement fine-tuning**: https://developers.openai.com/api/docs/guides/reinforcement-fine-tuning (IN30)
- **RFT use cases**: https://developers.openai.com/api/docs/guides/rft-use-cases
- **Best practices**: https://developers.openai.com/api/docs/guides/fine-tuning-best-practices
- **Graders**: https://developers.openai.com/api/docs/guides/graders (IN31)

## Gotchas and Quirks

- **Platform winding down**: Fine-tuning platform is NO LONGER ACCESSIBLE to new users. Existing users can create training jobs temporarily [VERIFIED] (OAIAPI-SC-OAI-GPRICE)
- **GPT-5.5 no fine-tuning**: Not supported for fine-tuning [VERIFIED]
- **Only o4-mini trainable**: Only `o4-mini-2025-04-16` is listed for new training ($100/hour) [VERIFIED] (OAIAPI-SC-OAI-GPRICE)
- **Base model sunset**: Fine-tuned inference stops when base model is deprecated [VERIFIED]
- **Vision fine-tuning**: Separate workflow from text-only fine-tuning, requires image-text training pairs [VERIFIED]
- **Checkpoint permissions**: Fine-tuned model checkpoints can be shared via permissions API [VERIFIED]

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

- OAIAPI-SC-OAI-FTJOBS, OAIAPI-SC-OAI-GFNTN, OAIAPI-SC-OAI-GDEPR, OAIAPI-SC-OAI-GVFT

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 11:20]**
- Added: Self-serve fine-tuning changes, deprecation impact, GPT-5.5 limitation
