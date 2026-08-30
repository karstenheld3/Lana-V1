<transcription_page_header>OpenAI Developers | Models</transcription_page_header>

# Compare models

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
<small>< Back to Models</small>

## Model selectors
- Dropdown 1: GPT-5.6 Sol
- Dropdown 2: GPT-5.6 Terra
- Dropdown 3: GPT-5.6 Luna
- Zoom controls (− +) [visual]

<!-- Section 2 -->
Three model cards displayed side-by-side: Sol, Terra, Luna.

<transcription_image>
**Figure 1: GPT-5.6 Sol (model card)**

```ascii
[MODEL CARD - GPT-5.6 Sol]
+---------------------------------------------------------------+
| [IMAGE: left half bright orange sun, right half black space] |
|                          SOL                                  |
+---------------------------------------------------------------+
Frontier model for complex professional work

[ Learn more ]   [ Playground ]

Ratings:
Reasoning: ● ● ● ● ●  (icons)   [unclear: exact icon semantics]
Speed:     ⚡ ⚡ ⚡ ⚡   [unclear: one icon maybe missing]
Input:     [icons: T, image, ...]  [unclear]
Output:    [icons: T, ...]         [unclear]
Reasoning tokens: ✓

PRICING     PER 1M TOKENS
[pricing values not visible in image -> [unclear]]
```

<transcription_json>
{"card_type":"model_card","title":"GPT-5.6 Sol","tagline":"Frontier model for complex professional work","buttons":["Learn more","Playground"],"ratings":{"reasoning":"[icons visible]","speed":"[icons visible]","input":"[icons visible]","output":"[icons visible]","reasoning_tokens":"checked"},"pricing_per_1m_tokens":"[unclear]","visual":{"image_description":"left: bright orange sun, right: black space, large text 'Sol' centered","colors":["orange","black","white"]}}
</transcription_json>

<transcription_notes>
- Type: model card / comparison tile.
- Image: bright orange sun on left blending to black starfield on right with large white "Sol" centered.
- Buttons: outlined "Learn more" (white/outlined) and filled black "Playground".
- Ratings shown as icons (dots for Reasoning, lightning for Speed, small icons for Input/Output). Exact counts for some icons are unclear from image; marked as [unclear] where necessary.
- Pricing row header visible ("PRICING" / "PER 1M TOKENS") but numeric prices not readable.
</transcription_notes>
</transcription_image>

<transcription_image>
**Figure 2: GPT-5.6 Terra (model card)**

```ascii
[MODEL CARD - GPT-5.6 Terra]
+---------------------------------------------------------------+
| [IMAGE: Earth/blue-green planet on dark space background]    |
|                          TERRA                                |
+---------------------------------------------------------------+
GPT-5.6 model that balances intelligence and cost

[ Learn more ]   [ Playground ]

Ratings:
Reasoning: ● ● ● ● ○  (icons)  [unclear: exact filled count]
Speed:     ⚡ ⚡ ⚡ ⚡  (icons)  [unclear]
Input:     [icons: T, image, ...]  [unclear]
Output:    [icons: T, ...]         [unclear]
Reasoning tokens: ✓

PRICING     PER 1M TOKENS
[pricing values not visible in image -> [unclear]]
```

<transcription_json>
{"card_type":"model_card","title":"GPT-5.6 Terra","tagline":"GPT-5.6 model that balances intelligence and cost","buttons":["Learn more","Playground"],"ratings":{"reasoning":"[icons visible]","speed":"[icons visible]","input":"[icons visible]","output":"[icons visible]","reasoning_tokens":"checked"},"pricing_per_1m_tokens":"[unclear]","visual":{"image_description":"Earth globe centered on dark space background with large white 'Terra' text","colors":["blue","green","black","white"]}}
</transcription_json>

<transcription_notes>
- Type: model card / comparison tile.
- Image: photo-like Earth (blue/green) on dark space background with large white "Terra".
- Buttons: outlined "Learn more" and filled black "Playground".
- Ratings shown as icons; exact filled vs empty counts are not fully legible and are marked [unclear].
- Pricing labels visible but numeric values are not legible.
</transcription_notes>
</transcription_image>

<transcription_image>
**Figure 3: GPT-5.6 Luna (model card)**

