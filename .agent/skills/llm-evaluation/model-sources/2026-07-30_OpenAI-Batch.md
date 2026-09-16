<transcription_page_header> OpenAI Developers | API </transcription_page_header>

# Pricing

<!-- Section 1 -->
<!-- Column 1 -->
Model catalog

Choose a model
: Pricing
: Model selection

Text and code
: Text generation
: Code generation
: Structured output

Prompting
: Overview
: Prompt engineering
: Citation formatting
: Migration guide
: Prompt generation
: Frontend prompting

Reasoning
: Reasoning models
: Reasoning best practices

Images and video
: Images and vision

<!-- Column 2 -->
## Flagship models

Our latest models

Prices per 1M tokens.

<transcription_table>
**Table 1: Flagship models — Prices per 1M tokens (short and long context)**

| Model | Short — Input | Short — Cached input | Short — Cache writes | Short — Output | Long — Input | Long — Cached input | Long — Cache writes | Long — Output |
|-------|---------------:|---------------------:|---------------------:|---------------:|-------------:|--------------------:|--------------------:|---------------:|
| gpt-5.6-sol | $2.50 | $0.25 | $3.125 | $15.00 | $5.00 | $0.50 | $6.25 | $22.50 |
| gpt-5.6-terra | $1.00 | $0.10 | $1.25 | $6.00 | $2.00 | $0.20 | $2.50 | $9.00 |
| gpt-5.6-luna | $0.10 | $0.01 | $0.125 | $0.60 | $0.20 | $0.02 | $0.25 | $0.90 |
| gpt-5.5 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.5-pro | $15.00 | - | - | $90.00 | [unclear] | [unclear] | [unclear] | [unclear] |
| gpt-5.4 | $1.25 | $0.13 | - | $7.50 | $2.50 | $0.25 | - | $11.25 |
| gpt-5.4-mini | $0.375 | $0.0375 | - | $2.25 | - | - | - | - |
| gpt-5.4-nano | $0.10 | $0.01 | - | $0.625 | - | - | - | - |
| gpt-5.4-pro | $15.00 | - | - | $90.00 | [unclear: ~90.00?] | [unclear: ~30.00?] | - | [unclear: ~135.00?] |

