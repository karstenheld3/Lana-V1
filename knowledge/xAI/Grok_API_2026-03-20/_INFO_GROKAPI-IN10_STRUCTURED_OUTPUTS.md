# INFO: Structured Outputs

**Doc ID**: GROKAPI-IN10
**Goal**: JSON schema enforcement, Pydantic/Zod support, response_format, structured outputs with tools
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Structured Outputs guarantees the API returns responses matching a defined schema (JSON). Supported by all language models. Define schemas using Pydantic (Python) or Zod (JavaScript). Supported JSON Schema types: string, number (integer/float), object, array, boolean, enum, anyOf. NOT supported: `allOf`, `minLength`/`maxLength` on strings, `minItems`/`maxItems`/`minContains`/`maxContains` on arrays. In Chat Completions, use `response_format` parameter with `client.beta.chat.completions.parse()`. In Responses API, use `text.format.type: "json_schema"`. The xAI SDK provides a `chat.parse(Model)` method that returns a tuple of (response, parsed_object). Structured outputs can be combined with tools for function calling that returns structured data. [VERIFIED] (GROKAPI-SC-XAI-STRUCTOUT | https://docs.x.ai/developers/model-capabilities/text/structured-outputs)

## Key Facts

- [VERIFIED] Supported by all language models (GROKAPI-SC-XAI-STRUCTOUT)
- [VERIFIED] Response guaranteed to match input schema (GROKAPI-SC-XAI-STRUCTOUT)
- [VERIFIED] Supported types: string, number, integer, float, object, array, boolean, enum, anyOf (GROKAPI-SC-XAI-STRUCTOUT)
- [VERIFIED] NOT supported: `allOf` (GROKAPI-SC-XAI-STRUCTOUT)
- [VERIFIED] NOT supported: `minLength`/`maxLength` on strings (GROKAPI-SC-XAI-STRUCTOUT)
- [VERIFIED] NOT supported: `minItems`/`maxItems`/`minContains`/`maxContains` on arrays (GROKAPI-SC-XAI-STRUCTOUT)
- [VERIFIED] Pydantic (Python) and Zod (JavaScript) schema definition supported (GROKAPI-SC-XAI-STRUCTOUT)

## Quick Reference

- **Chat Completions**: `client.beta.chat.completions.parse(response_format=Model)`
- **Responses API**: `text: {"format": {"type": "json_schema", "json_schema": {...}}}`
- **xAI SDK**: `chat.parse(Model)` returns `(response, parsed_object)`
- **Supported types**: string, number, object, array, boolean, enum, anyOf
- **NOT supported**: allOf, minLength, maxLength, minItems, maxItems

## Examples

### Invoice Parsing with Pydantic (xAI SDK)

```python
import os
from datetime import date
from enum import Enum

from pydantic import BaseModel, Field
from xai_sdk import Client
from xai_sdk.chat import system, user

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class LineItem(BaseModel):
    description: str = Field(description="Description of the item or service")
    quantity: int = Field(description="Number of units", ge=1)
    unit_price: float = Field(description="Price per unit", ge=0)

class Address(BaseModel):
    street: str = Field(description="Street address")
    city: str = Field(description="City")
    postal_code: str = Field(description="Postal/ZIP code")
    country: str = Field(description="Country")

class Invoice(BaseModel):
    vendor_name: str = Field(description="Name of the vendor")
    vendor_address: Address = Field(description="Vendor's address")
    invoice_number: str = Field(description="Unique invoice identifier")
    invoice_date: date = Field(description="Date the invoice was issued")
    line_items: list[LineItem] = Field(description="List of purchased items/services")
    total_amount: float = Field(description="Total amount due", ge=0)
    currency: Currency = Field(description="Currency of the invoice")

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(model="grok-4.20-beta-latest-non-reasoning")

chat.append(system("Extract invoice data into JSON format."))
chat.append(user("""
Vendor: Acme Corp, 123 Main St, Springfield, IL 62704
Invoice Number: INV-2025-001
Date: 2025-02-10
Items:
- Widget A, 5 units, $10.00 each
- Widget B, 2 units, $15.00 each
Total: $80.00 USD
"""))

response, invoice = chat.parse(Invoice)
assert isinstance(invoice, Invoice)
print(f"Vendor: {invoice.vendor_name}")
print(f"Total: {invoice.total_amount} {invoice.currency}")
```

### Invoice Parsing with Pydantic (OpenAI SDK)

```python
import os
from openai import OpenAI
from pydantic import BaseModel, Field
from datetime import date
from enum import Enum

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class LineItem(BaseModel):
    description: str = Field(description="Description of the item or service")
    quantity: int = Field(description="Number of units", ge=1)
    unit_price: float = Field(description="Price per unit", ge=0)

class Invoice(BaseModel):
    vendor_name: str
    invoice_number: str
    invoice_date: date
    line_items: list[LineItem]
    total_amount: float
    currency: Currency

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

completion = client.beta.chat.completions.parse(
    model="grok-4.20-beta-latest-non-reasoning",
    messages=[
        {"role": "system", "content": "Extract invoice data into JSON format."},
        {"role": "user", "content": "Vendor: Acme Corp\nInvoice: INV-001\nDate: 2025-02-10\nWidget A x5 $10, Widget B x2 $15\nTotal: $80.00 USD"},
    ],
    response_format=Invoice,
)

invoice = completion.choices[0].message.parsed
print(f"Vendor: {invoice.vendor_name}")
print(f"Total: {invoice.total_amount} {invoice.currency}")
```

### Entity Extraction with Zod (JavaScript)

```typescript
import { z } from "zod";
import { xai } from "@ai-sdk/xai";
import { generateObject } from "ai";

const PersonSchema = z.object({
  name: z.string().describe("Full name"),
  age: z.number().int().describe("Age in years"),
  occupation: z.string().describe("Current occupation"),
  skills: z.array(z.string()).describe("List of skills"),
});

const { object } = await generateObject({
  model: xai.responses("grok-4.20-beta-latest-non-reasoning"),
  schema: PersonSchema,
  prompt: "Extract info: John Smith, 35, software engineer skilled in Python, TypeScript, and Rust",
});

console.log(object.name);    // "John Smith"
console.log(object.skills);  // ["Python", "TypeScript", "Rust"]
```

## Differences from Other APIs

### vs OpenAI

- **Compatible**: Same `response_format` parameter, same Pydantic support
- **Schema limitations**: xAI does not support `allOf` (OpenAI does)
- **String constraints**: xAI does not support `minLength`/`maxLength` (OpenAI does)
- **Array constraints**: xAI does not support `minItems`/`maxItems` (OpenAI does)

### vs Anthropic

- **Different approach**: Anthropic uses tool_use with JSON schema for structured output; xAI uses dedicated response_format
- **No native parse**: Anthropic SDK has no `beta.chat.completions.parse()` equivalent

### vs Gemini

- **Different approach**: Gemini uses `response_mime_type: "application/json"` with `response_schema`; xAI uses OpenAI-compatible `response_format`

## Limitations and Known Issues

- [VERIFIED] `allOf` not supported (GROKAPI-SC-XAI-STRUCTOUT)
- [VERIFIED] `minLength`/`maxLength` not supported on strings (GROKAPI-SC-XAI-STRUCTOUT)
- [VERIFIED] `minItems`/`maxItems`/`minContains`/`maxContains` not supported on arrays (GROKAPI-SC-XAI-STRUCTOUT)

## Sources

- GROKAPI-SC-XAI-STRUCTOUT | https://docs.x.ai/developers/model-capabilities/text/structured-outputs | Accessed: 2026-03-20

## Document History

**[2026-03-20 04:10]**
- Initial document created with schema support, examples, and limitations