```ascii
[MODEL CARD - GPT-5.6 Luna]
+---------------------------------------------------------------+
| [IMAGE: grey Moon on black starfield background]              |
|                          LUNA                                 |
+---------------------------------------------------------------+
GPT-5.6 model optimized for cost-sensitive workloads

[ Learn more ]   [ Playground ]

Ratings:
Reasoning: ● ● ● ○ ○  (icons)  [unclear: exact filled count]
Speed:     ⚡ ⚡ ⚡     (icons)  [unclear]
Input:     [icons: T, image, ...]  [unclear]
Output:    [icons: T, ...]         [unclear]
Reasoning tokens: ✓

PRICING     PER 1M TOKENS
[pricing values not visible in image -> [unclear]]
```

<transcription_json>
{"card_type":"model_card","title":"GPT-5.6 Luna","tagline":"GPT-5.6 model optimized for cost-sensitive workloads","buttons":["Learn more","Playground"],"ratings":{"reasoning":"[icons visible]","speed":"[icons visible]","input":"[icons visible]","output":"[icons visible]","reasoning_tokens":"checked"},"pricing_per_1m_tokens":"[unclear]","visual":{"image_description":"grey Moon centered on dark starfield with large white 'Luna' text","colors":["grey","black","white"]}}
</transcription_json>

<transcription_notes>
- Type: model card / comparison tile.
- Image: photographic Moon (grey) on black starfield with large white "Luna".
- Buttons: outlined "Learn more" and filled black "Playground".
- Rating icons (Reasoning, Speed, Input, Output) are present but exact counts/meanings are partially unclear; marked as [unclear].
- Pricing header visible but numeric values not legible in the provided image.
</transcription_notes>
</transcription_image>

<!-- Section 3 -->
Additional details visible under cards (partially cropped in image):
- Rows labeled: Reasoning, Speed, Input, Output, Reasoning tokens.
- Small icons next to Input/Output rows (representing text, images, tools) — specific icon meanings unclear from image.
- Pricing header with "PER 1M TOKENS" visible under each column; specific price numbers not readable.

<transcription_table>
**Table 1: Pricing header visible (numeric values not legible)**

| PRICING | PER 1M TOKENS |
|---------|---------------|
| GPT-5.6 Sol | [unclear] |
| GPT-5.6 Terra | [unclear] |
| GPT-5.6 Luna | [unclear] |

<transcription_json>
{"table_type":"data_table","title":"Pricing header (values not legible)","columns":["PRICING","PER 1M TOKENS"],"data":[{"PRICING":"GPT-5.6 Sol","PER 1M TOKENS":"[unclear]"},{"PRICING":"GPT-5.6 Terra","PER 1M TOKENS":"[unclear]"},{"PRICING":"GPT-5.6 Luna","PER 1M TOKENS":"[unclear]"}],"unit":"per 1M tokens (currency unclear)"}
</transcription_json>

<transcription_notes>
- The pricing table header ("PRICING" / "PER 1M TOKENS") is visible across the three model columns; the numeric price values are not legible in the image provided.
- Visual layout: three equal-width columns, each containing a model card and rating rows.
</transcription_notes>
</transcription_table>

<transcription_page_footer>Page 1 | OpenAI Developers</transcription_page_footer>
<transcription_page_header> Compare models | Models </transcription_page_header>

# Compare models

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
< Models

## Model comparison selector
- Dropdown (left): GPT-5.6 Sol
- Dropdown (center): GPT-5.6 Terra
- Dropdown (right): GPT-5.6 Luna
- Zoom controls: "-"  "+"

<transcription_image>
**Figure 1: Model comparison cards (Sol, Terra, Luna)**

