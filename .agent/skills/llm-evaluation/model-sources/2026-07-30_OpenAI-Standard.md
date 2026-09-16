<transcription_page_header>OpenAI Developers | Models — Pricing</transcription_page_header>

# Pricing

<!-- Section 1 -->
<!-- Column 1 -->
**Flagship models**

Our latest models

Prices per 1M tokens.

<!-- Column 2 -->
(Primary content: pricing table for flagship models with short and long context pricing)

<!-- Section 2 -->
Sidebar (navigation omitted; see notes)

---

<transcription_table>
**Table 1: Flagship models — Prices per 1M tokens (Short context and Long context)**

| Model | Short — Input | Short — Cached input | Short — Cache writes | Short — Output | Long — Input | Long — Cached input | Long — Cache writes | Long — Output |
|-------|---------------:|---------------------:|---------------------:|---------------:|-------------:|--------------------:|--------------------:|--------------:|
| gpt-5.6-sol | $5.00 | $0.50 | $6.25 | $30.00 | $10.00 | $1.00 | $12.50 | $45.00 |
| gpt-5.6-terra | $2.00 | $0.20 | $2.50 | $12.00 | $4.00 | $0.40 | $5.00 | $18.00 |
| gpt-5.6-luna | $0.20 | $0.02 | $0.25 | $1.20 | $0.40 | $0.04 | $0.50 | $1.80 |
| gpt-5.5 | $5.00 | $0.50 | - | $30.00 | $10.00 | $1.00 | - | $45.00 |
| gpt-5.5-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | $270.00 |
| gpt-5.4 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.4-mini | $0.75 | $0.075 | - | $4.50 | - | - | - | - |
| gpt-5.4-nano | $0.20 | $0.02 | - | $1.25 | - | - | - | - |
| gpt-5.4-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | $270.00 |

