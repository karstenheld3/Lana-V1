# Admin Permissions, Data Retention, and Spend Alerts

**Doc ID**: OAIAPI-IN80
**Goal**: Document new administration endpoints for model permissions, hosted tool permissions, data retention, and spend alerts
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN47_ADMIN_OVERVIEW.md [OAIAPI-IN47]` for admin context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

New administration endpoints added since 2026-03 provide granular project-level controls. Admin API Keys allow creating and managing admin-scoped API keys. Model Permissions control which models a project can access. Hosted Tool Permissions control which hosted tools (computer_use, code_interpreter, etc.) are available. Data Retention allows per-project configuration of data storage duration. Spend Alerts enable threshold-based cost notifications. All endpoints require admin API key authentication and are now supported in all official SDKs (Python, Node, Go, Ruby, Java). [VERIFIED] (OAIAPI-SC-OAI-GADMSK, OAIAPI-SC-OAI-GCHLOG)

## REST API

### Admin API Keys

#### Create Admin API Key

**Endpoint**: `POST /v1/organization/admin_api_keys`

**Request**:

```json
{
  "name": "Production Admin Key"
}
```

#### Retrieve, Delete, List Admin API Keys

**Endpoints**:
- `GET /v1/organization/admin_api_keys/{key_id}`
- `DELETE /v1/organization/admin_api_keys/{key_id}`
- `GET /v1/organization/admin_api_keys`

### Model Permissions

Control which models a project can use.

#### Retrieve Model Permission

**Endpoint**: `GET /v1/organization/projects/{project_id}/model_permissions`

**Response** (`200 OK`):

```json
{
  "object": "model_permission",
  "data": [
    {
      "model": "gpt-5.5",
      "allowed": true
    },
    {
      "model": "gpt-image-2",
      "allowed": false
    }
  ]
}
```

#### Update Model Permission

**Endpoint**: `POST /v1/organization/projects/{project_id}/model_permissions`

**Request**:

```json
{
  "model": "gpt-5.5",
  "allowed": true
}
```

#### Delete Model Permission

**Endpoint**: `DELETE /v1/organization/projects/{project_id}/model_permissions/{permission_id}`

### Hosted Tool Permissions

Control which built-in hosted tools a project can use.

#### Retrieve Hosted Tool Permission

**Endpoint**: `GET /v1/organization/projects/{project_id}/hosted_tool_permissions`

**Response** (`200 OK`):

```json
{
  "object": "hosted_tool_permission",
  "data": [
    {
      "tool": "computer_use",
      "allowed": true
    },
    {
      "tool": "code_interpreter",
      "allowed": true
    },
    {
      "tool": "web_search",
      "allowed": false
    }
  ]
}
```

#### Update Hosted Tool Permission

**Endpoint**: `POST /v1/organization/projects/{project_id}/hosted_tool_permissions`

**Request**:

```json
{
  "tool": "web_search",
  "allowed": true
}
```

### Data Retention

Per-project data retention configuration.

#### Retrieve Data Retention

**Endpoint**: `GET /v1/organization/projects/{project_id}/data_retention`

**Response** (`200 OK`):

```json
{
  "object": "data_retention",
  "retention_days": 30,
  "default_retention_days": 30
}
```

#### Update Data Retention

**Endpoint**: `POST /v1/organization/projects/{project_id}/data_retention`

**Request**:

```json
{
  "retention_days": 7
}
```

### Spend Alerts

Threshold-based cost notifications per project.

#### Create Spend Alert

**Endpoint**: `POST /v1/organization/projects/{project_id}/spend_alerts`

**Request**:

```json
{
  "threshold_amount": 100.00,
  "currency": "USD",
  "notification_emails": ["admin@company.com"]
}
```

#### Update, Delete, List Spend Alerts

**Endpoints**:
- `POST /v1/organization/projects/{project_id}/spend_alerts/{alert_id}`
- `DELETE /v1/organization/projects/{project_id}/spend_alerts/{alert_id}`
- `GET /v1/organization/projects/{project_id}/spend_alerts`

## SDK Examples (Python)

### Admin API Key Management

```python
from openai import OpenAI

client = OpenAI()  # Use admin API key

# Create admin API key
key = client.admin.organization.admin_api_keys.create(
    name="CI/CD Pipeline Key"
)
print(f"Key ID: {key.id}")
print(f"Secret: {key.secret}")  # Only shown once

# List admin keys
keys = client.admin.organization.admin_api_keys.list()
for k in keys.data:
    print(f"{k.id}: {k.name}")

# Delete admin key
client.admin.organization.admin_api_keys.delete(key.id)
```

### Model Permission Management

```python
from openai import OpenAI

client = OpenAI()  # Use admin API key

project_id = "proj_abc123"

# Check current model permissions
perms = client.admin.organization.projects.model_permissions.retrieve(project_id)
for p in perms.data:
    print(f"{p.model}: {'allowed' if p.allowed else 'blocked'}")

# Allow GPT-5.5 for project
client.admin.organization.projects.model_permissions.update(
    project_id,
    model="gpt-5.6-sol",
    allowed=True,
)

# Block expensive image model
client.admin.organization.projects.model_permissions.update(
    project_id,
    model="gpt-image-2",
    allowed=False,
)
```

### Data Retention Configuration

```python
from openai import OpenAI

client = OpenAI()  # Use admin API key

