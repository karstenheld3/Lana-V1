# PROMPTS

The task the agent received (prompt-queue format: fenced prompts separated by ---).

PROMPTS.md
````
```
/transcribe the local file `input/pricing_page.html` to markdown at `output/pricing_page.md`. Preserve 100% of the content: all headings, the feature list, and the complete pricing table with every value. Do not add commentary or metadata.
```
````

# REFERENCE OUTPUT

One known-good solution produced by a reference agent. Folder structure:

```
└─ pricing_page.md
```

pricing_page.md
```
# Acme Widgets Pricing

Choose the plan that fits your team. All plans include a 14-day free trial and can be cancelled monthly.

## What every plan includes

- Unlimited widget templates
- Email support within 24 hours
- Export to CSV and JSON

## Plans

| Plan       | Price per month | Seats     | Storage |
|------------|-----------------|-----------|---------|
| Starter    | $9              | 1         | 5 GB    |
| Pro        | $29             | 5         | 50 GB   |
| Enterprise | $99             | Unlimited | 1 TB    |

## Notes

Prices exclude VAT. Yearly billing saves 20 percent. Enterprise includes a dedicated account manager.
```

# AGENT OUTPUT

The output to judge. Full workspace folder structure:

```
├─ input
│  └─ pricing_page.html
└─ output
   └─ pricing_page.md
```

output/pricing_page.md
```
# Acme Widgets Pricing

Choose the plan that fits your team. All plans include a 14-day free trial and can be cancelled monthly.

## What every plan includes

- Unlimited widget templates
- Email support within 24 hours
- Export to CSV and JSON

## Plans

| Plan | Price per month | Seats | Storage |
|---|---|---|---|
| Starter | $9 | 1 | 5 GB |
| Pro | $29 | 5 | 50 GB |
| Enterprise | $99 | Unlimited | 1 TB |

## Notes

Prices exclude VAT. Yearly billing saves 20 percent. Enterprise includes a dedicated account manager.
```