<transcription_json>
{"table_type":"data_table","title":"Flagship models — Prices per 1M tokens (Short context and Long context)","columns":["Model","Short_Input","Short_Cached_input","Short_Cache_writes","Short_Output","Long_Input","Long_Cached_input","Long_Cache_writes","Long_Output"],"data":[{"Model":"gpt-5.6-sol","Short_Input":5.00,"Short_Cached_input":0.50,"Short_Cache_writes":6.25,"Short_Output":30.00,"Long_Input":10.00,"Long_Cached_input":1.00,"Long_Cache_writes":12.50,"Long_Output":45.00},{"Model":"gpt-5.6-terra","Short_Input":2.00,"Short_Cached_input":0.20,"Short_Cache_writes":2.50,"Short_Output":12.00,"Long_Input":4.00,"Long_Cached_input":0.40,"Long_Cache_writes":5.00,"Long_Output":18.00},{"Model":"gpt-5.6-luna","Short_Input":0.20,"Short_Cached_input":0.02,"Short_Cache_writes":0.25,"Short_Output":1.20,"Long_Input":0.40,"Long_Cached_input":0.04,"Long_Cache_writes":0.50,"Long_Output":1.80},{"Model":"gpt-5.5","Short_Input":5.00,"Short_Cached_input":0.50,"Short_Cache_writes":null,"Short_Output":30.00,"Long_Input":10.00,"Long_Cached_input":1.00,"Long_Cache_writes":null,"Long_Output":45.00},{"Model":"gpt-5.5-pro","Short_Input":30.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":180.00,"Long_Input":60.00,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":270.00},{"Model":"gpt-5.4","Short_Input":2.50,"Short_Cached_input":0.25,"Short_Cache_writes":null,"Short_Output":15.00,"Long_Input":5.00,"Long_Cached_input":0.50,"Long_Cache_writes":null,"Long_Output":22.50},{"Model":"gpt-5.4-mini","Short_Input":0.75,"Short_Cached_input":0.075,"Short_Cache_writes":null,"Short_Output":4.50,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-nano","Short_Input":0.20,"Short_Cached_input":0.02,"Short_Cache_writes":null,"Short_Output":1.25,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-pro","Short_Input":30.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":180.00,"Long_Input":60.00,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":270.00}] ,"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- Table type: pricing table for Flagship models.
- Layout: wide table with two grouped contexts: "Short context" and "Long context". Each context shows 4 columns: Input, Cached input, Cache writes, Output.
- Visual cues: the "Short context" and "Long context" group headers sit above their respective columns. Gridlines are light grey. Selected left nav item is "Pricing" (light grey rounded rectangle). Right sidebar lists mirror navigation (Flagship models, Multimodal models, Tools, Specialized models, Finetuning) and a "Copy Page" button.
- Currency: USD (dollars). All values are per 1M tokens.
- Dashes (-) in cells indicate not applicable / not offered; represented as null in JSON.
- Some long context cells for smaller models are blank.
- Source: OpenAI Developers — Models pricing page (screenshot).
</transcription_notes>
</transcription_table>

---

<!-- Section 3 -->
Detailed notes visible on page (exact wording as shown):

Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency. See our Your data guide for supported regions and processing details. OpenAI models in Amazon Bedrock are billed through AWS and may differ from direct OpenAI pricing.

Priority processing was renamed Fast mode on July 30, 2026. You can use either `service_tier: "priority"` or `service_tier: "fast"` in your API requests. Learn more about Fast mode.

---

<transcription_table>
**Table 2: Example (partial) — Older model row visible below**

| Model | Input | Cached input | Output |
|-------|-------:|-------------:|-------:|
| gpt-5.2 | $1.75 | $0.175 | $14.00 |

<transcription_json>
{"table_type":"data_table","title":"Example older model row (partial)","columns":["Model","Input","Cached_input","Output"],"data":[{"Model":"gpt-5.2","Input":1.75,"Cached_input":0.175,"Output":14.00}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- This smaller table is partially visible at the bottom of the screenshot; only one row (gpt-5.2) was fully legible.
</transcription_notes>
</transcription_table>

---

<!-- Decorative: browser UI chrome, site header logo, scrollbars, right side badges --> 

<!-- Section Sidebar -->
<!-- Column 1 -->
Model catalog
- Choose a model
- Pricing (selected)
- Model selection

Text and code
- Text generation
- Code generation
- Structured output

Prompting
- Overview
- Prompt engineering
- Citation formatting
- Migration guide
- Prompt generation
- Frontend prompting

Reasoning
- Reasoning models
- Reasoning best practices

Images and video
- Images and vision

<!-- End Sidebar -->

<transcription_page_footer>Page 1 | OpenAI Developers</transcription_page_footer>
<transcription_page_header>OpenAI Developers | Pricing</transcription_page_header>

# Pricing

<!-- Section 1 -->
<!-- Column 1 -->
- (left navigation; model catalog, choose a model, Pricing selected, etc.)

<!-- Column 2 -->
## Flagship models

Our latest models

Prices per 1M tokens.

> Tabs: Standard (selected) · Batch · Flex · Fast mode

<transcription_table>
**Table 1: Flagship models — Standard pricing**

| Model | Short context — Input | Short context — Cached input | Short context — Cache writes | Short context — Output | Long context — Input | Long context — Cached input | Long context — Cache writes | Long context — Output |
|-------|----------------------:|-----------------------------:|------------------------------:|----------------------:|---------------------:|----------------------------:|---------------------------:|----------------------:|
| gpt-5.6-sol | $5.00 | $0.50 | $6.25 | $30.00 | $10.00 | $1.00 | $12.50 | $45.00 |
| gpt-5.6-terra | $2.00 | $0.20 | $2.50 | $12.00 | $4.00 | $0.40 | $5.00 | $18.00 |
| gpt-5.6-luna | $0.20 | $0.02 | $0.25 | $1.20 | $0.40 | $0.04 | $0.50 | $1.80 |
| gpt-5.5 | $5.00 | $0.50 | - | $30.00 | $10.00 | $1.00 | - | $45.00 |
| gpt-5.5-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | [unclear: $270.0?] |
| gpt-5.4 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.4-mini | $0.75 | $0.075 | - | $4.50 | - | - | - | - |
| gpt-5.4-nano | $0.20 | $0.02 | - | $1.25 | - | - | - | - |
| gpt-5.4-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | [unclear: $270.0?] |

<transcription_json>
{"table_type":"pricing_table","title":"Flagship models — Standard pricing","unit":"USD per 1M tokens","columns":["Model","Short_Input","Short_Cached_input","Short_Cache_writes","Short_Output","Long_Input","Long_Cached_input","Long_Cache_writes","Long_Output"],"data":[{"Model":"gpt-5.6-sol","Short_Input":"$5.00","Short_Cached_input":"$0.50","Short_Cache_writes":"$6.25","Short_Output":"$30.00","Long_Input":"$10.00","Long_Cached_input":"$1.00","Long_Cache_writes":"$12.50","Long_Output":"$45.00"},{"Model":"gpt-5.6-terra","Short_Input":"$2.00","Short_Cached_input":"$0.20","Short_Cache_writes":"$2.50","Short_Output":"$12.00","Long_Input":"$4.00","Long_Cached_input":"$0.40","Long_Cache_writes":"$5.00","Long_Output":"$18.00"},{"Model":"gpt-5.6-luna","Short_Input":"$0.20","Short_Cached_input":"$0.02","Short_Cache_writes":"$0.25","Short_Output":"$1.20","Long_Input":"$0.40","Long_Cached_input":"$0.04","Long_Cache_writes":"$0.50","Long_Output":"$1.80"},{"Model":"gpt-5.5","Short_Input":"$5.00","Short_Cached_input":"$0.50","Short_Cache_writes":"-","Short_Output":"$30.00","Long_Input":"$10.00","Long_Cached_input":"$1.00","Long_Cache_writes":"-","Long_Output":"$45.00"},{"Model":"gpt-5.5-pro","Short_Input":"$30.00","Short_Cached_input":"-","Short_Cache_writes":"-","Short_Output":"$180.00","Long_Input":"$60.00","Long_Cached_input":"-","Long_Cache_writes":"-","Long_Output":"[unclear: $270.0?]"},{"Model":"gpt-5.4","Short_Input":"$2.50","Short_Cached_input":"$0.25","Short_Cache_writes":"-","Short_Output":"$15.00","Long_Input":"$5.00","Long_Cached_input":"$0.50","Long_Cache_writes":"-","Long_Output":"$22.50"},{"Model":"gpt-5.4-mini","Short_Input":"$0.75","Short_Cached_input":"$0.075","Short_Cache_writes":"-","Short_Output":"$4.50","Long_Input":"-","Long_Cached_input":"-","Long_Cache_writes":"-","Long_Output":"-"},{"Model":"gpt-5.4-nano","Short_Input":"$0.20","Short_Cached_input":"$0.02","Short_Cache_writes":"-","Short_Output":"$1.25","Long_Input":"-","Long_Cached_input":"-","Long_Cache_writes":"-","Long_Output":"-"},{"Model":"gpt-5.4-pro","Short_Input":"$30.00","Short_Cached_input":"-","Short_Cache_writes":"-","Short_Output":"$180.00","Long_Input":"$60.00","Long_Cached_input":"-","Long_Cache_writes":"-","Long_Output":"[unclear: $270.0?]"}]}
</transcription_json>

<transcription_notes>
- Table spans center column of page. "Standard" tab is selected (tabs: Standard, Batch, Flex, Fast mode).
- Units: USD, prices are per 1M tokens.
- Dashes ("-") indicate not applicable or not listed.
- Values flagged with [unclear: ...] appear truncated/partially visible in the screenshot (likely $270.00 but image shows $270.0).
- Visual: light table borders, left navigation column on the far left, right sidebar with quick links on the right. Fonts: sans-serif (OpenAI site style).
</transcription_notes>
</transcription_table>

<!-- Section 2 -->
Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency. See our Your data guide for supported regions and processing details. OpenAI models in Amazon Bedrock are billed through AWS and may differ from direct OpenAI pricing.

Priority processing was renamed Fast mode on July 30, 2026. You can use either `service_tier: "priority"` or `service_tier: "fast"` in your API requests. Learn more about Fast mode.

<!-- Section 3 -->
<!-- Column 1 -->
- (right sidebar; links: Flagship models, Multimodal models, Tools, Specialized models, Finetuning — and a "Copy Page" button)

<!-- Section 4 -->
**Additional visible model row (partial, lower on page)**

| Model | Input | Cached input | Output |
|-------|------:|-------------:|-------:|
| gpt-5.2 | $1.75 | $0.175 | $14.00 |

<transcription_json>
{"note":"Additional lower table row partially visible; included as seen.","data":[{"Model":"gpt-5.2","Input":"$1.75","Cached_input":"$0.175","Output":"$14.00"}]}
</transcription_json>

<transcription_page_footer>Page 1 | OpenAI Developers</transcription_page_footer>
<transcription_page_header>OpenAI Developers | Pricing</transcription_page_header>

# Pricing

<!-- Section 1 -->
<!-- Column 1 -->
Model catalog

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

<transcription_table>
**Table 1: Flagship models — Prices per 1M tokens (Short context vs Long context)**

| Model | Short: Input | Short: Cached input | Short: Cache writes | Short: Output | Long: Input | Long: Cached input | Long: Cache writes | Long: Output |
|-------|--------------:|--------------------:|--------------------:|--------------:|------------:|-------------------:|-------------------:|-------------:|
| gpt-5.6-sol | $5.00 | $0.50 | $6.25 | $30.00 | $10.00 | $1.00 | $12.50 | $45.00 |
| gpt-5.6-terra | $2.00 | $0.20 | $2.50 | $12.00 | $4.00 | $0.40 | $5.00 | $18.00 |
| gpt-5.6-luna | $0.20 | $0.02 | $0.25 | $1.20 | $0.40 | $0.04 | $0.50 | $1.80 |
| gpt-5.5 | $5.00 | $0.50 | - | $30.00 | $10.00 | $1.00 | - | $45.00 |
| gpt-5.5-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | $270.0 [unclear] |
| gpt-5.4 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.4-mini | $0.75 | $0.075 | - | $4.50 | - | - | - | - |
| gpt-5.4-nano | $0.20 | $0.02 | - | $1.25 | - | - | - | - |
| gpt-5.4-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | $270.0 [unclear] |

<transcription_json>
{"table_type":"data_table","title":"Flagship models — Prices per 1M tokens (Short context vs Long context)","columns":["Model","Short: Input","Short: Cached input","Short: Cache writes","Short: Output","Long: Input","Long: Cached input","Long: Cache writes","Long: Output"],"data":[{"Model":"gpt-5.6-sol","Short: Input":5.00,"Short: Cached input":0.50,"Short: Cache writes":6.25,"Short: Output":30.00,"Long: Input":10.00,"Long: Cached input":1.00,"Long: Cache writes":12.50,"Long: Output":45.00},{"Model":"gpt-5.6-terra","Short: Input":2.00,"Short: Cached input":0.20,"Short: Cache writes":2.50,"Short: Output":12.00,"Long: Input":4.00,"Long: Cached input":0.40,"Long: Cache writes":5.00,"Long: Output":18.00},{"Model":"gpt-5.6-luna","Short: Input":0.20,"Short: Cached input":0.02,"Short: Cache writes":0.25,"Short: Output":1.20,"Long: Input":0.40,"Long: Cached input":0.04,"Long: Cache writes":0.50,"Long: Output":1.80},{"Model":"gpt-5.5","Short: Input":5.00,"Short: Cached input":0.50,"Short: Cache writes":null,"Short: Output":30.00,"Long: Input":10.00,"Long: Cached input":1.00,"Long: Cache writes":null,"Long: Output":45.00},{"Model":"gpt-5.5-pro","Short: Input":30.00,"Short: Cached input":null,"Short: Cache writes":null,"Short: Output":180.00,"Long: Input":60.00,"Long: Cached input":null,"Long: Cache writes":null,"Long: Output":270.0},{"Model":"gpt-5.4","Short: Input":2.50,"Short: Cached input":0.25,"Short: Cache writes":null,"Short: Output":15.00,"Long: Input":5.00,"Long: Cached input":0.50,"Long: Cache writes":null,"Long: Output":22.50},{"Model":"gpt-5.4-mini","Short: Input":0.75,"Short: Cached input":0.075,"Short: Cache writes":null,"Short: Output":4.50,"Long: Input":null,"Long: Cached input":null,"Long: Cache writes":null,"Long: Output":null},{"Model":"gpt-5.4-nano","Short: Input":0.20,"Short: Cached input":0.02,"Short: Cache writes":null,"Short: Output":1.25,"Long: Input":null,"Long: Cached input":null,"Long: Cache writes":null,"Long: Output":null},{"Model":"gpt-5.4-pro","Short: Input":30.00,"Short: Cached input":null,"Short: Cache writes":null,"Short: Output":180.00,"Long: Input":60.00,"Long: Cached input":null,"Long: Cache writes":null,"Long: Output":270.0}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- Visual layout: central content area with a grouped table showing "Short context" and "Long context" columns for each model.
- Table header grouping: two grouped contexts (Short context / Long context) each with subcolumns: Input, Cached input, Cache writes, Output.
- Colors: page uses light gray separators; table text is dark gray/black. Highlighted tab above table: "Standard" (selected), other tabs: Batch, Flex, Fast mode (unselected).
- Left column is a navigation menu (text-only). Right column contains small navigation links (Flagship models, Multimodal models, Tools, Specialized models, Finetuning) and a "Copy Page" button.
- Two entries show values that were partially obscured/cropped in the source image: gpt-5.5-pro Long: Output and gpt-5.4-pro Long: Output read as "$270.0" in the image. These are marked [unclear] in the table text but are represented as 270.0 in the JSON.
- Dashes "-" indicate an explicit dash in the source (no value).
- Decorative elements not transcribed: top logo/toolbar, page chrome, scrollbars.
</transcription_notes>
</transcription_table>

Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency. See our Your data guide for supported regions and processing details. OpenAI models in Amazon Bedrock are billed through AWS and may differ from direct OpenAI pricing.

Priority processing was renamed Fast mode on July 30, 2026. You can use either service_tier: "priority" or service_tier: "fast" in your API requests. Learn more about Fast mode.

<transcription_table>
**Table 2: Additional model row (partial view lower on page)**

| Model | Input | Cached input | Output |
|-------|------:|-------------:|-------:|
| gpt-5.2 | $1.75 | $0.175 | $14.00 |

<transcription_json>
{"table_type":"data_table","title":"Partial / lower table — model row visible","columns":["Model","Input","Cached input","Output"],"data":[{"Model":"gpt-5.2","Input":1.75,"Cached input":0.175,"Output":14.00}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- This smaller table is visible partially near the bottom of the page (only one model row visible in screenshot: gpt-5.2).
- All numeric values shown are USD per 1M tokens.
</transcription_notes>
</transcription_table>

<!-- Decorative: top-left "OpenAI Developers" logo, top navigation (Home, API, Codex, ChatGPT, Resources), search bar, API Dashboard button, page scrollbars --> 

<transcription_page_footer>Page 1 | OpenAI Developers</transcription_page_footer>
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
**Table 1: Flagship models — Prices per 1M tokens**

| Model | Short — Input | Short — Cached input | Short — Cache writes | Short — Output | Long — Input | Long — Cached input | Long — Cache writes | Long — Output |
|-------|---------------:|---------------------:|---------------------:|---------------:|-------------:|--------------------:|--------------------:|--------------:|
| gpt-5.6-sol | $5.00 | $0.50 | $6.25 | $30.00 | $10.00 | $1.00 | $12.50 | $45.00 |
| gpt-5.6-terra | $2.00 | $0.20 | $2.50 | $12.00 | $4.00 | $0.40 | $5.00 | $18.00 |
| gpt-5.6-luna | $0.20 | $0.02 | $0.25 | $1.20 | $0.40 | $0.04 | $0.50 | $1.80 |
| gpt-5.5 | $5.00 | $0.50 | - | $30.00 | $10.00 | $1.00 | - | $45.00 |
| gpt-5.5-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | $270.0 |
| gpt-5.4 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.4-mini | $0.75 | $0.075 | - | $4.50 | - | - | - | - |
| gpt-5.4-nano | $0.20 | $0.02 | - | $1.25 | - | - | - | - |
| gpt-5.4-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | $270.0 |

<transcription_json>
{"table_type":"data_table","title":"Flagship models — Prices per 1M tokens","columns":["Model","Short — Input","Short — Cached input","Short — Cache writes","Short — Output","Long — Input","Long — Cached input","Long — Cache writes","Long — Output"],"data":[{"Model":"gpt-5.6-sol","Short — Input":5.00,"Short — Cached input":0.50,"Short — Cache writes":6.25,"Short — Output":30.00,"Long — Input":10.00,"Long — Cached input":1.00,"Long — Cache writes":12.50,"Long — Output":45.00},{"Model":"gpt-5.6-terra","Short — Input":2.00,"Short — Cached input":0.20,"Short — Cache writes":2.50,"Short — Output":12.00,"Long — Input":4.00,"Long — Cached input":0.40,"Long — Cache writes":5.00,"Long — Output":18.00},{"Model":"gpt-5.6-luna","Short — Input":0.20,"Short — Cached input":0.02,"Short — Cache writes":0.25,"Short — Output":1.20,"Long — Input":0.40,"Long — Cached input":0.04,"Long — Cache writes":0.50,"Long — Output":1.80},{"Model":"gpt-5.5","Short — Input":5.00,"Short — Cached input":0.50,"Short — Cache writes":null,"Short — Output":30.00,"Long — Input":10.00,"Long — Cached input":1.00,"Long — Cache writes":null,"Long — Output":45.00},{"Model":"gpt-5.5-pro","Short — Input":30.00,"Short — Cached input":null,"Short — Cache writes":null,"Short — Output":180.00,"Long — Input":60.00,"Long — Cached input":null,"Long — Cache writes":null,"Long — Output":270.0},{"Model":"gpt-5.4","Short — Input":2.50,"Short — Cached input":0.25,"Short — Cache writes":null,"Short — Output":15.00,"Long — Input":5.00,"Long — Cached input":0.50,"Long — Cache writes":null,"Long — Output":22.50},{"Model":"gpt-5.4-mini","Short — Input":0.75,"Short — Cached input":0.075,"Short — Cache writes":null,"Short — Output":4.50,"Long — Input":null,"Long — Cached input":null,"Long — Cache writes":null,"Long — Output":null},{"Model":"gpt-5.4-nano","Short — Input":0.20,"Short — Cached input":0.02,"Short — Cache writes":null,"Short — Output":1.25,"Long — Input":null,"Long — Cached input":null,"Long — Cache writes":null,"Long — Output":null},{"Model":"gpt-5.4-pro","Short — Input":30.00,"Short — Cached input":null,"Short — Cache writes":null,"Short — Output":180.00,"Long — Input":60.00,"Long — Cached input":null,"Long — Cache writes":null,"Long — Output":270.0}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- Table spans center column of page; left column is site navigation; right column is contextual links.
- Visual: subtle horizontal grid lines, muted grey header separators. Active nav item "Pricing" has a light rounded highlight.
- Dashes ("-") in the table indicate no price or not applicable; represented as null in JSON.
- Two entries display "$270.0" in the source capture; preserved as-is in table and JSON.
- The table header groups columns into "Short context" (left group) and "Long context" (right group). Each group has Input, Cached input, Cache writes, Output columns.
- Page shows a horizontal scrollbar below the table and thin vertical scrollbar at right.
- Colors: page background white, text dark grey/black; active tab "Models" has an underline. Right sidebar has vertical divider line.
</transcription_notes>
</transcription_table>

<!-- Section 2 -->
<!-- Column 1 -->
Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency. See our Your data guide for supported regions and processing details. OpenAI models in Amazon Bedrock are billed through AWS and may differ from direct OpenAI pricing.

Priority processing was renamed Fast mode on July 30, 2026. You can use either service_tier: "priority" or service_tier: "fast" in your API requests. Learn more about Fast mode.

Model | Input | Cached input | Output
: gpt-5.2 | $1.75 | $0.175 | $14.00
: [remaining table rows not fully visible in capture — [unclear]]

<!-- Section 3 -->
<!-- Column 3 -->
Flagship models
: Multimodal models
: Tools
: Specialized models
: Finetuning

[Copy Page]

<transcription_page_footer>Page 1 | OpenAI Developers</transcription_page_footer>
<transcription_page_header>Pricing | Models</transcription_page_header>

# Pricing

<!-- Section 1 -->
<!-- Column 1 -->
<!-- Decorative: left navigation (Model catalog, Choose a model, Pricing selected), other nav items omitted -->

<!-- Column 2 -->
## Flagship models

Our latest models

Prices per 1M tokens.

<transcription_table>
**Table: Flagship models — Prices per 1M tokens**

| Model | Short — Input | Short — Cached input | Short — Cache writes | Short — Output | Long — Input | Long — Cached input | Long — Cache writes | Long — Output |
|-------|---------------:|---------------------:|---------------------:|---------------:|-------------:|--------------------:|--------------------:|--------------:|
| gpt-5.6-sol | $5.00 | $0.50 | $6.25 | $30.00 | $10.00 | $1.00 | $12.50 | $45.00 |
| gpt-5.6-terra | $2.00 | $0.20 | $2.50 | $12.00 | $4.00 | $0.40 | $5.00 | $18.00 |
| gpt-5.6-luna | $0.20 | $0.02 | $0.25 | $1.20 | $0.40 | $0.04 | $0.50 | $1.80 |
| gpt-5.5 | $5.00 | $0.50 | - | $30.00 | $10.00 | $1.00 | - | $45.00 |
| gpt-5.5-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | $270.0 [unclear] |
| gpt-5.4 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.4-mini | $0.75 | $0.075 | - | $4.50 | - | - | - | - |
| gpt-5.4-nano | $0.20 | $0.02 | - | $1.25 | - | - | - | - |
| gpt-5.4-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | $270.0 [unclear] |

<transcription_json>
{"table_type":"pricing_table","title":"Flagship models — Prices per 1M tokens","unit":"per 1M tokens","columns":["Model","Short_Input","Short_Cached_input","Short_Cache_writes","Short_Output","Long_Input","Long_Cached_input","Long_Cache_writes","Long_Output"],"data":[{"Model":"gpt-5.6-sol","Short_Input":"$5.00","Short_Cached_input":"$0.50","Short_Cache_writes":"$6.25","Short_Output":"$30.00","Long_Input":"$10.00","Long_Cached_input":"$1.00","Long_Cache_writes":"$12.50","Long_Output":"$45.00"},{"Model":"gpt-5.6-terra","Short_Input":"$2.00","Short_Cached_input":"$0.20","Short_Cache_writes":"$2.50","Short_Output":"$12.00","Long_Input":"$4.00","Long_Cached_input":"$0.40","Long_Cache_writes":"$5.00","Long_Output":"$18.00"},{"Model":"gpt-5.6-luna","Short_Input":"$0.20","Short_Cached_input":"$0.02","Short_Cache_writes":"$0.25","Short_Output":"$1.20","Long_Input":"$0.40","Long_Cached_input":"$0.04","Long_Cache_writes":"$0.50","Long_Output":"$1.80"},{"Model":"gpt-5.5","Short_Input":"$5.00","Short_Cached_input":"$0.50","Short_Cache_writes":"-","Short_Output":"$30.00","Long_Input":"$10.00","Long_Cached_input":"$1.00","Long_Cache_writes":"-","Long_Output":"$45.00"},{"Model":"gpt-5.5-pro","Short_Input":"$30.00","Short_Cached_input":"-","Short_Cache_writes":"-","Short_Output":"$180.00","Long_Input":"$60.00","Long_Cached_input":"-","Long_Cache_writes":"-","Long_Output":"$270.0 [unclear]"},{"Model":"gpt-5.4","Short_Input":"$2.50","Short_Cached_input":"$0.25","Short_Cache_writes":"-","Short_Output":"$15.00","Long_Input":"$5.00","Long_Cached_input":"$0.50","Long_Cache_writes":"-","Long_Output":"$22.50"},{"Model":"gpt-5.4-mini","Short_Input":"$0.75","Short_Cached_input":"$0.075","Short_Cache_writes":"-","Short_Output":"$4.50","Long_Input":"-","Long_Cached_input":"-","Long_Cache_writes":"-","Long_Output":"-"},{"Model":"gpt-5.4-nano","Short_Input":"$0.20","Short_Cached_input":"$0.02","Short_Cache_writes":"-","Short_Output":"$1.25","Long_Input":"-","Long_Cached_input":"-","Long_Cache_writes":"-","Long_Output":"-"},{"Model":"gpt-5.4-pro","Short_Input":"$30.00","Short_Cached_input":"-","Short_Cache_writes":"-","Short_Output":"$180.00","Long_Input":"$60.00","Long_Cached_input":"-","Long_Cache_writes":"-","Long_Output":"$270.0 [unclear]"}]}
</transcription_json>

<transcription_notes>
- Table type: Pricing table for "Flagship models".
- Location: Center column of page; left column contains site navigation, right column contains a vertical list of related links and a "Copy Page" control (decorative).
- Visual details: Table has two grouped header sections: "Short context" and "Long context", each with columns Input, Cached input, Cache writes, Output. Values are monetary ($) per 1M tokens.
- UI elements near table: a segmented control with options "Standard", "Batch", "Flex", "Fast mode" (Standard selected).
- Colors: subtle grey gridlines; selected row headers bold. (Exact colors not required.)
- Ambiguities: Two occurrences of a long-context Output shown as "270.0" near the right edge are partially cut off in the image; transcribed as "$270.0 [unclear]". Verify source if exact cents (e.g., $270.00) are required.
- Decorative elements omitted from transcription: top navigation bar, search input, API Dashboard button, and left/right sidebars beyond labels mentioned.
</transcription_notes>
</transcription_table>

<!-- Column 3 -->
<!-- Decorative: right sidebar (Flagship models, Multimodal models, Tools, Specialized models, Finetuning) -->

Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency. See our Your data guide for supported regions and processing details. OpenAI models in Amazon Bedrock are billed through AWS and may differ from direct OpenAI pricing.

Priority processing was renamed Fast mode on July 30, 2026. You can use either `service_tier: "priority"` or `service_tier: "fast"` in your API requests. Learn more about Fast mode.

<transcription_page_footer>Page 1 | OpenAI</transcription_page_footer>
<transcription_page_header> OpenAI Developers | Pricing </transcription_page_header>

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

[Toggle buttons visible: Standard (selected)  Batch  Flex  Fast mode]

<transcription_table>
**Table 1: Flagship models — Prices per 1M tokens**

| Model | Short context — Input | Short context — Cached input | Short context — Cache writes | Short context — Output | Long context — Input | Long context — Cached input | Long context — Cache writes | Long context — Output |
|-------|----------------------:|-----------------------------:|-----------------------------:|----------------------:|---------------------:|---------------------------:|---------------------------:|----------------------:|
| gpt-5.6-sol | $5.00 | $0.50 | $6.25 | $30.00 | $10.00 | $1.00 | $12.50 | $45.00 |
| gpt-5.6-terra | $2.00 | $0.20 | $2.50 | $12.00 | $4.00 | $0.40 | $5.00 | $18.00 |
| gpt-5.6-luna | $0.20 | $0.02 | $0.25 | $1.20 | $0.40 | $0.04 | $0.50 | $1.80 |
| gpt-5.5 | $5.00 | $0.50 | - | $30.00 | $10.00 | $1.00 | - | $45.00 |
| gpt-5.5-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | [unclear: $270.0?] |
| gpt-5.4 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.4-mini | $0.75 | $0.075 | - | $4.50 | - | - | - | - |
| gpt-5.4-nano | $0.20 | $0.02 | - | $1.25 | - | - | - | - |
| gpt-5.4-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | [unclear: $270.0?] |

<transcription_json>
{"table_type":"data_table","title":"Flagship models — Prices per 1M tokens","columns":["Model","Short_Input","Short_Cached_input","Short_Cache_writes","Short_Output","Long_Input","Long_Cached_input","Long_Cache_writes","Long_Output"],"data":[{"Model":"gpt-5.6-sol","Short_Input":5.00,"Short_Cached_input":0.50,"Short_Cache_writes":6.25,"Short_Output":30.00,"Long_Input":10.00,"Long_Cached_input":1.00,"Long_Cache_writes":12.50,"Long_Output":45.00},{"Model":"gpt-5.6-terra","Short_Input":2.00,"Short_Cached_input":0.20,"Short_Cache_writes":2.50,"Short_Output":12.00,"Long_Input":4.00,"Long_Cached_input":0.40,"Long_Cache_writes":5.00,"Long_Output":18.00},{"Model":"gpt-5.6-luna","Short_Input":0.20,"Short_Cached_input":0.02,"Short_Cache_writes":0.25,"Short_Output":1.20,"Long_Input":0.40,"Long_Cached_input":0.04,"Long_Cache_writes":0.50,"Long_Output":1.80},{"Model":"gpt-5.5","Short_Input":5.00,"Short_Cached_input":0.50,"Short_Cache_writes":null,"Short_Output":30.00,"Long_Input":10.00,"Long_Cached_input":1.00,"Long_Cache_writes":null,"Long_Output":45.00},{"Model":"gpt-5.5-pro","Short_Input":30.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":180.00,"Long_Input":60.00,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":"[unclear: 270.0?]"},{"Model":"gpt-5.4","Short_Input":2.50,"Short_Cached_input":0.25,"Short_Cache_writes":null,"Short_Output":15.00,"Long_Input":5.00,"Long_Cached_input":0.50,"Long_Cache_writes":null,"Long_Output":22.50},{"Model":"gpt-5.4-mini","Short_Input":0.75,"Short_Cached_input":0.075,"Short_Cache_writes":null,"Short_Output":4.50,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-nano","Short_Input":0.20,"Short_Cached_input":0.02,"Short_Cache_writes":null,"Short_Output":1.25,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-pro","Short_Input":30.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":180.00,"Long_Input":60.00,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":"[unclear: 270.0?]"}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- Layout: central pricing table showing "Short context" and "Long context" pricing columns (each context has Input, Cached input, Cache writes, Output).
- The "Standard" service tier tab is visually selected in the UI (buttons: Standard, Batch, Flex, Fast mode).
- Dashes ("-") indicate not applicable or not shown for that cell.
- Two rows (gpt-5.5-pro and gpt-5.4-pro) show a long-context Output value that is partially cut/unclear in the image; transcribed as "[unclear: $270.0?]".
- Colors: header row uses darker text; table gridlines are light grey. Right column contains a vertical sidebar with links.
- Source: OpenAI Developers — Models Pricing page (screenshot).
</transcription_notes>
</transcription_table>

<!-- Section 2 -->
<!-- Column 1 -->
> **Sidebar: Flagship models**
> Multimodal models
> Tools
> Specialized models
> Finetuning
> [Copy Page button]

<!-- Column 2 -->
Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency. See our Your data guide for supported regions and processing details. OpenAI models in Amazon Bedrock are billed through AWS and may differ from direct OpenAI pricing.

Priority processing was renamed Fast mode on July 30, 2026. You can use either `service_tier: "priority"` or `service_tier: "fast"` in your API requests. Learn more about Fast mode.

<transcription_page_footer> Page 1 | OpenAI Developers </transcription_page_footer>
<transcription_page_header> OpenAI Developers | Models — Pricing </transcription_page_header>

# Pricing

<!-- Section 1 -->
<!-- Column 1 -->
- Model catalog

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

<!-- Column 3 -->
- Flagship models
- Multimodal models
- Tools
- Specialized models
- Finetuning

<!-- Decorative: OpenAI logo, top navigation, search bar, "API Dashboard" button, right-side icons -->

<!-- Section 2 -->
### Flagship models — Pricing table

<transcription_table>
**Table 1: Flagship models — Prices per 1M tokens (Short context / Long context)**

| Model | Short: Input | Short: Cached input | Short: Cache writes | Short: Output | Long: Input | Long: Cached input | Long: Cache writes | Long: Output |
|-------|--------------:|---------------------:|---------------------:|--------------:|------------:|--------------------:|-------------------:|-------------:|
| gpt-5.6-sol | $5.00 | $0.50 | $6.25 | $30.00 | $10.00 | $1.00 | $12.50 | $45.00 |
| gpt-5.6-terra | $2.00 | $0.20 | $2.50 | $12.00 | $4.00 | $0.40 | $5.00 | $18.00 |
| gpt-5.6-luna | $0.20 | $0.02 | $0.25 | $1.20 | $0.40 | $0.04 | $0.50 | $1.80 |
| gpt-5.5 | $5.00 | $0.50 | - | $30.00 | $10.00 | $1.00 | - | $45.00 |
| gpt-5.5-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | $270.0 |
| gpt-5.4 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.4-mini | $0.75 | $0.075 | - | $4.50 | - | - | - | - |
| gpt-5.4-nano | $0.20 | $0.02 | - | $1.25 | - | - | - | - |
| gpt-5.4-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | $270.0 |

<transcription_json>
{"table_type":"data_table","title":"Flagship models — Prices per 1M tokens (Short context / Long context)","columns":["Model","Short: Input","Short: Cached input","Short: Cache writes","Short: Output","Long: Input","Long: Cached input","Long: Cache writes","Long: Output"],"data":[{"Model":"gpt-5.6-sol","Short: Input":5.00,"Short: Cached input":0.50,"Short: Cache writes":6.25,"Short: Output":30.00,"Long: Input":10.00,"Long: Cached input":1.00,"Long: Cache writes":12.50,"Long: Output":45.00},{"Model":"gpt-5.6-terra","Short: Input":2.00,"Short: Cached input":0.20,"Short: Cache writes":2.50,"Short: Output":12.00,"Long: Input":4.00,"Long: Cached input":0.40,"Long: Cache writes":5.00,"Long: Output":18.00},{"Model":"gpt-5.6-luna","Short: Input":0.20,"Short: Cached input":0.02,"Short: Cache writes":0.25,"Short: Output":1.20,"Long: Input":0.40,"Long: Cached input":0.04,"Long: Cache writes":0.50,"Long: Output":1.80},{"Model":"gpt-5.5","Short: Input":5.00,"Short: Cached input":0.50,"Short: Cache writes":null,"Short: Output":30.00,"Long: Input":10.00,"Long: Cached input":1.00,"Long: Cache writes":null,"Long: Output":45.00},{"Model":"gpt-5.5-pro","Short: Input":30.00,"Short: Cached input":null,"Short: Cache writes":null,"Short: Output":180.00,"Long: Input":60.00,"Long: Cached input":null,"Long: Cache writes":null,"Long: Output":270.0},{"Model":"gpt-5.4","Short: Input":2.50,"Short: Cached input":0.25,"Short: Cache writes":null,"Short: Output":15.00,"Long: Input":5.00,"Long: Cached input":0.50,"Long: Cache writes":null,"Long: Output":22.50},{"Model":"gpt-5.4-mini","Short: Input":0.75,"Short: Cached input":0.075,"Short: Cache writes":null,"Short: Output":4.50,"Long: Input":null,"Long: Cached input":null,"Long: Cache writes":null,"Long: Output":null},{"Model":"gpt-5.4-nano","Short: Input":0.20,"Short: Cached input":0.02,"Short: Cache writes":null,"Short: Output":1.25,"Long: Input":null,"Long: Cached input":null,"Long: Cache writes":null,"Long: Output":null},{"Model":"gpt-5.4-pro","Short: Input":30.00,"Short: Cached input":null,"Short: Cache writes":null,"Short: Output":180.00,"Long: Input":60.00,"Long: Cached input":null,"Long: Cache writes":null,"Long: Output":270.0}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- Type: Pricing table for flagship models.
- Layout: Three-column page: left navigation, main content (table centered), right sidebar with related links and "Copy Page" button.
- Table visually split into two grouped sections: "Short context" (Input, Cached input, Cache writes, Output) and "Long context" (Input, Cached input, Cache writes, Output).
- Selected service tier toggle shows "Standard" highlighted (other options visible: Batch, Flex, Fast mode).
- Missing/unavailable values shown as "-" in the table; represented as null in JSON.
- Repeated large-price rows (gpt-5.5-pro and gpt-5.4-pro) show Long: Output as "$270.0" in the image (transcribed exactly).
- Colors: header text black, table grid light grey, selected tab pill light grey with darker active state. Right sidebar vertical divider visible.
- Source: OpenAI Developers — Models pricing page (screenshot).
</transcription_notes>
</transcription_table>

### Notes

Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, that are eligible for data residency. See our Your data guide for supported regions and processing details. OpenAI models in Amazon Bedrock are billed through AWS and may differ from direct OpenAI pricing.

Priority processing was renamed Fast mode on July 30, 2026. You can use either service_tier: "priority" or service_tier: "fast" in your API requests. Learn more about Fast mode.

<transcription_page_footer> Page 1 | OpenAI Developers </transcription_page_footer>
<transcription_page_header> Pricing | Models </transcription_page_header>

# Pricing

<!-- Section 1 -->
<!-- Column 1 -->
<!-- Decorative: left navigation (Model catalog, Choose a model, Pricing highlighted, Model selection, Text and code menu items, Prompting, Reasoning, Images and video, etc.) -->

<!-- Column 2 -->
## Flagship models

### Our latest models

Prices per 1M tokens.

<transcription_table>
**Table: Flagship models — Prices per 1M tokens**

| Model | Short context — Input | Short context — Cached input | Short context — Cache writes | Short context — Output | Long context — Input | Long context — Cached input | Long context — Cache writes | Long context — Output |
|-------|-----------------------:|------------------------------:|-----------------------------:|------------------------:|---------------------:|----------------------------:|---------------------------:|----------------------:|
| gpt-5.6-sol | $5.00 | $0.50 | $6.25 | $30.00 | $10.00 | $1.00 | $12.50 | $45.00 |
| gpt-5.6-terra | $2.00 | $0.20 | $2.50 | $12.00 | $4.00 | $0.40 | $5.00 | $18.00 |
| gpt-5.6-luna | $0.20 | $0.02 | $0.25 | $1.20 | $0.40 | $0.04 | $0.50 | $1.80 |
| gpt-5.5 | $5.00 | $0.50 | - | $30.00 | $10.00 | $1.00 | - | $45.00 |
| gpt-5.5-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | $270.0 |
| gpt-5.4 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.4-mini | $0.75 | $0.075 | - | $4.50 | - | - | - | - |
| gpt-5.4-nano | $0.20 | $0.02 | - | $1.25 | - | - | - | - |
| gpt-5.4-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | $270.0 |

<transcription_json>
{"table_type":"data_table","title":"Flagship models — Prices per 1M tokens","columns":["Model","Short_Input","Short_Cached_input","Short_Cache_writes","Short_Output","Long_Input","Long_Cached_input","Long_Cache_writes","Long_Output"],"data":[{"Model":"gpt-5.6-sol","Short_Input":5.00,"Short_Cached_input":0.50,"Short_Cache_writes":6.25,"Short_Output":30.00,"Long_Input":10.00,"Long_Cached_input":1.00,"Long_Cache_writes":12.50,"Long_Output":45.00},{"Model":"gpt-5.6-terra","Short_Input":2.00,"Short_Cached_input":0.20,"Short_Cache_writes":2.50,"Short_Output":12.00,"Long_Input":4.00,"Long_Cached_input":0.40,"Long_Cache_writes":5.00,"Long_Output":18.00},{"Model":"gpt-5.6-luna","Short_Input":0.20,"Short_Cached_input":0.02,"Short_Cache_writes":0.25,"Short_Output":1.20,"Long_Input":0.40,"Long_Cached_input":0.04,"Long_Cache_writes":0.50,"Long_Output":1.80},{"Model":"gpt-5.5","Short_Input":5.00,"Short_Cached_input":0.50,"Short_Cache_writes":null,"Short_Output":30.00,"Long_Input":10.00,"Long_Cached_input":1.00,"Long_Cache_writes":null,"Long_Output":45.00},{"Model":"gpt-5.5-pro","Short_Input":30.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":180.00,"Long_Input":60.00,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":270.0},{"Model":"gpt-5.4","Short_Input":2.50,"Short_Cached_input":0.25,"Short_Cache_writes":null,"Short_Output":15.00,"Long_Input":5.00,"Long_Cached_input":0.50,"Long_Cache_writes":null,"Long_Output":22.50},{"Model":"gpt-5.4-mini","Short_Input":0.75,"Short_Cached_input":0.075,"Short_Cache_writes":null,"Short_Output":4.50,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-nano","Short_Input":0.20,"Short_Cached_input":0.02,"Short_Cache_writes":null,"Short_Output":1.25,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-pro","Short_Input":30.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":180.00,"Long_Input":60.00,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":270.0}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- Source: OpenAI Developers — Pricing (Models page).
- Visual layout: three-column page: left navigation (decorative), center content (pricing table), right sidebar (decorative). Table centered with two grouped header sections: "Short context" and "Long context", each with subcolumns: Input, Cached input, Cache writes, Output.
- Colors: header labels and separators in light grey; selected sidebar item "Pricing" highlighted in light grey. Buttons above table show modes: "Standard" selected, "Batch", "Flex", "Fast mode".
- Precision: All monetary values shown with leading "$". Missing/unused entries shown as "-" in the visual table (encoded as null in JSON).
- Note: The rightmost Output values for "gpt-5.5-pro" and "gpt-5.4-pro" appear as "$270.0" in the image (one trailing zero visible).
- Decorative elements omitted from transcription: OpenAI logo/top navigation, left navigation links, right sidebar links, "Copy Page" button, and other UI chrome.
</transcription_notes>
</transcription_table>

<!-- Column 3 -->
<!-- Decorative: right sidebar (Flagship models, Multimodal models, Tools, Specialized models, Finetuning, Copy Page button) -->

<transcription_page_footer> Page 1 | OpenAI Developers </transcription_page_footer>
<transcription_page_header>OpenAI Developers | Models</transcription_page_header>

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
<!-- Main content (center column) -->

## Flagship models

Our latest models

Prices per 1M tokens.

<transcription_table>
**Table 1: Flagship models — Prices per 1M tokens (Short context / Long context)**

| Model | Short — Input | Short — Cached input | Short — Cache writes | Short — Output | Long — Input | Long — Cached input | Long — Cache writes | Long — Output |
|-------|---------------:|--------------------:|---------------------:|---------------:|-------------:|--------------------:|--------------------:|--------------:|
| gpt-5.6-sol | $5.00 | $0.50 | $6.25 | $30.00 | $10.00 | $1.00 | $12.50 | $45.00 |
| gpt-5.6-terra | $2.00 | $0.20 | $2.50 | $12.00 | $4.00 | $0.40 | $5.00 | $18.00 |
| gpt-5.6-luna | $0.20 | $0.02 | $0.25 | $1.20 | $0.40 | $0.04 | $0.50 | $1.80 |
| gpt-5.5 | $5.00 | $0.50 | - | $30.00 | $10.00 | $1.00 | - | $45.00 |
| gpt-5.5-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | $270.0 |
| gpt-5.4 | $2.50 | $0.25 | - | $15.00 | $5.00 | $0.50 | - | $22.50 |
| gpt-5.4-mini | $0.75 | $0.075 | - | $4.50 | - | - | - | - |
| gpt-5.4-nano | $0.20 | $0.02 | - | $1.25 | - | - | - | - |
| gpt-5.4-pro | $30.00 | - | - | $180.00 | $60.00 | - | - | $270.0 |

<transcription_json>
{"table_type":"data_table","title":"Flagship models — Prices per 1M tokens (Short context / Long context)","columns":["Model","Short_Input","Short_Cached_input","Short_Cache_writes","Short_Output","Long_Input","Long_Cached_input","Long_Cache_writes","Long_Output"],"data":[{"Model":"gpt-5.6-sol","Short_Input":5.00,"Short_Cached_input":0.50,"Short_Cache_writes":6.25,"Short_Output":30.00,"Long_Input":10.00,"Long_Cached_input":1.00,"Long_Cache_writes":12.50,"Long_Output":45.00},{"Model":"gpt-5.6-terra","Short_Input":2.00,"Short_Cached_input":0.20,"Short_Cache_writes":2.50,"Short_Output":12.00,"Long_Input":4.00,"Long_Cached_input":0.40,"Long_Cache_writes":5.00,"Long_Output":18.00},{"Model":"gpt-5.6-luna","Short_Input":0.20,"Short_Cached_input":0.02,"Short_Cache_writes":0.25,"Short_Output":1.20,"Long_Input":0.40,"Long_Cached_input":0.04,"Long_Cache_writes":0.50,"Long_Output":1.80},{"Model":"gpt-5.5","Short_Input":5.00,"Short_Cached_input":0.50,"Short_Cache_writes":null,"Short_Output":30.00,"Long_Input":10.00,"Long_Cached_input":1.00,"Long_Cache_writes":null,"Long_Output":45.00},{"Model":"gpt-5.5-pro","Short_Input":30.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":180.00,"Long_Input":60.00,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":270.0},{"Model":"gpt-5.4","Short_Input":2.50,"Short_Cached_input":0.25,"Short_Cache_writes":null,"Short_Output":15.00,"Long_Input":5.00,"Long_Cached_input":0.50,"Long_Cache_writes":null,"Long_Output":22.50},{"Model":"gpt-5.4-mini","Short_Input":0.75,"Short_Cached_input":0.075,"Short_Cache_writes":null,"Short_Output":4.50,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-nano","Short_Input":0.20,"Short_Cached_input":0.02,"Short_Cache_writes":null,"Short_Output":1.25,"Long_Input":null,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":null},{"Model":"gpt-5.4-pro","Short_Input":30.00,"Short_Cached_input":null,"Short_Cache_writes":null,"Short_Output":180.00,"Long_Input":60.00,"Long_Cached_input":null,"Long_Cache_writes":null,"Long_Output":270.0}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- Location: center column, main pricing table titled "Flagship models".
- Header groups: "Short context" (Input, Cached input, Cache writes, Output) and "Long context" (Input, Cached input, Cache writes, Output).
- Prices are labeled "Prices per 1M tokens." Units: USD per 1M tokens.
- Visual cues: table uses vertical separators and subtle grey row dividers; some entries display "-" where not applicable.
- Two entries show "270.0" (gpt-5.5-pro long output and gpt-5.4-pro long output) as rendered on the page.
</transcription_notes>
</transcription_table>

<!-- Column 3 -->
> Sidebar: Models
> Flagship models
> Multimodal models
> Tools
> Specialized models
> Finetuning

<!-- Section 2 -->
Additional visible pricing table (partial, lower on page)

<transcription_table>
**Table 2: Sample row visible further down (partial)**

| Model | Input | Cached input | Output |
|-------|------:|-------------:|-------:|
| gpt-5.2 | $1.75 | $0.175 | $14.00 |

<transcription_json>
{"table_type":"data_table","title":"Sample row visible further down (partial)","columns":["Model","Input","Cached_input","Output"],"data":[{"Model":"gpt-5.2","Input":1.75,"Cached_input":0.175,"Output":14.00}],"unit":"USD per 1M tokens"}
</transcription_json>

<transcription_notes>
- This second table is partially visible near the bottom of the page; only the first row (gpt-5.2) and headers are legible in the screenshot.
</transcription_notes>
</transcription_table>

Regional processing note (visible paragraph under the table in the page image) states that regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026, and references "Your data" guide and OpenAI models in Amazon Bedrock. (Full paragraph text truncated in the image.)

<transcription_page_footer>Page 1 | OpenAI</transcription_page_footer>