project_id = "proj_abc123"

# Get current retention
retention = client.admin.organization.projects.data_retention.retrieve(project_id)
print(f"Current retention: {retention.retention_days} days")

# Set 7-day retention for sensitive project
client.admin.organization.projects.data_retention.update(
    project_id,
    retention_days=7,
)
```

### Spend Alert Setup

```python
from openai import OpenAI

client = OpenAI()  # Use admin API key

project_id = "proj_abc123"

# Create spend alert at $100
alert = client.admin.organization.projects.spend_alerts.create(
    project_id,
    threshold_amount=100.00,
    currency="USD",
    notification_emails=["admin@company.com", "finance@company.com"],
)
print(f"Alert ID: {alert.id}")

# Create higher threshold alert
client.admin.organization.projects.spend_alerts.create(
    project_id,
    threshold_amount=500.00,
    currency="USD",
    notification_emails=["admin@company.com"],
)

# List all alerts
alerts = client.admin.organization.projects.spend_alerts.list(project_id)
for a in alerts.data:
    print(f"${a.threshold_amount}: {a.notification_emails}")
```

### Model Permission Management (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/admin/organization/projects/model_permissions.py
# Note: SDK uses mode="allow_list"/"deny_list" + model_ids=[], not model= + allowed=
from openai import OpenAI

client = OpenAI(admin_api_key="sk-admin-...")

project_id = "proj_abc123"

# Check current model permissions
perms = client.admin.organization.projects.model_permissions.retrieve(project_id)
print(f"Mode: {perms.mode}, Models: {perms.model_ids}")

# Allow only specific models for project (allowlist mode)
client.admin.organization.projects.model_permissions.update(
    project_id,
    mode="allow_list",
    model_ids=["gpt-5.5", "gpt-4.1-mini"],
)

# Block specific models (denylist mode)
client.admin.organization.projects.model_permissions.update(
    project_id,
    mode="deny_list",
    model_ids=["gpt-image-2"],
)
```

### Data Retention Configuration (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/admin/organization/projects/data_retention.py
# Note: SDK uses retention_type (enum), not retention_days (int)
# Valid values: "organization_default", "none", "zero_data_retention",
#   "modified_abuse_monitoring", "enhanced_zero_data_retention",
#   "enhanced_modified_abuse_monitoring"
from openai import OpenAI

client = OpenAI(admin_api_key="sk-admin-...")

project_id = "proj_abc123"

# Get current retention
retention = client.admin.organization.projects.data_retention.retrieve(project_id)
print(f"Current retention: {retention.retention_type}")

# Set zero data retention for sensitive project
client.admin.organization.projects.data_retention.update(
    project_id,
    retention_type="zero_data_retention",
)
```

### Spend Alert Setup (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/admin/organization/projects/spend_alerts.py
# Note: SDK uses notification_channel={emails: [...]}, not notification_emails=[]
#       threshold_amount is in cents (int), not dollars (float)
from openai import OpenAI

client = OpenAI(admin_api_key="sk-admin-...")

project_id = "proj_abc123"

# Create spend alert at $100 (10000 cents)
alert = client.admin.organization.projects.spend_alerts.create(
    project_id,
    threshold_amount=10000,
    currency="USD",
    interval="month",
    notification_channel={"emails": ["admin@company.com", "finance@company.com"]},
)
print(f"Alert ID: {alert.id}")

# Create higher threshold alert
client.admin.organization.projects.spend_alerts.create(
    project_id,
    threshold_amount=50000,
    currency="USD",
    interval="month",
    notification_channel={"emails": ["admin@company.com"]},
)

# List all alerts
alerts = client.admin.organization.projects.spend_alerts.list(project_id)
for a in alerts.data:
    print(f"${a.threshold_amount/100:.2f}: {a.notification_channel}")
```

## Error Responses

- **401 Unauthorized** - Missing or invalid admin API key
- **403 Forbidden** - Insufficient permissions (need admin role)
- **404 Not Found** - Project or resource not found
- **400 Bad Request** - Invalid retention_days or threshold_amount

## Gotchas and Quirks

- **Admin key required**: All endpoints require an admin API key, not a regular project API key [VERIFIED]
- **SDK support**: Now in Python, Node, Go, Ruby, and Java SDKs [VERIFIED] (OAIAPI-SC-OAI-GCHLOG)
- **Retention minimum**: Data retention cannot be set below organizational minimum [ASSUMED]
- **Spend alerts are notifications only**: They do NOT automatically stop usage when threshold is reached [ASSUMED]

## TypeScript Examples

### Admin API

```typescript
import OpenAI from "openai";

// Admin API requires admin API key
const client = new OpenAI();

// List organization members
for await (const user of await client.admin.users.list()) {
  console.log(`${user.email}: ${user.role}`);
}
```

## Sources

- OAIAPI-SC-OAI-ADMKEY - Admin API Keys reference
- OAIAPI-SC-OAI-ADMMDL - Model Permissions reference
- OAIAPI-SC-OAI-ADMHTL - Hosted Tool Permissions reference
- OAIAPI-SC-OAI-ADMDRT - Data Retention reference
- OAIAPI-SC-OAI-ADMSPN - Spend Alerts reference
- OAIAPI-SC-OAI-GADMSK - Admin APIs guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 10:10]**
- Initial documentation for admin permissions, data retention, and spend alerts (new topic)