```ascii
[MODEL CARDS - Compare models]

+---------------------------+---------------------------+---------------------------+
|  [IMAGE: Sun]             |  [IMAGE: Earth]          |  [IMAGE: Moon]           |
|       SOL                 |       TERRA              |       LUNA               |
|                           |                          |                          |
| Frontier model for        | GPT-5.6 model that       | GPT-5.6 model optimized  |
| complex professional work | balances intelligence    | for cost-sensitive       |
|                           | and cost                 | workloads                |
|                           |                          |                          |
| [ Learn more ]   [Playground]  [ Learn more ]   [Playground]  [ Learn more ]  [Playground] |
|                           |                          |                          |
| Reasoning: ● ● ● ● ●      | Reasoning: ● ● ● ● ○    | Reasoning: ● ● ● ○ ○    |
| Speed:     ⚡ ⚡ ⚡ ⚡      | Speed:     ⚡ ⚡ ⚡ ⚡      | Speed:     ⚡ ⚡ ⚡ ○      |
| Input:     [T][IMG][🔇]?   | Input:     [T][IMG][🔇]?  | Input:     [T][IMG][🔇]? |
| Output:    [T][IMG][🔇]?   | Output:    [T][IMG][🔇]?  | Output:    [T][IMG][🔇]? |
| Reasoning tokens: ● (check)| Reasoning tokens: ● (check)| Reasoning tokens: ● (check)|
+---------------------------+---------------------------+---------------------------+
```

<transcription_json>
{"chart_type":"model_cards","title":"Compare models - Sol / Terra / Luna","data":[{"name":"GPT-5.6 Sol","image":"sun (orange/yellow)","tagline":"Frontier model for complex professional work","buttons":["Learn more","Playground"],"ratings":{"reasoning":"5 filled (● ● ● ● ●)","speed":"4 filled (⚡ ⚡ ⚡ ⚡)","input":"icons: text, image, [unclear]","output":"icons: text, image, [unclear]","reasoning_tokens":"enabled (check)"}},{"name":"GPT-5.6 Terra","image":"earth (blue/green)","tagline":"GPT-5.6 model that balances intelligence and cost","buttons":["Learn more","Playground"],"ratings":{"reasoning":"4 filled, 1 outline (● ● ● ● ○) [unclear]","speed":"4 filled (⚡ ⚡ ⚡ ⚡) [unclear]","input":"icons: text, image, [unclear]","output":"icons: text, image, [unclear]","reasoning_tokens":"enabled (check)"}},{"name":"GPT-5.6 Luna","image":"moon (grey)","tagline":"GPT-5.6 model optimized for cost-sensitive workloads","buttons":["Learn more","Playground"],"ratings":{"reasoning":"3 filled, 2 outline (● ● ● ○ ○) [unclear]","speed":"3 filled, 1 outline (⚡ ⚡ ⚡ ○) [unclear]","input":"icons: text, image, [unclear]","output":"icons: text, image, [unclear]","reasoning_tokens":"enabled (check)"}}],"notes":"Icon counts for reasoning/speed inferred visually; counts marked [unclear] where not fully legible."}
</transcription_json>

<transcription_notes>
- Type: Three side-by-side model cards for "Sol", "Terra", "Luna".
- Images: Sol = close-up sun (orange/yellow gradient), Terra = Earth (blue/green continents), Luna = Moon (grey surface). Each image spans card width with the model name overlaid in large white text (Sol, Terra, Luna).
- Layout: Each card contains a short tagline, two buttons ("Learn more" — hollow rounded button; "Playground" — filled black rounded button), then a compact feature/ratings table rows (Reasoning, Speed, Input, Output, Reasoning tokens).
- Icons: Reasoning uses circular dot icons (filled vs outline). Speed uses lightning bolts (filled vs outline). Input/Output show small icons (text, image, [unclear small icons indicating modalities like audio or file types]). Reasoning tokens show a small check/indicator icon.
- Colors: Sol card predominantly orange/black; Terra predominantly blue/black; Luna grey/black. Buttons: "Learn more" white/hollow with grey border; "Playground" solid black with white text.
- Confidence: Text taglines are fully legible. Exact counts of filled vs outline icons for some rows inferred visually; where uncertain those fields are marked with [unclear] in JSON.
</transcription_notes>
</transcription_image>

<!-- Section 2 -->
### Model cards — detailed rows (visual, icon-based)
- Reasoning:
  - Sol: 5 filled dots (● ● ● ● ●)
  - Terra: 4 filled + 1 outline (● ● ● ● ○) [unclear]
  - Luna: 3 filled + 2 outline (● ● ● ○ ○) [unclear]
- Speed:
  - Sol: 4 lightning bolts (⚡ ⚡ ⚡ ⚡) [unclear]
  - Terra: 4 lightning bolts (⚡ ⚡ ⚡ ⚡) [unclear]
  - Luna: 3 lightning bolts (⚡ ⚡ ⚡ ○) [unclear]