<transcription_json>
{"table_type":"data_table","title":"Flagship models — Prices per 1M tokens","columns":["Model","Short_Input","Short_Cached_input","Short_Cache_writes","Short_Output","Long_Input","Long_Cached_input","Long_Cache_writes","Long_Output"],"data":[{"Model":"gpt-5.6-sol","Short_Input":"$2.50","Short_Cached_input":"$0.25","Short_Cache_writes":"$3.125","Short_Output":"$15.00","Long_Input":"$5.00","Long_Cached_input":"$0.50","Long_Cache_writes":"$6.25","Long_Output":"$22.50"},{"Model":"gpt-5.6-terra","Short_Input":"$1.00","Short_Cached_input":"$0.10","Short_Cache_writes":"$1.25","Short_Output":"$6.00","Long_Input":"$2.00","Long_Cached_input":"$0.20","Long_Cache_writes":"$2.50","Long_Output":"$9.00"},{"Model":"gpt-5.6-luna","Short_Input":"$0.10","Short_Cached_input":"$0.01","Short_Cache_writes":"$0.125","Short_Output":"$0.60","Long_Input":"$0.20","Long_Cached_input":"$0.02","Long_Cache_writes":"$0.25","Long_Output":"$0.90"},{"Model":"gpt-5.5","Short_Input":"$2.50","Short_Cached_input":"$0.25","Short_Cache_writes":"-","Short_Output":"$15.00","Long_Input":"$5.00","Long_Cached_input":"$0.50","Long_Cache_writes":"-","Long_Output":"$22.50"},{"Model":"gpt-5.5-pro","Short_Input":"$15.00","Short_Cached_input":"-","Short_Cache_writes":"-","Short_Output":"$90.00","Long_Input":"[unclear]","Long_Cached_input":"[unclear]","Long_Cache_writes":"[unclear]","Long_Output":"[unclear]"},{"Model":"gpt-5.4","Short_Input":"$1.25","Short_Cached_input":"$0.13","Short_Cache_writes":"-","Short_Output":"$7.50","Long_Input":"$2.50","Long_Cached_input":"$0.25","Long_Cache_writes":"-","Long_Output":"$11.25"},{"Model":"gpt-5.4-mini","Short_Input":"$0.375","Short_Cached_input":"$0.0375","Short_Cache_writes":"-","Short_Output":"$2.25","Long_Input":"-","Long_Cached_input":"-","Long_Cache_writes":"-","Long_Output":"-"},{"Model":"gpt-5.4-nano","Short_Input":"$0.10","Short_Cached_input":"$0.01","Short_Cache_writes":"-","Short_Output":"$0.625","Long_Input":"-","Long_Cached_input":"-","Long_Cache_writes":"-","Long_Output":"-"},{"Model":"gpt-5.4-pro","Short_Input":"$15.00","Short_Cached_input":"-","Short_Cache_writes":"-","Short_Output":"$90.00","Long_Input":"[unclear: ~90.00?]","Long_Cached_input":"[unclear: ~30.00?]","Long_Cache_writes":"-","Long_Output":"[unclear: ~135.00?]"}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- Source: OpenAI Developers — Pricing (page shows header "Pricing" and subsection "Flagship models").
- Layout: Left navigation column (Model catalog, sections) and main content area with tabs above table: "Standard  Batch  Flex  Fast mode" (the "Batch" tab is active/outlined).
- Table visual: two grouped column sets labeled "Short context" and "Long context" with subcolumns: Input, Cached input, Cache writes, Output.
- Colors: table headers and separators are grey; active tab has a subtle darker background. Right side of page contains a vertical sidebar listing "Flagship models", "Multimodal models", "Tools", "Specialized models", "Finetuning" and a "Copy Page" control.
- Scrolling: table appears horizontally scrollable (some rightmost values partly clipped); several long-context values in lower rows are partially obscured — those values are marked [unclear] above.
- Typographic notes: monetary values shown with dollar sign and 2-4 decimal places in places (e.g., $3.125, $0.0375).
</transcription_notes>
</transcription_table>

<!-- Section 2 -->
There is a lower table (partially visible) listing older models and prices (example visible rows include gpt-5.2, gpt-5.2-pro, gpt-5.1 with Input/Cached input/Output columns). Values are partially visible:
- gpt-5.2: Input $0.875, Cached input $0.0875, Output $7.00
- gpt-5.2-pro: Input $10.50, Output $84.00
- gpt-5.1: Input $0.625, Cached input $0.0625, Output $5.00

<transcription_page_footer> Page 1 | OpenAI </transcription_page_footer>
<transcription_page_header> OpenAI Developers | Models </transcription_page_header>

# Pricing

<!-- Section 1 -->
<!-- Column 1 -->
<!-- Decorative: [Left navigation ("Model catalog", "Choose a model", "Pricing", "Model selection", "Text and code" sections, etc.), Right sidebar ("Flagship models", "Multimodal models", "Tools", etc.)] -->

## Flagship models

Our latest models  
Prices per 1M tokens.

<transcription_table>
**Table 1: Flagship models — Prices per 1M tokens (Short context and Long context)**

| Model | Short: Input | Short: Cached input | Short: Cache writes | Short: Output | Long: Input | Long: Cached input | Long: Cache writes | Long: Output |
|-------|--------------:|--------------------:|--------------------:|--------------:|------------:|-------------------:|-------------------:|-------------:|
| gpt-5.6-sol | $2.50 | $0.25 | $3.125 | $15.00 | $5.00 | $0.50 | $6.25 | $22.50 |
| gpt-5.6-terra | $1.00 | $0.10 | $1.25 | $6.00 | $2.00 | $0.20 | $2.50 | $9.00 |
| gpt-5.6-luna | $0.10 | $0.01 | $0.125 | $0.60 | $0.20 | $0.02 | $0.25 | $0.90 |
| gpt-5.5 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.5-pro | $15.00 | - | - | $90.00 | - | - | - | - |
| gpt-5.4 | $1.25 | $0.13 | - | $7.50 | $2.50 | $0.25 | - | $11.25 |
| gpt-5.4-mini | $0.375 | $0.0375 | - | $2.25 | - | - | - | - |
| gpt-5.4-nano | $0.10 | $0.01 | - | $0.625 | - | - | - | - |
| gpt-5.4-pro | $15.00 | - | - | $90.00 | $30.00 | - | - | $135.00 |

<transcription_json>
{"table_type":"data_table","title":"Flagship models — Prices per 1M tokens (Short context and Long context)","unit":"USD per 1M tokens","columns":["Model","Short_Input","Short_Cached_input","Short_Cache_writes","Short_Output","Long_Input","Long_Cached_input","Long_Cache_writes","Long_Output"],"data":[{"Model":"gpt-5.6-sol","Short_Input":2.50,"Short_Cached_input":0.25,"Short_Cache_writes":3.125,"Short_Output":15.00,"Long_Input":5.00,"Long_Cached_input":0.50,"Long_Cache_writes":6.25,"Long_Output":22.50},{"Model":"gpt-5.6-terra","Short_Input":1.00,"Short_Cached_input":0.10,"Short_Cache_writes":1.25,"Short_Output":6.00,"Long_Input":2.00,"Long_Cached_input":0.20,"Long_Cache_writes":2.50,"Long_Output":9.00},{"Model":"gpt-5.6-luna","Short_Input":0.10,"Short_Cached_input":0.01,"Short_Cache_writes":0.125,"Short_Output":0.60,"Long_Input":0.20,"Long_Cached_input":0.02,"Long_Cache_writes":0.25,"Long_Output":0.90},{"Model":"gpt-5.5","Short_Input":2.50,"Short_Cached_input":0.25,"Short_Cache_writes":null,"Short_Output":15.00,"Long_Input":5.00,"Long_Cached_input":0.50,"Long_Cache_writes":null,"Long_Output":22.50},{"Model":"gpt-5.5-pro","Short_Input":15.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":90.00,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4","Short_Input":1.25,"Short_Cached_input":0.13,"Short_Cache_writes":null,"Short_Output":7.50,"Long_Input":2.50,"Long_Cached_input":0.25,"Long_Cache_writes":null,"Long_Output":11.25},{"Model":"gpt-5.4-mini","Short_Input":0.375,"Short_Cached_input":0.0375,"Short_Cache_writes":null,"Short_Output":2.25,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-nano","Short_Input":0.10,"Short_Cached_input":0.01,"Short_Cache_writes":null,"Short_Output":0.625,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-pro","Short_Input":15.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":90.00,"Long_Input":30.00,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":135.00}]}
</transcription_json>

<transcription_notes>
- Table type: Pricing table for flagship models.
- Context: "Short" and "Long" context columns are separate groups (each group has Input, Cached input, Cache writes, Output).
- Unit: USD per 1M tokens (as displayed on page).
- Dashes ("-") indicate values not provided / not applicable.
- Visual layout: Two grouped column sets (Short context at left of table, Long context at right). Thin vertical separators between groups.
- Colors/Styling: Minimal gray table lines and light-weight font; header row bold. Some model names and prices are emphasized visually by weight.
</transcription_notes>
</transcription_table>

Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency. See our Your data guide for supported regions and processing details.

<!-- Section 2 -->
## Additional models (selected)

<transcription_table>
**Table 2: Additional models — Input / Cached input / Output**

| Model | Input | Cached input | Output |
|-------:|------:|-------------:|-------:|
| gpt-5.2 | $0.875 | $0.0875 | $7.00 |
| gpt-5.2-pro | $10.50 | - | $84.00 |
| gpt-5.1 | $0.625 | $0.0625 | $5.00 |

<transcription_json>
{"table_type":"data_table","title":"Additional models — Input / Cached input / Output","unit":"USD per 1M tokens","columns":["Model","Input","Cached_input","Output"],"data":[{"Model":"gpt-5.2","Input":0.875,"Cached_input":0.0875,"Output":7.00},{"Model":"gpt-5.2-pro","Input":10.50,"Cached_input":null,"Output":84.00},{"Model":"gpt-5.1","Input":0.625,"Cached_input":0.0625,"Output":5.00}]}
</transcription_json>

<transcription_notes>
- Table type: Compact pricing table for select models.
- Dashes ("-") indicate values not provided / not applicable.
</transcription_notes>
</transcription_table>

<transcription_page_footer> Page 1 | OpenAI Developers </transcription_page_footer>
<transcription_page_header>OpenAI Developers | Pricing</transcription_page_header>

# Pricing

<!-- Section 1 -->
<!-- Column 1 -->
- Model catalog

Choose a model
: **Pricing**
: **Model selection**

Text and code
: **Text generation**
: **Code generation**
: **Structured output**

Prompting
: **Overview**
: **Prompt engineering**
: **Citation formatting**
: **Migration guide**
: **Prompt generation**
: **Frontend prompting**

Reasoning
: **Reasoning models**
: **Reasoning best practices**

Images and video
: **Images and vision**

<!-- Column 2 -->
## Flagship models

Our latest models

Prices per 1M tokens.

<!-- Section 2 -->
### Pricing table — flagship models

<transcription_table>
**Table 1: Flagship models — prices per 1M tokens**

| Model | Short context — Input | Short context — Cached input | Short context — Cache writes | Short context — Output | Long context — Input | Long context — Cached input | Long context — Cache writes | Long context — Output |
|-------|----------------------:|-----------------------------:|-----------------------------:|----------------------:|---------------------:|---------------------------:|---------------------------:|---------------------:|
| gpt-5.6-sol | $2.50 | $0.25 | $3.125 | $15.00 | $5.00 | $0.50 | $6.25 | $22.50 |
| gpt-5.6-terra | $1.00 | $0.10 | $1.25 | $6.00 | $2.00 | $0.20 | $2.50 | $9.00 |
| gpt-5.6-luna | $0.10 | $0.01 | $0.125 | $0.60 | $0.20 | $0.02 | $0.25 | $0.90 |
| gpt-5.5 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.5-pro | $15.00 | - | - | $90.00 | - | - | - | - |
| gpt-5.4 | $1.25 | $0.13 | - | $7.50 | $2.50 | $0.25 | - | $11.25 |
| gpt-5.4-mini | $0.375 | $0.0375 | - | $2.25 | - | - | - | - |
| gpt-5.4-nano | $0.10 | $0.01 | - | $0.625 | - | - | - | - |
| gpt-5.4-pro | $15.00 | - | - | $90.00 | $30.00 [unclear: maybe Input?] | [unclear] | - | $135.00 [unclear] |

<transcription_json>
{"table_type":"data_table","title":"Flagship models — prices per 1M tokens","columns":["Model","Short_Input","Short_Cached_input","Short_Cache_writes","Short_Output","Long_Input","Long_Cached_input","Long_Cache_writes","Long_Output"],"data":[{"Model":"gpt-5.6-sol","Short_Input":2.50,"Short_Cached_input":0.25,"Short_Cache_writes":3.125,"Short_Output":15.00,"Long_Input":5.00,"Long_Cached_input":0.50,"Long_Cache_writes":6.25,"Long_Output":22.50},{"Model":"gpt-5.6-terra","Short_Input":1.00,"Short_Cached_input":0.10,"Short_Cache_writes":1.25,"Short_Output":6.00,"Long_Input":2.00,"Long_Cached_input":0.20,"Long_Cache_writes":2.50,"Long_Output":9.00},{"Model":"gpt-5.6-luna","Short_Input":0.10,"Short_Cached_input":0.01,"Short_Cache_writes":0.125,"Short_Output":0.60,"Long_Input":0.20,"Long_Cached_input":0.02,"Long_Cache_writes":0.25,"Long_Output":0.90},{"Model":"gpt-5.5","Short_Input":2.50,"Short_Cached_input":0.25,"Short_Cache_writes":null,"Short_Output":15.00,"Long_Input":5.00,"Long_Cached_input":0.50,"Long_Cache_writes":null,"Long_Output":22.50},{"Model":"gpt-5.5-pro","Short_Input":15.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":90.00,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4","Short_Input":1.25,"Short_Cached_input":0.13,"Short_Cache_writes":null,"Short_Output":7.50,"Long_Input":2.50,"Long_Cached_input":0.25,"Long_Cache_writes":null,"Long_Output":11.25},{"Model":"gpt-5.4-mini","Short_Input":0.375,"Short_Cached_input":0.0375,"Short_Cache_writes":null,"Short_Output":2.25,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-nano","Short_Input":0.10,"Short_Cached_input":0.01,"Short_Cache_writes":null,"Short_Output":0.625,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-pro","Short_Input":15.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":90.00,"Long_Input":"[unclear: 30.00?]","Long_Cached_input":"[unclear]","Long_Cache_writes":null,"Long_Output":"[unclear: 135.00?]"}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- Table is a wide pricing table showing "Short context" and "Long context" columns; each context has: Input, Cached input, Cache writes, Output.
- Dashes ("-") indicate no pricing / not applicable.
- Cells marked "[unclear]" indicate the value in the image was partially occluded or low-resolution; best-guesses are annotated.
- Visual: centered main content, left navigation column, right sidebar. Table lines are subtle grey; active tab in header shows "Batch".
</transcription_notes>
</transcription_table>

<!-- Section 3 -->
### Additional models (lower table, visible portion)

<transcription_table>
**Table 2: Other models — visible rows**

| Model | Input | Cached input | Output |
|-------|------:|-------------:|-------:|
| gpt-5.2 | $0.875 | $0.0875 | $7.00 |
| gpt-5.2-pro | $10.50 | - | $84.00 |
| gpt-5.1 | $0.625 | $0.0625 | $5.00 |

<transcription_json>
{"table_type":"data_table","title":"Other models — visible rows","columns":["Model","Input","Cached_input","Output"],"data":[{"Model":"gpt-5.2","Input":0.875,"Cached_input":0.0875,"Output":7.00},{"Model":"gpt-5.2-pro","Input":10.50,"Cached_input":null,"Output":84.00},{"Model":"gpt-5.1","Input":0.625,"Cached_input":0.0625,"Output":5.00}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- This smaller table appears further down the page; only the top rows are visible in the screenshot.
- Units: USD per 1M tokens.
- Visual: subtle horizontal separators between rows; left-most column lists model names.
</transcription_notes>
</transcription_table>

<!-- Section 4 -->
Notes:
: Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency. See our Your data guide for supported regions and processing details.

<!-- Sidebar (right) -->
> **Sidebar: Flagship models**
> Multimodal models
> Tools
> Specialized models
> Finetuning
> [Copy Page]

<transcription_page_footer>Page 1 | OpenAI Developers</transcription_page_footer>
<transcription_page_header> OpenAI Developers | Pricing </transcription_page_header>

# Pricing

## Flagship models

Our latest models  
Prices per 1M tokens.

<!-- Section 1 -->
<!-- Column 1 -->
- Model catalog
- Choose a model
  - Pricing
  - Model selection

- Text and code
  - Text generation
  - Code generation
  - Structured output

- Prompting
  - Overview
  - Prompt engineering
  - Citation formatting
  - Migration guide
  - Prompt generation
  - Frontend prompting

<!-- Column 2 -->
**Pricing**

**Flagship models**

Our latest models

Prices per 1M tokens.

<!-- Section 2 -->
<!-- Column 1 -->
> **Table controls:** Standard | **Batch** | Flex | Fast mode

<!-- Column 2 -->
<transcription_table>
**Table 1: Flagship models — Prices per 1M tokens**

| Model | Short context — Input | Short context — Cached input | Short context — Cache writes | Short context — Output | Long context — Input | Long context — Cached input | Long context — Cache writes | Long context — Output |
|-------|----------------------:|-----------------------------:|-----------------------------:|----------------------:|---------------------:|---------------------------:|---------------------------:|---------------------:|
| gpt-5.6-sol | $2.50 | $0.25 | $3.125 | $15.00 | $5.00 | $0.50 | $6.25 | $22.50 |
| gpt-5.6-terra | $1.00 | $0.10 | $1.25 | $6.00 | $2.00 | $0.20 | $2.50 | $9.00 |
| gpt-5.6-luna | $0.10 | $0.01 | $0.125 | $0.60 | $0.20 | $0.02 | $0.25 | $0.90 |
| gpt-5.5 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.5-pro | $15.00 | - | - | $90.00 | - | - | - | - |
| gpt-5.4 | $1.25 | $0.13 | - | $7.50 | $2.50 | $0.25 | - | $11.25 |
| gpt-5.4-mini | $0.375 | $0.0375 | - | $2.25 | - | - | - | - |
| gpt-5.4-nano | $0.10 | $0.01 | - | $0.625 | - | - | - | - |
| gpt-5.4-pro | $15.00 | - | - | $90.00 | $30.00 | - | - | $135.00 |

<transcription_json>
{"table_type":"data_table","title":"Flagship models — Prices per 1M tokens","columns":["Model","Short context — Input","Short context — Cached input","Short context — Cache writes","Short context — Output","Long context — Input","Long context — Cached input","Long context — Cache writes","Long context — Output"],"data":[{"Model":"gpt-5.6-sol","ShortInput":2.50,"ShortCachedInput":0.25,"ShortCacheWrites":3.125,"ShortOutput":15.00,"LongInput":5.00,"LongCachedInput":0.50,"LongCacheWrites":6.25,"LongOutput":22.50},{"Model":"gpt-5.6-terra","ShortInput":1.00,"ShortCachedInput":0.10,"ShortCacheWrites":1.25,"ShortOutput":6.00,"LongInput":2.00,"LongCachedInput":0.20,"LongCacheWrites":2.50,"LongOutput":9.00},{"Model":"gpt-5.6-luna","ShortInput":0.10,"ShortCachedInput":0.01,"ShortCacheWrites":0.125,"ShortOutput":0.60,"LongInput":0.20,"LongCachedInput":0.02,"LongCacheWrites":0.25,"LongOutput":0.90},{"Model":"gpt-5.5","ShortInput":2.50,"ShortCachedInput":0.25,"ShortCacheWrites":null,"ShortOutput":15.00,"LongInput":5.00,"LongCachedInput":0.50,"LongCacheWrites":null,"LongOutput":22.50},{"Model":"gpt-5.5-pro","ShortInput":15.00,"ShortCachedInput":null,"ShortCacheWrites":null,"ShortOutput":90.00,"LongInput":null,"LongCachedInput":null,"LongCacheWrites":null,"LongOutput":null},{"Model":"gpt-5.4","ShortInput":1.25,"ShortCachedInput":0.13,"ShortCacheWrites":null,"ShortOutput":7.50,"LongInput":2.50,"LongCachedInput":0.25,"LongCacheWrites":null,"LongOutput":11.25},{"Model":"gpt-5.4-mini","ShortInput":0.375,"ShortCachedInput":0.0375,"ShortCacheWrites":null,"ShortOutput":2.25,"LongInput":null,"LongCachedInput":null,"LongCacheWrites":null,"LongOutput":null},{"Model":"gpt-5.4-nano","ShortInput":0.10,"ShortCachedInput":0.01,"ShortCacheWrites":null,"ShortOutput":0.625,"LongInput":null,"LongCachedInput":null,"LongCacheWrites":null,"LongOutput":null},{"Model":"gpt-5.4-pro","ShortInput":15.00,"ShortCachedInput":null,"ShortCacheWrites":null,"ShortOutput":90.00,"LongInput":30.00,"LongCachedInput":null,"LongCacheWrites":null,"LongOutput":135.00}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- Layout: central content column contains the pricing table with two grouped column sets: "Short context" and "Long context".
- Controls above table show view modes: Standard | Batch (selected) | Flex | Fast mode.
- Dashes "-" indicate no applicable price or not offered.
- Colors: table headers light grey; selected "Batch" control darker.
- Source: OpenAI Developers pricing page (screenshot). The table lists prices per 1,000,000 tokens (USD).
- Visual: three-column page layout visible (left nav, center content, right sidebar).
</transcription_notes>
</transcription_table>

<!-- Section 3 -->
<!-- Column 1 -->
Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency. See our Your data guide for supported regions and processing details.

<!-- Column 2 -->
<transcription_table>
**Table 2: Additional models — Prices per 1M tokens (excerpt lower on page)**

| Model | Input | Cached input | Output |
|-------|------:|-------------:|-------:|
| gpt-5.2 | $0.875 | $0.0875 | $7.00 |
| gpt-5.2-pro | $10.50 | - | $84.00 |
| gpt-5.1 | $0.625 | $0.0625 | $5.00 |

<transcription_json>
{"table_type":"data_table","title":"Additional models — Prices per 1M tokens (excerpt)","columns":["Model","Input","Cached input","Output"],"data":[{"Model":"gpt-5.2","Input":0.875,"CachedInput":0.0875,"Output":7.00},{"Model":"gpt-5.2-pro","Input":10.50,"CachedInput":null,"Output":84.00},{"Model":"gpt-5.1","Input":0.625,"CachedInput":0.0625,"Output":5.00}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- This lower excerpted table is partially visible in the screenshot; values transcribed where legible.
- Dashes "-" denote empty/not listed fields.
</transcription_notes>
</transcription_table>

<!-- Decorative: navigation links, page chrome, and right sidebar (Flagship models, Multimodal models, Tools, Specialized models, Finetuning) --> 

<transcription_page_footer> Page 1 | OpenAI Developers </transcription_page_footer>
<transcription_page_header> OpenAI Developers | Pricing </transcription_page_header>

# Pricing

<!-- Section 1 -->
<!-- Column 1 -->
- Model catalog
- Choose a model
  - Pricing
  - Model selection

- Text and code
  - Text generation
  - Code generation
  - Structured output

- Prompting
  - Overview
  - Prompt engineering
  - Citation formatting
  - Migration guide
  - Prompt generation
  - Frontend prompting

- Reasoning
  - Reasoning models
  - Reasoning best practices

- Images and video
  - Images and vision

<!-- Column 2 -->
## Flagship models

Our latest models

Prices per 1M tokens.

<transcription_table>
**Table 1: Flagship models — Prices per 1M tokens**

| Model | Short — Input | Short — Cached input | Short — Cache writes | Short — Output | Long — Input | Long — Cached input | Long — Cache writes | Long — Output |
|-------|---------------:|---------------------:|---------------------:|---------------:|-------------:|--------------------:|--------------------:|--------------:|
| gpt-5.6-sol | $2.50 | $0.25 | $3.125 | $15.00 | $5.00 | $0.50 | $6.25 | $22.50 |
| gpt-5.6-terra | $1.00 | $0.10 | $1.25 | $6.00 | $2.00 | $0.20 | $2.50 | $9.00 |
| gpt-5.6-luna | $0.10 | $0.01 | $0.125 | $0.60 | $0.20 | $0.02 | $0.25 | $0.90 |
| gpt-5.5 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.5-pro | $15.00 | - | - | $90.00 | - | - | - | - |
| gpt-5.4 | $1.25 | $0.13 | - | $7.50 | $2.50 | $0.25 | - | $11.25 |
| gpt-5.4-mini | $0.375 | $0.0375 | - | $2.25 | - | - | - | - |
| gpt-5.4-nano | $0.10 | $0.01 | - | $0.625 | - | - | - | - |
| gpt-5.4-pro | $15.00 | - | - | $90.00 | $30.00 | - | - | $135.00 |

<transcription_json>
{"table_type":"data_table","title":"Flagship models — Prices per 1M tokens","columns":["Model","Short_Input","Short_Cached_input","Short_Cache_writes","Short_Output","Long_Input","Long_Cached_input","Long_Cache_writes","Long_Output"],"data":[{"Model":"gpt-5.6-sol","Short_Input":2.50,"Short_Cached_input":0.25,"Short_Cache_writes":3.125,"Short_Output":15.00,"Long_Input":5.00,"Long_Cached_input":0.50,"Long_Cache_writes":6.25,"Long_Output":22.50},{"Model":"gpt-5.6-terra","Short_Input":1.00,"Short_Cached_input":0.10,"Short_Cache_writes":1.25,"Short_Output":6.00,"Long_Input":2.00,"Long_Cached_input":0.20,"Long_Cache_writes":2.50,"Long_Output":9.00},{"Model":"gpt-5.6-luna","Short_Input":0.10,"Short_Cached_input":0.01,"Short_Cache_writes":0.125,"Short_Output":0.60,"Long_Input":0.20,"Long_Cached_input":0.02,"Long_Cache_writes":0.25,"Long_Output":0.90},{"Model":"gpt-5.5","Short_Input":2.50,"Short_Cached_input":0.25,"Short_Cache_writes":null,"Short_Output":15.00,"Long_Input":5.00,"Long_Cached_input":0.50,"Long_Cache_writes":null,"Long_Output":22.50},{"Model":"gpt-5.5-pro","Short_Input":15.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":90.00,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4","Short_Input":1.25,"Short_Cached_input":0.13,"Short_Cache_writes":null,"Short_Output":7.50,"Long_Input":2.50,"Long_Cached_input":0.25,"Long_Cache_writes":null,"Long_Output":11.25},{"Model":"gpt-5.4-mini","Short_Input":0.375,"Short_Cached_input":0.0375,"Short_Cache_writes":null,"Short_Output":2.25,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-nano","Short_Input":0.10,"Short_Cached_input":0.01,"Short_Cache_writes":null,"Short_Output":0.625,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-pro","Short_Input":15.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":90.00,"Long_Input":30.00,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":135.00}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- Table spans two context categories: "Short context" and "Long context" (each with Input, Cached input, Cache writes, Output).
- Missing values are shown as "-" in the visual table; represented as null in JSON.
- Visual layout: left column (navigation) is light grey, main content centered with table, right column contains related links. Table gridlines are thin grey lines. Typography: headings bold, body text medium weight.
- Colors: header row text dark grey/black; alternating subtle row separators; currency values right-aligned.
- Source: OpenAI Developers pricing page screenshot.
</transcription_notes>
</transcription_table>

Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency. See our Your data guide for supported regions and processing details.

<!-- Section 2 -->
## Additional model pricing (excerpt)

<transcription_table>
**Table 2: Additional models — Prices per 1M tokens (excerpt)**

| Model | Input | Cached input | Output |
|-------|------:|-------------:|-------:|
| gpt-5.2 | $0.875 | $0.0875 | $7.00 |
| gpt-5.2-pro | $10.50 | - | $84.00 |
| gpt-5.1 | $0.625 | $0.0625 | $5.00 |

<transcription_json>
{"table_type":"data_table","title":"Additional models — Prices per 1M tokens (excerpt)","columns":["Model","Input","Cached_input","Output"],"data":[{"Model":"gpt-5.2","Input":0.875,"Cached_input":0.0875,"Output":7.00},{"Model":"gpt-5.2-pro","Input":10.50,"Cached_input":null,"Output":84.00},{"Model":"gpt-5.1","Input":0.625,"Cached_input":0.0625,"Output":5.00}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- This lower table appears below the flagship table on the page.
- Layout: three columns (Model, Input, Cached input, Output). Missing cached values shown as "-" visually.
</transcription_notes>
</transcription_table>

<!-- Column 3 -->
- Flagship models
- Multimodal models
- Tools
- Specialized models
- Finetuning

(translucent button) Copy Page

<transcription_page_footer> Page 1 | OpenAI Developers </transcription_page_footer>
<transcription_page_header>OpenAI Developers | Pricing</transcription_page_header>

# Pricing

## Flagship models
Our latest models  
Prices per 1M tokens.

<!-- Section 1 -->
<!-- Column 1 -->
Model catalog

Choose a model
: Pricing
: Model selection

Text and code

Text generation
: Code generation
: Structured output

Prompting
: Overview
: Prompt engineering
: Citation formatting
: Migration guide
: Prompt generation
: Frontend prompting

Reasoning
: Reasoning models
: Reasoning best practices

Images and video
: Images and vision

<!-- Column 2 -->

### Pricing table — Short context / Long context

<transcription_table>
**Flagship models — Prices per 1M tokens (short and long context)**

| Model | Short — Input | Short — Cached input | Short — Cache writes | Short — Output | Long — Input | Long — Cached input | Long — Cache writes | Long — Output |
|-------|---------------:|---------------------:|---------------------:|---------------:|-------------:|--------------------:|--------------------:|--------------:|
| gpt-5.6-sol | $2.50 | $0.25 | $3.125 | $15.00 | $5.00 | $0.50 | $6.25 | $22.50 |
| gpt-5.6-terra | $1.00 | $0.10 | $1.25 | $6.00 | $2.00 | $0.20 | $2.50 | $9.00 |
| gpt-5.6-luna | $0.10 | $0.01 | $0.125 | $0.60 | $0.20 | $0.02 | $0.25 | $0.90 |
| gpt-5.5 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.5-pro | $15.00 | - | - | $90.00 | - | - | - | - |
| gpt-5.4 | $1.25 | $0.13 | - | $7.50 | $2.50 | $0.25 | - | $11.25 |
| gpt-5.4-mini | $0.375 | $0.0375 | - | $2.25 | - | - | - | - |
| gpt-5.4-nano | $0.10 | $0.01 | - | $0.625 | - | - | - | - |
| gpt-5.4-pro | $15.00 | - | - | $90.00 | $[unclear: ~30.00?] | $[unclear: ~30.00?] | $[unclear: ~30.00?] | $135.00 |
</transcription_table>

<transcription_json>
{"table_type":"pricing_table","title":"Flagship models — Prices per 1M tokens (short and long context)","columns":["Model","Short — Input","Short — Cached input","Short — Cache writes","Short — Output","Long — Input","Long — Cached input","Long — Cache writes","Long — Output"],"data":[{"Model":"gpt-5.6-sol","Short — Input":2.50,"Short — Cached input":0.25,"Short — Cache writes":3.125,"Short — Output":15.00,"Long — Input":5.00,"Long — Cached input":0.5,"Long — Cache writes":6.25,"Long — Output":22.5},{"Model":"gpt-5.6-terra","Short — Input":1.00,"Short — Cached input":0.10,"Short — Cache writes":1.25,"Short — Output":6.00,"Long — Input":2.00,"Long — Cached input":0.20,"Long — Cache writes":2.5,"Long — Output":9.00},{"Model":"gpt-5.6-luna","Short — Input":0.10,"Short — Cached input":0.01,"Short — Cache writes":0.125,"Short — Output":0.60,"Long — Input":0.20,"Long — Cached input":0.02,"Long — Cache writes":0.25,"Long — Output":0.90},{"Model":"gpt-5.5","Short — Input":2.50,"Short — Cached input":0.25,"Short — Cache writes":null,"Short — Output":15.00,"Long — Input":5.00,"Long — Cached input":0.5,"Long — Cache writes":null,"Long — Output":22.5},{"Model":"gpt-5.5-pro","Short — Input":15.00,"Short — Cached input":null,"Short — Cache writes":null,"Short — Output":90.00,"Long — Input":null,"Long — Cached input":null,"Long — Cache writes":null,"Long — Output":null},{"Model":"gpt-5.4","Short — Input":1.25,"Short — Cached input":0.13,"Short — Cache writes":null,"Short — Output":7.50,"Long — Input":2.50,"Long — Cached input":0.25,"Long — Cache writes":null,"Long — Output":11.25},{"Model":"gpt-5.4-mini","Short — Input":0.375,"Short — Cached input":0.0375,"Short — Cache writes":null,"Short — Output":2.25,"Long — Input":null,"Long — Cached input":null,"Long — Cache writes":null,"Long — Output":null},{"Model":"gpt-5.4-nano","Short — Input":0.10,"Short — Cached input":0.01,"Short — Cache writes":null,"Short — Output":0.625,"Long — Input":null,"Long — Cached input":null,"Long — Cache writes":null,"Long — Output":null},{"Model":"gpt-5.4-pro","Short — Input":15.00,"Short — Cached input":null,"Short — Cache writes":null,"Short — Output":90.00,"Long — Input":"[unclear: ~30.00?]","Long — Cached input":"[unclear: ~30.00?]","Long — Cache writes":"[unclear: ~30.00?]","Long — Output":135.00}]}
</transcription_json>

<transcription_notes>
- Type: Wide pricing table with two grouped contexts (Short context / Long context).
- Layout details: Leftmost column = Model. Each context group has four columns: Input, Cached input, Cache writes, Output.
- Units: Prices per 1M tokens, USD (values display with $).
- Visual: Thin gridlines, muted grey headers. Rightmost portion partially cut off in image; last row long-context intermediate columns are partially unclear — flagged as [unclear].
- Source area: "Standard | Batch | Flex | Fast mode" toggles visible above the table with "Batch" selected.
</transcription_notes>

<!-- Column 3 -->
> Sidebar: Flagship models
> Multimodal models
> Tools
> Specialized models
> Finetuning
> 
> [ Copy Page ]

---

<!-- Section 2 -->
Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency. See our Your data guide for supported regions and processing details.

<!-- Section 3 -->
### Additional models (lower on page)

<transcription_table>
**Model | Input | Cached input | Output**

| Model | Input | Cached input | Output |
|-------|-----:|-------------:|-------:|
| gpt-5.2 | $0.875 | $0.0875 | $7.00 |
| gpt-5.2-pro | $10.50 | - | $84.00 |
| gpt-5.1 | $0.625 | $0.0625 | $5.00 |
</transcription_table>

<transcription_json>
{"table_type":"data_table","title":"Additional models — sample pricing","columns":["Model","Input","Cached input","Output"],"data":[{"Model":"gpt-5.2","Input":0.875,"Cached input":0.0875,"Output":7.0},{"Model":"gpt-5.2-pro","Input":10.5,"Cached input":null,"Output":84.0},{"Model":"gpt-5.1","Input":0.625,"Cached input":0.0625,"Output":5.0}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- This smaller table appears lower on the page; values visible for a few models.
- Some cells use "-" to indicate not applicable or not listed.
</transcription_notes>

<transcription_page_footer>Page 1 | OpenAI Developers</transcription_page_footer>
<transcription_page_header> Pricing | Flagship models </transcription_page_header>

# Pricing

<!-- Section 1 -->
<!-- Column 1 -->
<!-- Decorative: Left navigation, page chrome, logo, search, top nav (not transcribed) -->

<!-- Column 2 -->
## Flagship models

Our latest models  
Prices per 1M tokens.

**Table: Short context & Long context pricing (prices per 1M tokens)**

<transcription_table>
**Flagship models — Short context / Long context pricing**

| Model | Short: Input | Short: Cached input | Short: Cache writes | Short: Output | Long: Input | Long: Cached input | Long: Cache writes | Long: Output |
|-------|--------------:|-------------------:|--------------------:|--------------:|------------:|-------------------:|-------------------:|-------------:|
| gpt-5.6-sol | $2.50 | $0.25 | $3.125 | $15.00 | $5.00 | $0.50 | $6.25 | $22.50 |
| gpt-5.6-terra | $1.00 | $0.10 | $1.25 | $6.00 | $2.00 | $0.20 | $2.50 | $9.00 |
| gpt-5.6-luna | $0.10 | $0.01 | $0.125 | $0.60 | $0.20 | $0.02 | $0.25 | $0.90 |
| gpt-5.5 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.5-pro | $15.00 | - | - | $90.00 | - | - | - | - |
| gpt-5.4 | $1.25 | $0.13 | - | $7.50 | $2.50 | $0.25 | - | $11.25 |
| gpt-5.4-mini | $0.375 | $0.0375 | - | $2.25 | - | - | - | - |
| gpt-5.4-nano | $0.10 | $0.01 | - | $0.625 | - | - | - | - |
| gpt-5.4-pro | $15.00 | - | - | $90.00 | [unclear] | [unclear] | [unclear] | [unclear] |
</transcription_table>

<transcription_json>
{"table_type":"data_table","title":"Flagship models — Short context / Long context pricing","columns":["Model","Short: Input","Short: Cached input","Short: Cache writes","Short: Output","Long: Input","Long: Cached input","Long: Cache writes","Long: Output"],"data":[{"Model":"gpt-5.6-sol","Short: Input":"$2.50","Short: Cached input":"$0.25","Short: Cache writes":"$3.125","Short: Output":"$15.00","Long: Input":"$5.00","Long: Cached input":"$0.50","Long: Cache writes":"$6.25","Long: Output":"$22.50"},{"Model":"gpt-5.6-terra","Short: Input":"$1.00","Short: Cached input":"$0.10","Short: Cache writes":"$1.25","Short: Output":"$6.00","Long: Input":"$2.00","Long: Cached input":"$0.20","Long: Cache writes":"$2.50","Long: Output":"$9.00"},{"Model":"gpt-5.6-luna","Short: Input":"$0.10","Short: Cached input":"$0.01","Short: Cache writes":"$0.125","Short: Output":"$0.60","Long: Input":"$0.20","Long: Cached input":"$0.02","Long: Cache writes":"$0.25","Long: Output":"$0.90"},{"Model":"gpt-5.5","Short: Input":"$2.50","Short: Cached input":"$0.25","Short: Cache writes":"-","Short: Output":"$15.00","Long: Input":"$5.00","Long: Cached input":"$0.50","Long: Cache writes":"-","Long: Output":"$22.50"},{"Model":"gpt-5.5-pro","Short: Input":"$15.00","Short: Cached input":"-","Short: Cache writes":"-","Short: Output":"$90.00","Long: Input":"-","Long: Cached input":"-","Long: Cache writes":"-","Long: Output":"-"},{"Model":"gpt-5.4","Short: Input":"$1.25","Short: Cached input":"$0.13","Short: Cache writes":"-","Short: Output":"$7.50","Long: Input":"$2.50","Long: Cached input":"$0.25","Long: Cache writes":"-","Long: Output":"$11.25"},{"Model":"gpt-5.4-mini","Short: Input":"$0.375","Short: Cached input":"$0.0375","Short: Cache writes":"-","Short: Output":"$2.25","Long: Input":"-","Long: Cached input":"-","Long: Cache writes":"-","Long: Output":"-"},{"Model":"gpt-5.4-nano","Short: Input":"$0.10","Short: Cached input":"$0.01","Short: Cache writes":"-","Short: Output":"$0.625","Long: Input":"-","Long: Cached input":"-","Long: Cache writes":"-","Long: Output":"-"},{"Model":"gpt-5.4-pro","Short: Input":"$15.00","Short: Cached input":"-","Short: Cache writes":"-","Short: Output":"$90.00","Long: Input":"[unclear]","Long: Cached input":"[unclear]","Long: Cache writes":"[unclear]","Long: Output":"[unclear]"}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- Layout: three-column page: left navigation (catalog), center content (pricing tables), right sidebar (links). Center column contains the flagship models pricing table shown above.
- Table visually has thin separators and muted gray headers. Dashes ("-") indicate not applicable/no price shown.
- Colors: headers and accents use dark gray/black text; selected tab ("Batch") is highlighted; background is white.
- Source location: OpenAI Developers — Models → Pricing page (screenshot cropped to flagship pricing).
- The row for "gpt-5.4-pro" long-context columns are partially cut/unclear in the provided image; values marked [unclear].
</transcription_notes>

<!-- Column 3 -->
<!-- Decorative: Right sidebar with quick links (Flagship models, Multimodal models, Tools, Specialized models, Finetuning) and "Copy Page" button. -->

<!-- Section 2 -->
## Additional models (lower table, partially visible)

<transcription_table>
**Other model pricing (visible portion)**

| Model | Input | Cached input | Output |
|-------|------:|-------------:|-------:|
| gpt-5.2 | $0.875 | $0.0875 | $7.00 |
| gpt-5.2-pro | $10.50 | - | $84.00 |
| gpt-5.1 | $0.625 | $0.0625 | $5.00 |
</transcription_table>

<transcription_json>
{"table_type":"data_table","title":"Other model pricing (visible portion)","columns":["Model","Input","Cached input","Output"],"data":[{"Model":"gpt-5.2","Input":"$0.875","Cached input":"$0.0875","Output":"$7.00"},{"Model":"gpt-5.2-pro","Input":"$10.50","Cached input":"-","Output":"$84.00"},{"Model":"gpt-5.1","Input":"$0.625","Cached input":"$0.0625","Output":"$5.00"}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- This secondary table is lower on the page and only a portion is visible in the screenshot.
- Regional processing (data residency) note appears below the flagship table in smaller text: "Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency. See our Your data guide for supported regions and processing details." (Rendered small; transcribed here as contextual note.)
</transcription_notes>

<transcription_page_footer> Page 1 | OpenAI Developers </transcription_page_footer>
<transcription_page_header>OpenAI Developers | Pricing</transcription_page_header>

# Pricing

<!-- Section 1 -->
<!-- Column 1 -->
Model catalog

Choose a model
: Pricing
: Model selection

Text and code
: Text generation
: Code generation
: Structured output

Prompting
: Overview
: Prompt engineering
: Citation formatting
: Migration guide
: Prompt generation
: Frontend prompting

Reasoning
: Reasoning models
: Reasoning best practices

Images and video
: Images and vision

<!-- Column 2 -->
## Flagship models

Our latest models

Prices per 1M tokens.

<transcription_table>
**Table 1: Flagship models — Prices per 1M tokens (short context vs long context)**

| Model | Short Input | Short Cached input | Short Cache writes | Short Output | Long Input | Long Cached input | Long Cache writes | Long Output |
|-------|-------------:|-------------------:|-------------------:|-------------:|-----------:|------------------:|------------------:|------------:|
| gpt-5.6-sol | $2.50 | $0.25 | $3.125 | $15.00 | $5.00 | $0.50 | $6.25 | $22.50 |
| gpt-5.6-terra | $1.00 | $0.10 | $1.25 | $6.00 | $2.00 | $0.20 | $2.50 | $9.00 |
| gpt-5.6-luna | $0.10 | $0.01 | $0.125 | $0.60 | $0.20 | $0.02 | $0.25 | $0.90 |
| gpt-5.5 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.5-pro | $15.00 | - | - | $90.00 | - | - | - | - |
| gpt-5.4 | $1.25 | $0.13 | - | $7.50 | $2.50 | $0.25 | - | $11.25 |
| gpt-5.4-mini | $0.375 | $0.0375 | - | $2.25 | - | - | - | - |
| gpt-5.4-nano | $0.10 | $0.01 | - | $0.625 | - | - | - | - |
| gpt-5.4-pro | $15.00 | - | - | $90.00 | $30.00 | - | - | [unclear: $135.0?] |

<transcription_json>
{"table_type":"data_table","title":"Flagship models — Prices per 1M tokens","columns":["Model","Short Input","Short Cached input","Short Cache writes","Short Output","Long Input","Long Cached input","Long Cache writes","Long Output"],"data":[{"Model":"gpt-5.6-sol","Short Input":2.5,"Short Cached input":0.25,"Short Cache writes":3.125,"Short Output":15.0,"Long Input":5.0,"Long Cached input":0.5,"Long Cache writes":6.25,"Long Output":22.5},{"Model":"gpt-5.6-terra","Short Input":1.0,"Short Cached input":0.1,"Short Cache writes":1.25,"Short Output":6.0,"Long Input":2.0,"Long Cached input":0.2,"Long Cache writes":2.5,"Long Output":9.0},{"Model":"gpt-5.6-luna","Short Input":0.1,"Short Cached input":0.01,"Short Cache writes":0.125,"Short Output":0.6,"Long Input":0.2,"Long Cached input":0.02,"Long Cache writes":0.25,"Long Output":0.9},{"Model":"gpt-5.5","Short Input":2.5,"Short Cached input":0.25,"Short Cache writes":null,"Short Output":15.0,"Long Input":5.0,"Long Cached input":0.5,"Long Cache writes":null,"Long Output":22.5},{"Model":"gpt-5.5-pro","Short Input":15.0,"Short Cached input":null,"Short Cache writes":null,"Short Output":90.0,"Long Input":null,"Long Cached input":null,"Long Cache writes":null,"Long Output":null},{"Model":"gpt-5.4","Short Input":1.25,"Short Cached input":0.13,"Short Cache writes":null,"Short Output":7.5,"Long Input":2.5,"Long Cached input":0.25,"Long Cache writes":null,"Long Output":11.25},{"Model":"gpt-5.4-mini","Short Input":0.375,"Short Cached input":0.0375,"Short Cache writes":null,"Short Output":2.25,"Long Input":null,"Long Cached input":null,"Long Cache writes":null,"Long Output":null},{"Model":"gpt-5.4-nano","Short Input":0.1,"Short Cached input":0.01,"Short Cache writes":null,"Short Output":0.625,"Long Input":null,"Long Cached input":null,"Long Cache writes":null,"Long Output":null},{"Model":"gpt-5.4-pro","Short Input":15.0,"Short Cached input":null,"Short Cache writes":null,"Short Output":90.0,"Long Input":30.0,"Long Cached input":null,"Long Cache writes":null,"Long Output":"[unclear: 135.0?]"}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- Table spans the main content area; two grouped columns: "Short context" and "Long context" each with Input, Cached input, Cache writes, Output.
- Visual: light-gray grid lines, left-aligned model names, currency values right-aligned; selected tab "Batch" appears above table (toggle among Standard / Batch / Flex / Fast mode) with "Batch" highlighted.
- Dashes ("-") indicate not applicable / not listed for that cell.
- The bottom-right long Output for gpt-5.4-pro is partially cut off in the image; value shown as " $135.0" but last digit/format unclear — marked above as [unclear: $135.0?].
- Colors: page uses black text on white background; table header row labels in bold; no additional chart graphics.
</transcription_notes>
</transcription_table>

Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency. See our Your data guide for supported regions and processing details.

<!-- Section 2 -->
## Other models (excerpt)

<transcription_table>
**Table 2: Additional model pricing (excerpt)**

| Model | Input | Cached input | Output |
|-------|------:|-------------:|-------:|
| gpt-5.2 | $0.875 | $0.0875 | $7.00 |
| gpt-5.2-pro | $10.50 | - | $84.00 |
| gpt-5.1 | $0.625 | $0.0625 | $5.00 |

<transcription_json>
{"table_type":"data_table","title":"Additional model pricing (excerpt)","columns":["Model","Input","Cached input","Output"],"data":[{"Model":"gpt-5.2","Input":0.875,"Cached input":0.0875,"Output":7.0},{"Model":"gpt-5.2-pro","Input":10.5,"Cached input":null,"Output":84.0},{"Model":"gpt-5.1","Input":0.625,"Cached input":0.0625,"Output":5.0}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- This is a lower-page table excerpt showing older-generation model pricing columns: Input, Cached input, Output.
- Values shown in USD per 1M tokens.
</transcription_notes>
</transcription_table>

<!-- Section 3 -->
<!-- Column 1 -->
> Sidebar: Flagship models
> Multimodal models
> Tools
> Specialized models
> Finetuning
>
> [Copy Page]

<transcription_page_footer>Page 1</transcription_page_footer>
<transcription_page_header> Pricing | Models </transcription_page_header>

# Pricing

<!-- Section 1 -->
<!-- Column 1 -->
**Flagship models**

Our latest models

Prices per 1M tokens.

<!-- Column 2 -->
> **Sidebar: Model catalog**
> Choose a model
> : Pricing
> : Model selection
>
> Text and code
> : Text generation
> : Code generation
> : Structured output
>
> Prompting
> : Overview
> : Prompt engineering
> : Citation formatting
> : Migration guide
> : Prompt generation
> : Frontend prompting

<!-- Decorative: logo, top navigation, search, API Dashboard button -->

<transcription_table>
**Table 1: Flagship models (prices per 1M tokens)**

| Model | Short — Input | Short — Cached input | Short — Cache writes | Short — Output | Long — Input | Long — Cached input | Long — Cache writes | Long — Output |
|-------|---------------:|---------------------:|---------------------:|---------------:|-------------:|--------------------:|--------------------:|--------------:|
| gpt-5.6-sol | $2.50 | $0.25 | $3.125 | $15.00 | $5.00 | $0.50 | $6.25 | $22.50 |
| gpt-5.6-terra | $1.00 | $0.10 | $1.25 | $6.00 | $2.00 | $0.20 | $2.50 | $9.00 |
| gpt-5.6-luna | $0.10 | $0.01 | $0.125 | $0.60 | $0.20 | $0.02 | $0.25 | $0.90 |
| gpt-5.5 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.5-pro | $15.00 | - | - | $90.00 | - | - | - | - |
| gpt-5.4 | $1.25 | $0.13 | - | $7.50 | $2.50 | $0.25 | - | $11.25 |
| gpt-5.4-mini | $0.375 | $0.0375 | - | $2.25 | - | - | - | - |
| gpt-5.4-nano | $0.10 | $0.01 | - | $0.625 | - | - | - | - |
| gpt-5.4-pro | $15.00 | - | - | $90.00 | - | - | $30.00 | $135.00 |

<transcription_json>
{"table_type":"data_table","title":"Flagship models (prices per 1M tokens)","columns":["Model","Short_Input","Short_Cached_input","Short_Cache_writes","Short_Output","Long_Input","Long_Cached_input","Long_Cache_writes","Long_Output"],"data":[{"Model":"gpt-5.6-sol","Short_Input":2.50,"Short_Cached_input":0.25,"Short_Cache_writes":3.125,"Short_Output":15.00,"Long_Input":5.00,"Long_Cached_input":0.50,"Long_Cache_writes":6.25,"Long_Output":22.50},{"Model":"gpt-5.6-terra","Short_Input":1.00,"Short_Cached_input":0.10,"Short_Cache_writes":1.25,"Short_Output":6.00,"Long_Input":2.00,"Long_Cached_input":0.20,"Long_Cache_writes":2.50,"Long_Output":9.00},{"Model":"gpt-5.6-luna","Short_Input":0.10,"Short_Cached_input":0.01,"Short_Cache_writes":0.125,"Short_Output":0.60,"Long_Input":0.20,"Long_Cached_input":0.02,"Long_Cache_writes":0.25,"Long_Output":0.90},{"Model":"gpt-5.5","Short_Input":2.50,"Short_Cached_input":0.25,"Short_Cache_writes":null,"Short_Output":15.00,"Long_Input":5.00,"Long_Cached_input":0.50,"Long_Cache_writes":null,"Long_Output":22.50},{"Model":"gpt-5.5-pro","Short_Input":15.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":90.00,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4","Short_Input":1.25,"Short_Cached_input":0.13,"Short_Cache_writes":null,"Short_Output":7.50,"Long_Input":2.50,"Long_Cached_input":0.25,"Long_Cache_writes":null,"Long_Output":11.25},{"Model":"gpt-5.4-mini","Short_Input":0.375,"Short_Cached_input":0.0375,"Short_Cache_writes":null,"Short_Output":2.25,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-nano","Short_Input":0.10,"Short_Cached_input":0.01,"Short_Cache_writes":null,"Short_Output":0.625,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-pro","Short_Input":15.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":90.00,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":30.00,"Long_Output":135.00}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- Table appears centered on page with a horizontal rule and scroll bar at bottom.
- Top-right toggle shows modes: "Standard   Batch   Flex   Fast mode" with "Batch" selected (gray pill).
- Left column is a site navigation (Model catalog) shown as a vertical list; right column is a smaller "Flagship models" mini-navigation.
- Visual style: light background, thin gray grid lines between rows, subtle fonts. Numbers aligned on the right in the original.
- Dashes ("-") indicate not applicable / no listed price.
- Source: OpenAI Developers — Models pricing page (screenshot).
</transcription_notes>
</transcription_table>

<!-- Section 2 -->
**Regional processing note**

Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency. See our Your data guide for supported regions and processing details.

<!-- Section 3 -->
<transcription_table>
**Table 2: Additional models (excerpt)**

| Model | Input | Cached input | Output |
|-------|------:|-------------:|-------:|
| gpt-5.2 | $0.875 | $0.0875 | $7.00 |
| gpt-5.2-pro | $10.50 | - | $84.00 |
| gpt-5.1 | $0.625 | $0.0625 | $5.00 |

<transcription_json>
{"table_type":"data_table","title":"Additional models (excerpt)","columns":["Model","Input","Cached_input","Output"],"data":[{"Model":"gpt-5.2","Input":0.875,"Cached_input":0.0875,"Output":7.00},{"Model":"gpt-5.2-pro","Input":10.50,"Cached_input":null,"Output":84.00},{"Model":"gpt-5.1","Input":0.625,"Cached_input":0.0625,"Output":5.00}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- This lower table is partially visible in the screenshot; included rows are those clearly legible.
- The page continues below (not fully visible in the image).
</transcription_notes>
</transcription_table>

<!-- Section 4 -->
**Notes on transcription**
- Where table cells in the screenshot contain a dash (–), the transcription uses "-" and JSON uses null.
- If any specific value appears unclear when zoomed, it is marked as null in JSON and as "-" or left blank in the Markdown table.
- Decorative elements (logo, top nav, search bar, "API Dashboard" button) are intentionally not transcribed as content. <!-- Decorative: logo, top navigation, search bar, API Dashboard button -->

<transcription_page_footer> Page 1 | OpenAI Developers </transcription_page_footer>