- Input:
  - All three show small modality icons (Text, Image, and additional small icons). Exact small icons unclear — marked as [unclear] where not certain.
- Output:
  - All three show small modality icons similar to Input. Exact icons unclear.
- Reasoning tokens:
  - All three show indicator (filled circle/check) meaning enabled.

<!-- Decorative: top-left "OpenAI Developers" logo, top nav (Home, API, Codex, ChatGPT, Resources), search and "API Dashboard" button -->

<transcription_page_footer> Page 1 | OpenAI Developers </transcription_page_footer>
<transcription_page_header>OpenAI Developers | Models</transcription_page_header>

# Compare models

<!-- Decorative: OpenAI logo in top-left, top navigation bar (Overview, Models, Agents, Tools, Voice & Audio, Production, API reference), search field, "API Dashboard" button -->

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
<small>< Models</small>

## Model selection controls
- Dropdown (center column): GPT-5.6 Sol
- Dropdown (middle column): GPT-5.6 Terra
- Dropdown (right column): GPT-5.6 Luna
- Zoom controls: -  +

<!-- Section 2 -->
<!-- Column 1 -->
<!-- (left sidebar continues off-screen) -->

<!-- Column 2 -->
### Model cards grid (3 columns)

<transcription_image>
**Figure 1: GPT-5.6 Sol — Model card**

```ascii
[MODEL CARD - SOL]
Dropdown: GPT-5.6 Sol ▾

+---------------------------------------------------------------+
| [Banner image: bright orange sun on left, black space right] |
|                          Sol                                  |
+---------------------------------------------------------------+

Tagline: Frontier model for complex professional work

[Learn more]   [Playground]

Ratings:
Reasoning: ● ● ● ● ●
Speed: ⚡ ⚡ ⚡ ⚡
Input: [T] [img] [file?] [unclear]
Output: [T] [unclear]
Reasoning tokens: ✔

PRICING           PER 1M TOKENS
```

<transcription_json>
{"chart_type":"model_card","title":"GPT-5.6 Sol","data":{"name":"Sol","dropdown_label":"GPT-5.6 Sol","tagline":"Frontier model for complex professional work","buttons":["Learn more","Playground"],"banner":{"description":"bright orange sun on left, black space on right with large 'Sol' text","colors":["orange","#000000"]},"ratings":{"reasoning":{"icons":"dots","value":"[unclear: appears as 5 filled dots]"},"speed":{"icons":"lightning","value":"[unclear: appears as 4 lightnings]"},"input":{"icons":["T","image","[unclear]"],"notes":"small icons; some unclear"},"output":{"icons":["T","[unclear]"],"notes":"icons partially obscured"},"reasoning_tokens":"present (checkmark)"},"pricing_header":"PRICING PER 1M TOKENS"}}
</transcription_json>

<transcription_notes>
- Type: Model card (visual banner + metadata)
- Banner visuals: left side bright yellow-orange sun texture, right side black space with white "Sol" text centered vertically.
- Colors: dominant orange/yellow for sun, black background for space, white text.
- Buttons: rounded pill style; "Learn more" (outlined/white), "Playground" (filled black).
- Ratings use small icons: filled circles for reasoning, lightning bolts for speed, small glyphs for input/output types. Exact counts partially unclear due to image scale — marked with [unclear: ...].
- Location on page: left column of 3-card grid under "Compare models".
</transcription_notes>
</transcription_image>

<transcription_image>
**Figure 2: GPT-5.6 Terra — Model card**

```ascii
[MODEL CARD - TERRA]
Dropdown: GPT-5.6 Terra ▾

+---------------------------------------------------------------+
| [Banner image: Earth globe centered, space background]        |
|                          Terra                                 |
+---------------------------------------------------------------+

Tagline: GPT-5.6 model that balances intelligence and cost

[Learn more]   [Playground]

Ratings:
Reasoning: ● ● ● ● ○
Speed: ⚡ ⚡ ⚡
Input: [T] [img] [unclear]
Output: [T] [unclear]
Reasoning tokens: ✔

PRICING           PER 1M TOKENS
```

<transcription_json>
{"chart_type":"model_card","title":"GPT-5.6 Terra","data":{"name":"Terra","dropdown_label":"GPT-5.6 Terra","tagline":"GPT-5.6 model that balances intelligence and cost","buttons":["Learn more","Playground"],"banner":{"description":"Earth globe centered against black space with 'Terra' white text","colors":["blue","green","#000000"]},"ratings":{"reasoning":{"icons":"dots","value":"[unclear: appears as 4 filled, 1 empty dot]"},"speed":{"icons":"lightning","value":"[unclear: appears as 3 lightnings]"},"input":{"icons":["T","image","[unclear]"],"notes":"input/output glyphs visible but small"},"output":{"icons":["T","[unclear]"]},"reasoning_tokens":"present (checkmark)"},"pricing_header":"PRICING PER 1M TOKENS"}}
</transcription_json>

<transcription_notes>
- Type: Model card (visual banner + metadata)
- Banner visuals: realistic Earth photo, illuminated continents, space background; large white "Terra" text centered.
- Buttons same style as Sol card.
- Ratings: similar iconography to other cards; counts estimated visually and marked [unclear] where not certain.
- Visual alignment: middle card of 3-card grid.
</transcription_notes>
</transcription_image>

<transcription_image>
**Figure 3: GPT-5.6 Luna — Model card**

```ascii
[MODEL CARD - LUNA]
Dropdown: GPT-5.6 Luna ▾

+---------------------------------------------------------------+
| [Banner image: gray moon on black space]                      |
|                          Luna                                 |
+---------------------------------------------------------------+

Tagline: GPT-5.6 model optimized for cost-sensitive workloads

[Learn more]   [Playground]

Ratings:
Reasoning: ● ● ● ○ ○
Speed: ⚡ ⚡ ⚡ ⚡
Input: [T] [img?] [unclear]
Output: [T] [unclear]
Reasoning tokens: ✔

PRICING           PER 1M TOKENS
```

<transcription_json>
{"chart_type":"model_card","title":"GPT-5.6 Luna","data":{"name":"Luna","dropdown_label":"GPT-5.6 Luna","tagline":"GPT-5.6 model optimized for cost-sensitive workloads","buttons":["Learn more","Playground"],"banner":{"description":"grayscale moon image on black space with 'Luna' white text","colors":["gray","#000000"]},"ratings":{"reasoning":{"icons":"dots","value":"[unclear: appears as 3 filled, 2 empty dots]"},"speed":{"icons":"lightning","value":"[unclear: appears as 4 lightnings]"},"input":{"icons":["T","[unclear]","[unclear]"],"notes":"icons not fully legible"},"output":{"icons":["T","[unclear]"]},"reasoning_tokens":"present (checkmark)"},"pricing_header":"PRICING PER 1M TOKENS"}}
</transcription_json>

<transcription_notes>
- Type: Model card (visual banner + metadata)
- Banner visuals: moon texture (grayscale), black starfield background, large white "Luna" text centered.
- Buttons and layout match the Sol and Terra cards.
- Ratings icons and small input/output glyphs are present but small; counts and some glyph meanings uncertain and annotated as [unclear].
- Visual: rightmost card of the 3-card grid.
</transcription_notes>
</transcription_image>

<!-- Section 3 -->
### Ratings and attribute rows (shared visual style under each model card)
- Attribute rows visible for each model (vertically aligned under each card):
  - Reasoning
    : icons (filled/empty circles) indicate strength; counts visually: Sol appears strongest, Terra medium, Luna lower — exact counts [unclear]
  - Speed
    : lightning bolt icons indicate speed; Sol/Terra/Luna show multiple bolts; exact counts [unclear]
  - Input
    : small glyphs for input types (Text icon "T", image icon, others) — some glyphs unclear
  - Output
    : small glyphs similar to Input; partially unclear
  - Reasoning tokens
    : checkmark present for visible models

<!-- Section 4 -->
### Pricing header (visible but numbers not captured in screenshot)
- Visible heading text: PRICING    PER 1M TOKENS
- No numeric pricing visible in cropped image area (off-screen or below fold)

<!-- transcription_page_footer -->
<transcription_page_footer>Page 1 | OpenAI Developers</transcription_page_footer>
