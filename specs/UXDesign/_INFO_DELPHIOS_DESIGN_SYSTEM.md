# INFO: Delphios Design System

**Doc ID**: DLPHS-IN10
**Goal**: Single source of truth for the visual implementation of the Delphios brand across presentations, web applications, and marketing materials
**Timeline**: Created 2026-08-16

**Depends on:**
- `_INFO_DELPHIOS_BRAND.md [DLPHS-IN07]` for brand values, archetype, voice, DO/DONT

**Does not depend on:**
- `ChatGPT_DelphiosPitchDesignSystem.md` (superseded by this document)

## Summary

- Design principle: `[DLPHS-PRINCIPLE]` - calm, precise, engineered. Innovation from clarity, not effects [VERIFIED - pitch slides + brand archetype]
- Color system: 70% neutral / 20% navy / 10% AI blue - blue is scarce and therefore powerful [VERIFIED - pitch slides]
- Typography: Inter font family, semibold for hierarchy, navy default, blue for emphasis only [VERIFIED - tailwind configs + slides]
- Iconography: Phosphor Icons, thin/light weights, navy/blue palette [VERIFIED - S05 NOTES + Slide 14]
- Dual-context system: Same tokens for presentations (16:9) and web apps (responsive) [VERIFIED - implemented in 10 apps + 14 slides]
- Placeholder dependency system: All unknowns tagged with PREFIX-PLACEHOLDER notation for systematic resolution [ASSUMED - not yet tested with real resolution workflow]

**Scope and Coverage**: This document currently covers **presentations (16:9)** and **web applications (lead magnets)**. Sections 1-6 (tokens, principles) are universal and apply to all future formats. Sections 7-16 contain format-specific application rules primarily for web apps and slides. Future formats (Agent Builder, delphios.ai website, PDF reports, print materials) will be added as dedicated sections when those outputs are actively produced.

**Quick Start (new lead magnet app)**:
1. Copy S05 template (shared header, footer, theme, `tailwind.config.js`)
2. Font: Inter (Google Fonts), weights 400/500/600/700
3. Colors: Background `#F7FAFC`, text `#14213A`, accent `#2C5ED6`, border `#C8D6E5`
4. Icons: `@phosphor-icons/react` or `@phosphor-icons/web`, Light weight, navy default
5. One blue element per card/section. 70% neutral / 20% navy / 10% blue.
6. Framework: React (Vite) if wizard/stateful, vanilla if read-display-submit
7. See Section 15.2 for full Tailwind config, Section 16.2 for tech stack details

## Table of Contents

1. [Design Principle](#1-design-principle)
2. [Placeholder Dependency Map](#2-placeholder-dependency-map)
3. [Color System](#3-color-system)
4. [Typography](#4-typography)
5. [Spacing and Layout](#5-spacing-and-layout)
6. [Iconography](#6-iconography)
7. [Components](#7-components)
8. [Chrome: Header and Footer](#8-chrome-header-and-footer)
9. [Information Design Patterns](#9-information-design-patterns)
10. [Page Layout Patterns](#10-page-layout-patterns)
11. [States and Interactions](#11-states-and-interactions)
12. [Writing for UI](#12-writing-for-ui)
13. [Accessibility](#13-accessibility)
14. [Anti-Patterns](#14-anti-patterns)
15. [Design Tokens Reference](#15-design-tokens-reference)
16. [Application Contexts](#16-application-contexts)
17. [Sources](#17-sources)

## 1. Design Principle

**`[DLPHS-PRINCIPLE]`** The "CLEN-CARE-FROM" look: CLear ENgineered, CAlm RElaxed, FResh MOdern. 

The design balances 3 dimensions:
- Precision: Clear, engineered - order, structure and clarity are top priorities.
- Emotion: Calm, relaxed - we implement it with a human feeling as the second priority. No distractions, no dissonances, no noise.
- Innovativeness: Fresh, modern - we are part of the AI revolution. Innovation comes from clarity and reduction, not visual effects. Our design stands out with small innovative details. This is the third priority.


This principle derives from the brand archetype (`[DLPHS-ARCHETYPE]`), brand values (`[DLPHS-VALUES]`), and the three brand pillars: `[DLPHS-PILLAR-FLOW]`, `[DLPHS-PILLAR-RELIABILITY]`, `[DLPHS-PILLAR-SAFETY]` (DLPHS-IN07 Section 2). Every visual decision must pass this test: Does it add information or does it add decoration? If decoration, remove it.

**Design philosophy**:
- Quiet backgrounds, disciplined grids, navy typography
- Blue used surgically - it attracts the eye because it is scarce
- Evidence presented as a system rather than decoration
- One dominant message per view (slide or screen)
- Whitespace as an active design element, not leftover space

**Litmus test**: Does a slide or screen say "controlled, reliable AI infrastructure" or does it say "energetic SaaS startup"? If the latter, redesign. Second test: Does the design support flow (minimal friction, non-distracting, focused on one task) or does it interrupt (noisy, cluttered, demanding attention)? The visual language must feel architectural: quiet, exact, structured, spacious.

**Design origin**: The current visual direction resulted from a structured critique of the V3C pitch deck (see source DLPHS-IN10-SC-CGPT-CRIT). That critique identified five problems in the previous version: too much saturated blue, heavy glow/shadow effects, overuse of bold, slides-as-documents, and logo repetition. Each was resolved in the redesign and codified as rules in this document.

**Key acronyms used in this document:**
- **CTA** - Call-to-Action (buttons or links prompting user action)
- **KPI** - Key Performance Indicator (metric display block)
- **WCAG** - Web Content Accessibility Guidelines
- **ARIA** - Accessible Rich Internet Applications (accessibility attributes)
- **SVG** - Scalable Vector Graphics

## 2. Placeholder Dependency Map

Placeholders mark values not yet confirmed from authoritative source material. Format: `[PREFIX-PLACEHOLDER]` or `[PREFIX-SUBPREFIX-PLACEHOLDER]`.

### 2.1 Prefix Groups

- `LOGO-` = Logo mark, wordmark, safe space, usage rules
- `COLOR-` = Color palette (core + semantic + severity)
- `TYPE-` = Typography (families, sizes, weights)
- `SPACE-` = Spacing scale
- `RADIUS-` = Border radii
- `SHADOW-` = Elevation/shadow values
- `MOTION-` = Transitions, animations, durations
- `LAYOUT-` = Grid, breakpoints, content widths
- `ICON-` = Icon system specifics
- `COMP-` = Component-level values

### 2.2 Dependency Graph

Values flow TOP-DOWN. Changing an upstream value requires updating all downstream dependents.

```
LOGO-BLUE ─────────────────────────────────────────────────────────┐
                                                                   │
COLOR-PRIMARY ◄── Should match or complement LOGO-BLUE             │
  ├──> COLOR-INTERACTIVE (links, CTAs, active states)              │
  ├──> COLOR-EMPHASIS (highlighted numbers, key phrases)           │
  ├──> COMP-BUTTON-PRIMARY-BG                                      │
  ├──> COMP-BADGE-BG                                               │
  ├──> COMP-PROGRESS-FILL                                          │
  ├──> COMP-CARD-HIGHLIGHT-BORDER                                  │
  └──> ICON-ACTIVE-COLOR                                           │
                                                                   │
COLOR-NAVY (primary text) ◄── Derived from LOGO-BLUE darken        │
  ├──> TYPE-COLOR-DEFAULT                                          │
  ├──> ICON-DEFAULT-COLOR                                          │
  ├──> COMP-CARD-TITLE-COLOR                                       │
  ├──> COMP-TABLE-HEADER-COLOR                                     │
  └──> COMP-FOOTER-TEXT-COLOR                                      │
                                                                   │
COLOR-BG (page background)                                         │
  ├──> COMP-CARD-BG (slightly lighter or white)                    │
  ├──> COLOR-BG-HIGHLIGHT (slightly darker tint of COLOR-BG)       │
  └──> COMP-HEADER-BG                                              │
                                                                   │
COLOR-BORDER ◄── Derived from COLOR-BG darken                      │
  ├──> COMP-CARD-BORDER                                            │
  ├──> COMP-INPUT-BORDER                                           │
  ├──> COMP-TABLE-DIVIDER                                          │
  └──> COMP-HEADER-DIVIDER                                         │
                                                                   │
TYPE-BASE-SIZE (16px)                                              │
  ├──> TYPE-SCALE-* (all sizes derived via ratio)                  │
  ├──> COMP-BUTTON-FONT-SIZE                                       │
  ├──> COMP-INPUT-FONT-SIZE                                        │
  └──> COMP-BADGE-FONT-SIZE                                        │
                                                                   │
SPACE-BASE (unit)                                                  │
  ├──> SPACE-SCALE-* (all spacings are multiples)                  │
  ├──> COMP-CARD-PADDING                                           │
  ├──> COMP-BUTTON-PADDING                                         │
  ├──> COMP-INPUT-PADDING                                          │
  ├──> LAYOUT-GUTTER                                               │
  └──> LAYOUT-SECTION-GAP                                          │
                                                                   │
RADIUS-BASE                                                        │
  ├──> COMP-CARD-RADIUS (= RADIUS-BASE * multiplier)               │
  ├──> COMP-BUTTON-RADIUS                                          │
  ├──> COMP-INPUT-RADIUS                                           │
  ├──> COMP-BADGE-RADIUS                                           │
  └──> COMP-MODAL-RADIUS                                           │
                                                                   │
LOGO-WORDMARK-FONT ◄── Independent of UI font                      │
LOGO-SAFE-SPACE ◄── Derived from LOGO-HEIGHT                       │
```

### 2.3 Resolution Protocol

When resolving placeholders:
1. Start with LOGO-* values (brand mark is the immovable anchor)
2. Derive COLOR-PRIMARY from LOGO-BLUE (must harmonize)
3. Derive COLOR-NAVY from LOGO-BLUE (darken to near-black)
4. Set TYPE-BASE-SIZE, SPACE-BASE, RADIUS-BASE (independent foundations)
5. All COMP-* values derive from the above - never set COMP-* without checking upstream

**Rule**: If a COMP-* value contradicts its upstream dependency, the upstream wins. Components adapt to foundations, never the reverse.

### 2.4 Placeholder Registry

All unresolved placeholders in this document. Resolve top-down (LOGO first, then COLOR, then COMP).

**LOGO (4 placeholders):**
- `[LOGO-WORDMARK-FONT]` - Typeface of "Delphios" wordmark. Source: brand asset files (AI, Figma, or font metadata). Independent of UI font.
- `[LOGO-HEIGHT-HEADER]` - Logo height in web app headers. Estimated: 28-36px. Derive: proportional to `[COMP-HEADER-HEIGHT]`.
- `[LOGO-HEIGHT-SLIDE]` - Logo height in presentation headers. Estimated: 24-28px. Source: measure from pitch slides.
- `[LOGO-SAFE-SPACE]` - Minimum clear space around logo. Derive: typically 50-100% of logo height.

**COLOR (0 placeholders - RESOLVED):**
- ~~`[COLOR-PRIMARY-LIGHT]`~~ RESOLVED: `#C3D9F0` - Icon/badge backgrounds, focus rings. Source: DLPHS-IN11, 13 occurrences in pitch deck.
- ~~`[COLOR-PRIMARY-SUBTLE]`~~ RESOLVED: `#EAF3FC` - Badge backgrounds, notification dots. Source: DLPHS-IN11, same value as pitch header bar background.

**TYPE (2 placeholders):**
- `[TYPE-SCALE-RATIO]` - Modular scale ratio. Estimated: 1.25 (Major Third). Source: verify against actual type ramp (sizes already defined explicitly).
- `[TYPE-LETTER-SPACING-HEADING]` - Tracking for headings type-2xl+. Estimated: -0.01em to -0.02em. Source: measure from pitch slides.

**LAYOUT (6 placeholders):**
- `[LAYOUT-MAX-WIDTH]` - Content container max-width. Estimated: 1200px. Source: measure from deployed apps.
- `[LAYOUT-PAGE-MARGIN]` - Desktop horizontal page margin. Estimated: 32-64px (space-8 to space-16). Derive: responsive, scales with viewport.
- `[LAYOUT-BP-SM]` - Mobile breakpoint. Estimated: 640px. Standard Tailwind default.
- `[LAYOUT-BP-MD]` - Tablet breakpoint. Estimated: 768px. Standard Tailwind default.
- `[LAYOUT-BP-LG]` - Desktop breakpoint. Estimated: 1024px. Standard Tailwind default.
- `[LAYOUT-BP-XL]` - Wide desktop breakpoint. Estimated: 1280px. Standard Tailwind default.

**ICON (3 placeholders):**
- `[ICON-REGULAR-USAGE]` - When to use Phosphor Regular weight. Estimated: mid-emphasis UI elements. Source: decide based on visual testing.
- `[ICON-BOLD-USAGE]` - When to use Phosphor Bold weight. Estimated: high-emphasis states, warnings. Source: decide based on visual testing.
- `[ICON-SIZE-3XL]` - Largest icon size for empty states. Estimated: 64-80px. Source: measure from deployed apps.

**RADIUS (3 placeholders):**
- `[RADIUS-SM]` - Small radius (inputs, buttons). Estimated: 6px. Derive: RADIUS-BASE.
- `[RADIUS-MD]` - Medium radius (cards). Estimated: 8-10px. Derive: RADIUS-BASE * 1.5.
- `[RADIUS-LG]` - Large radius (modals). Estimated: 12-16px. Derive: RADIUS-BASE * 2.

**SHADOW (3 placeholders):**
- `[SHADOW-CARD]` - Card elevation. Estimated: `0 1px 3px rgba(0,0,0,0.04)` or none. Source: verify in deployed apps (current apps use border only).
- `[SHADOW-MODAL]` - Modal elevation. Estimated: `0 20px 60px rgba(0,0,0,0.15)`. Source: standard overlay depth.
- `[SHADOW-DROPDOWN]` - Dropdown/popover elevation. Estimated: `0 4px 12px rgba(0,0,0,0.08)`. Source: standard dropdown depth.

**MOTION (4 placeholders):**
- `[MOTION-DURATION-FAST]` - Hover/color transitions. Estimated: 150ms. Industry standard for micro-interactions.
- `[MOTION-DURATION-NORMAL]` - Panel/tab transitions. Estimated: 250ms. Industry standard for UI transitions.
- `[MOTION-DURATION-SLOW]` - Modal/page transitions. Estimated: 350ms. Industry standard for overlays.
- `[MOTION-EASING-DEFAULT]` - Default easing curve. Estimated: `cubic-bezier(0.4, 0, 0.2, 1)`. Material Design standard ease-out.

**COMP (12 placeholders):**
- `[COMP-CARD-RADIUS]` - Card border radius. Estimated: 8-12px. Derive: `[RADIUS-MD]`.
- `[COMP-BUTTON-RADIUS]` - Button border radius. Estimated: 6-8px. Derive: `[RADIUS-SM]`.
- `[COMP-BUTTON-FOCUS-RING]` - Focus ring specification. Estimated: `0 0 0 2px [COLOR-PRIMARY-LIGHT]` offset 2px.
- `[COMP-INPUT-RADIUS]` - Input border radius. Estimated: 6px. Derive: `[RADIUS-SM]`.
- `[COMP-BADGE-RADIUS]` - Badge radius. Value: 9999px (full pill). Already defined, included for completeness.
- `[COMP-BADGE-FREE-BG]` - "Kostenlos" badge background. Estimated: `[COLOR-PRIMARY-SUBTLE]` or green-subtle. Source: decide based on brand tone.
- `[COMP-BADGE-FREE-TEXT]` - "Kostenlos" badge text color. Estimated: COLOR-PRIMARY or green-600. Derive: matches `[COMP-BADGE-FREE-BG]`.
- `[COMP-PROGRESS-HEIGHT]` - Progress bar track height. Estimated: 8px. Source: visual preference.
- `[COMP-MODAL-RADIUS]` - Modal border radius. Estimated: 12-16px. Derive: `[RADIUS-LG]`.
- `[COMP-MODAL-MAX-WIDTH]` - Modal container max-width. Estimated: 560px (standard), 800px (wide).
- `[COMP-ALERT-RADIUS]` - Alert border radius (right corners). Estimated: `[RADIUS-SM]`.
- `[COMP-HEADER-HEIGHT]` - Web app header height. Estimated: 64-72px. Source: measure from deployed apps.
- `[COMP-FOOTER-BG]` - Footer background color. Estimated: COLOR-BG (#F7FAFC) or 1 shade darker.

**A11Y (4 placeholders):**
- `[A11Y-CONTRAST-NAVY-BG]` - #14213A on #F7FAFC. Estimated: >12:1 (AAA). Verify: run through WCAG calculator.
- `[A11Y-CONTRAST-SLATE-BG]` - #536078 on #F7FAFC. Estimated: ~5:1 (AA). Verify: run through WCAG calculator.
- `[A11Y-CONTRAST-PRIMARY-WHITE]` - #2C5ED6 on #FFFFFF. Estimated: ~4.5:1 (AA boundary). Verify: critical - may require slight darkening.
- `[A11Y-CONTRAST-WHITE-PRIMARY]` - #FFFFFF on #2C5ED6. Estimated: same ratio (inverse). Passes if above passes.

**Total: 40 placeholders** (4 LOGO + 0 COLOR + 2 TYPE + 6 LAYOUT + 2 ICON + 3 RADIUS + 3 SHADOW + 4 MOTION + 12 COMP + 4 A11Y)

## 3. Color System

### 3.1 Dual-Context Color Model

The Delphios palette exists in two contexts with deliberately different hex values for the same semantic tokens. Both derive from one brand identity but are optimized for their viewing conditions.

**Why two contexts:**
- **Presentations** are projected in dark rooms, viewed passively at distance. Maximum visual impact, vivid saturation, high contrast between elements.
- **Web applications** are viewed on monitors at arm's length, used interactively for extended periods. Comfort, reduced eye strain, clear interactive boundaries.

**Context selection rule:**
- Writing a pitch deck, marketing material, social card, or brand asset? → Brand Reference values (Section 3.3)
- Building a web app, dashboard, or interactive tool? → App Implementation values (Section 3.2)
- Creating a document template or PDF report? → App Implementation values (screen-optimized)

**Mapping table** (Brand Reference → App Implementation):

- **COLOR-PRIMARY**: `#003EDA` → `#2C5ED6` - Vivid blue fatigues on screens; softer shade comfortable for extended use. App value has better WCAG contrast ratio on white (4.5:1 vs borderline for `#003EDA`). [VERIFIED - DLPHS-IN11 extraction vs BP02 tailwind.config.js]
- **COLOR-NAVY**: `#162444` → `#14213A` - App version slightly deeper for stronger text contrast on light backgrounds. Difference: +2R +3G +10B. [VERIFIED - DLPHS-IN11 vs ChatGPT design system]
- **COLOR-CHROME**: `#283552` → `#283552` - Same in both contexts. Footer taglines, table headers, structural text. Weight between navy and slate. [VERIFIED - DLPHS-IN11, 42 occurrences in pitch]
- **COLOR-SLATE**: `#54637D` → `#536078` - Nearly identical. App version marginally darker for AA contrast on tinted backgrounds. [VERIFIED - DLPHS-IN11 vs BP02 config]
- **COLOR-BG**: `#F5F9FB` → `#F7FAFC` - App version very close to brand value. Light enough for white cards to need border for contrast. [VERIFIED - S05 template 2026-08-16]
- **COLOR-BG-HIGHLIGHT**: `#EAF3FC` → `#E8F0FA` - App version more defined for interactive surfaces (selected rows, hover states). [VERIFIED - DLPHS-IN11 vs BP02 config]
- **COLOR-BORDER**: `#DFE5EB` → `#C8D6E5` - Apps need visible interactive boundaries (clickable cards, form fields). Darker borders = clearer affordance. Pitch borders can be subtler since elements are passive. [VERIFIED - DLPHS-IN11 vs BP02 config]
- **COLOR-BORDER-CARD**: `#D9E0E7` → `#C8D6E5` - Pitch uses a separate darker stroke for card outlines vs divider lines. Apps merge both into one border token. [VERIFIED - DLPHS-IN11]
- **COLOR-BORDER-BLUE**: `#E0E8F4` → `#A3BFE8` - Featured/active card borders. App value more saturated blue for clear interactive state signaling. [VERIFIED - DLPHS-IN11 vs BP02 config]
- **COLOR-PRIMARY-LIGHT**: `#C3D9F0` → `#C3D9F0` - Same in both. Icon/badge backgrounds, focus rings. [VERIFIED - DLPHS-IN11, 13 occurrences in pitch]
- **COLOR-WHITE**: `#FFFFFF` → `#FFFFFF` - Same. Card surfaces in both contexts.

### 3.2 App Implementation Palette

Values used in `tailwind.config.js` across all web applications. These are the canonical implementation values.

- **COLOR-PRIMARY** (AI Blue): `#2C5ED6` - Links, CTAs, active states, button fills. For large surfaces (buttons, borders). [VERIFIED - BP02 tailwind.config.js, 10 deployed apps]
- **COLOR-PRIMARY-TEXT** (Emphasis Numbers): `#003EDA` - The ONE key number per view (totals, KPIs, headline metrics). Uses brand-reference blue for maximum impact on small text surfaces. Compensates for perceptual loss of saturation at small sizes. [PROVEN - S05 template, matches pitch deck Slide 10]
- **COLOR-NAVY** (Primary Text): `#14213A` - All body text, headings, icon default. Deep navy, not pure black. [VERIFIED - BP02 config]
- **COLOR-CHROME** (Structural Text): `#283552` - Footer taglines, table column headers, badge labels. Darker than slate, lighter than navy. [VERIFIED - DLPHS-IN11]
- **COLOR-SLATE** (Secondary Text): `#536078` - Muted text, captions, helper text, timestamps. [VERIFIED - BP02 config]
- **COLOR-BG** (Page Background): `#F7FAFC` - Very light cool blue-white. Never pure white. [VERIFIED - S05 template 2026-08-16, updated from #F1F6FA for lighter feel]
- **COLOR-BG-HIGHLIGHT** (Highlight Surface): `#E8F0FA` - Pale blue tint for cards, panels, selected rows. [VERIFIED - BP02 config]
- **COLOR-BORDER** (Lines/Borders): `#C8D6E5` - Pale blue-gray, visible enough for interactive boundaries. [VERIFIED - BP02 config]
- **COLOR-BORDER-BLUE** (Active Borders): `#A3BFE8` - Thin blue border on highlighted/selected elements. [VERIFIED - BP02 config]
- **COLOR-WHITE** (Card Surface): `#FFFFFF` - Cards, modals, inputs sit on pure white against COLOR-BG. White inline boxes on COLOR-BG MUST have `border: 1px solid COLOR-BORDER` for contrast. [VERIFIED - S05 template 2026-08-16]
- **COLOR-LOGO-TEXT** (Logo Wordmark): `#1A2E5A` - Dark navy-blue used exclusively for the "Delphios" wordmark text and tool name in the header. Slightly different from COLOR-NAVY. [VERIFIED - brand logo reference 2026-08-16]

### 3.3 Brand Reference Palette

Values extracted from pitch deck SVGs (DLPHS-IN11). Used in presentations, marketing materials, brand assets.

- **COLOR-PRIMARY** (AI Blue): `#003EDA` - Emphasis numbers, key phrases, domain link, logo mark, connector lines. Vivid electric blue with zero green channel. [VERIFIED - 172 occurrences across 14 slides]
- **COLOR-NAVY** (Heading Text): `#162444` - Slide titles, names, main statements. [VERIFIED - 127 occurrences]
- **COLOR-CHROME** (Footer/Header Text): `#283552` - Footer tagline "Built for enterprises. Trusted by compliance.", table column headers. [VERIFIED - 42 occurrences, all slides]
- **COLOR-SLATE** (Body Text): `#54637D` - Supporting descriptions, evidence statements, contact info. [VERIFIED - 133 occurrences]
- **COLOR-BG** (Slide Background): `#F5F9FB` - Full-canvas fill, very pale cool blue-white. [VERIFIED - all 14 slides]
- **COLOR-BG-HIGHLIGHT** (Header Bar): `#EAF3FC` - Narrow strip at slide top, subtle differentiation from page. [VERIFIED - all slides with chrome]
- **COLOR-BORDER** (Divider Lines): `#DFE5EB` - Horizontal separators between header and content. [VERIFIED - 18 occurrences]
- **COLOR-BORDER-CARD** (Card/Table Outlines): `#D9E0E7` - Card outlines and table grid lines. Slightly darker than dividers. [VERIFIED - 33 occurrences]
- **COLOR-BORDER-BLUE** (Featured Card Border): `#E0E8F4` - Blue-tinted border on highlighted cards. [VERIFIED - 12 occurrences]
- **COLOR-PRIMARY-LIGHT** (Icon/Badge Fill): `#C3D9F0` - Light blue fill behind icons and badge containers. [VERIFIED - 13 occurrences]
- **COLOR-WHITE** (Card Surface): `#FFFFFF` - Content card interiors against tinted slide background. [VERIFIED - all slides]
- **ICON-FILL-DARK**: `#1F3868` - Primary fill for icon path elements. [VERIFIED - 21 occurrences]
- **ICON-FILL-DEEP**: `#1A2E56` - Secondary fill for icon sub-elements. [VERIFIED - 13 occurrences]

### 3.4 Extended Blue Scale

For states requiring lighter/darker variants of COLOR-PRIMARY:

- **COLOR-PRIMARY-DARK**: `#1D4ED8` - Hover state for buttons and links. [VERIFIED - S05 NOTES, BP02 config]
- **COLOR-PRIMARY-LIGHT**: `#C3D9F0` - Focus rings, selected tab backgrounds, icon/badge fill. [VERIFIED - DLPHS-IN11, pitch deck icon backgrounds]
- **COLOR-PRIMARY-SUBTLE**: `#EAF3FC` - Badge backgrounds, notification dots, very subtle highlights. Derived: same value as brand header bar background. [VERIFIED - DLPHS-IN11]

### 3.5 Semantic Roles

Map core palette to functional roles:

- `text-primary` = COLOR-NAVY
- `text-secondary` = COLOR-SLATE
- `text-chrome` = COLOR-CHROME (footers, table headers, structural labels)
- `text-emphasis` = COLOR-PRIMARY-TEXT (the ONE key number per view - totals, KPIs)
- `text-inverse` = COLOR-WHITE (on dark/blue backgrounds)
- `surface-page` = COLOR-BG
- `surface-card` = COLOR-WHITE
- `surface-highlight` = COLOR-BG-HIGHLIGHT
- `border-default` = COLOR-BORDER
- `border-active` = COLOR-BORDER-BLUE
- `interactive-default` = COLOR-PRIMARY
- `interactive-hover` = COLOR-PRIMARY-DARK
- `interactive-focus` = COLOR-PRIMARY (border) + 15% opacity COLOR-PRIMARY (glow shadow)

### 3.6 Severity Indicators

For risk levels, compliance status, and alert states:

- **Prohibited/Critical/Error**: `#EA2A2A` (red-600, slightly warmer than Tailwind default)
- **High-Risk/Warning**: `#EA580C` (orange-600)
- **Limited/Caution**: `#CA8A04` (amber-600)
- **Minimal/Success/Pass**: `#16A34A` (green-600)
- **Info/Neutral**: COLOR-PRIMARY (`#2C5ED6` in apps, `#003EDA` in presentations)

Each severity color has a background variant at 10% opacity for banner/card fills:
- Red bg: `#FEF2F2`, Orange bg: `#FFF7ED`, Amber bg: `#FAF8EB`, Green bg: `#F0FDF4`

### 3.7 Visual Emphasis Rule

**70% neutral / 20% navy / 10% AI blue**

The blue attracts the eye because it is scarce. Applied as:
- **70% neutral**: Backgrounds (COLOR-BG, COLOR-WHITE), borders (COLOR-BORDER), whitespace
- **20% navy**: Body text (COLOR-NAVY), headings, icons in default state
- **10% AI blue**: Key numbers, CTAs, active states, the single most important element per view

**Rule**: If more than 2-3 elements on a screen are COLOR-PRIMARY, the emphasis is diluted. Reduce until the blue draws the eye to the ONE thing that matters.

### 3.8 Progress (Lifecycle) Indicators

For task/workflow lifecycle stages. Independent hue family from severity (no overlap by design):

- **Done/Erfüllt**: `#0891B2` (cyan-600, teal-blue) - bg: `#CFFAFE`
- **In Progress/In Arbeit**: `#2C5ED6` (COLOR-PRIMARY, brand active) - bg: `#D6E4F5`
- **Open/Offen**: `#536078` (COLOR-SLATE, awaiting) - bg: `#E2E8F0`
- **Planned/Geplant**: `#7030A1` (Royal Purple, PowerPoint Accent 3) - bg: `#EBE0F7`
- **Inactive/Inaktiv**: `#9CA3AF` (grey-400, dormant) - bg: `#F3F4F6`

[VERIFIED - S05 visual testing 2026-08-16]

**Design rationale:**
- In Progress = brand blue (reinforces the "active work = brand" association from the emphasis rule)
- Open = neutral slate (no action taken yet, low visual weight)
- Planned = royal purple (distinct from blue, signals intentional future commitment)
- Done = teal (cool, resolved, clearly distinct from severity green which is warm success)
- Background values are darker than typical Tailwind -50 to ensure badge visibility on white surfaces

### 3.9 Confirmation Feedback Colors

For quiz/assessment/checklist feedback. 4-level system. Semantically different from severity (feedback is calm, not danger):

- **Yes/Correct (Ja/Korrekt)**: `#16A34A` (green) - bg: `#F0FDF4`
- **No/Incorrect (Nein/Inkorrekt)**: `#F63341` (red-orange, calm warmth) - bg: `#FFF0F1`
- **Partial/Unsure (Teilweise/Unklar)**: `#92845D` (Lazer muted, pitch Accent 6) - bg: `#F7F3E3`
- **Not Applicable (Nicht zutreffend)**: `#6B7280` (grey-500) - bg: `#F3F4F6`

[PROVEN - S05 template 2026-08-16]

**Design rationale:**
- "Incorrect" feedback is NOT danger/critical. Users should not feel alarmed. The red-orange (`#F63341`) is warmer and lighter than severity-critical (`#EA2A2A`), creating a calmer emotional response while still clearly signaling "wrong."
- "Partial/Unsure" uses Lazer (`#92845D`, pitch Accent 6 muted) - warm golden-brown, completely distinct from severity-moderate amber (`#CA8A04`). Each semantic zone has its own color family.
- "Not Applicable" uses neutral grey - carries no emotional weight, signals irrelevance.
- Severity-critical (`#EA2A2A`) remains reserved for system alerts, prohibited states, and actual danger conditions.

**Usage:** Tri-state selectors (BP02), quiz answers (BP04), checklist compliance states, inline assessment icons.

### 3.10 Choosing the Right Color (Decision Guide)

When coloring a value, label, or indicator, ask these questions in order:

**1. Is this a lifecycle/workflow STATE?** (Erfüllt, In Arbeit, Offen, Geplant, Inaktiv)
→ Use **Progress** palette. Never severity colors for lifecycle labels.

**2. Is this a RISK LEVEL or URGENCY?** (Kritisch, Hoch, Mittel, Niedrig, Deadline)
→ Use **Severity** palette. These signal "how concerned should I be?"

**3. Is this a POSITIVE OUTCOME?** (savings, reduction, improvement, success message)
→ Use **severity-low green** (`#16A34A`). Green = good news / positive result.

**4. Is this a NEGATIVE OUTCOME without danger?** (quiz wrong answer, comparison loss)
→ Use **confirm-no red-orange** (`#F63341`). Calmer than critical red.

**5. Is this the KEY NUMBER on this screen?** (total, headline metric, primary KPI)
→ Use **COLOR-PRIMARY-TEXT** (`#003EDA`). Vivid brand blue for maximum impact at small text size.

**6. Is this a DESTRUCTIVE ACTION?** (delete, remove, cancel permanently)
→ Use **severity-critical red** (`#EA2A2A`). Only for irreversible danger.

**7. Is this regular DATA with no emotional valence?** (neutral numbers, body text)
→ Use **COLOR-NAVY** (`#14213A`) or **COLOR-SLATE** (`#536078`). No color coding.

**Zone isolation rule:** Each semantic zone (Severity, Progress, Confirmation) MUST use its own distinct colors. Never borrow colors from one zone to use in another. This prevents visual ambiguity when both zones appear on the same screen.

**Common mistakes:**
- Coloring buttons by action type (green=confirm, purple=schedule) → wrong, all buttons are brand blue
- Using severity-critical for "Offen" (open) → wrong, that's a progress state, use progress-open
- Using brand blue for savings/positive results → wrong, green signals "good outcome"
- Using progress-done (teal) for financial savings → wrong, teal means lifecycle-complete, not "positive value"
- Using progress-done (teal) for alert "Bestanden" state → wrong, alert banners are Severity zone, use severity-low (green)
- Using severity-moderate for confirmation "Teilweise" → wrong, confirmation zone uses Lazer (`#A38940`), severity uses amber (`#CA8A04`)

[VERIFIED - S05 visual testing 2026-08-16]

## 4. Typography

### 4.1 Font Stack

- **UI Font**: `Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- **Logo Wordmark Font**: `[LOGO-WORDMARK-FONT]` - The typeface used in the "Delphios" wordmark. NOT used for UI text. Identified from brand assets only.
- **Monospace** (code snippets, technical values): `'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace`

### 4.2 Type Scale

Based on TYPE-BASE-SIZE = 16px with a modular scale ratio of `[TYPE-SCALE-RATIO]` (estimated 1.25 "Major Third" from slide hierarchy).

Web app sizes:

- `type-xs`: 12px / 0.75rem - Labels, footnotes, timestamps
- `type-sm`: 14px / 0.875rem - Helper text, captions, badge text
- `type-base`: 16px / 1rem - Body text, form inputs, table cells
- `type-lg`: 18px / 1.125rem - Subheadings, card titles
- `type-xl`: 20px / 1.25rem - Section headings
- `type-2xl`: 24px / 1.5rem - Page section titles
- `type-3xl`: 30px / 1.875rem - Page titles, hero subtext
- `type-4xl`: 36px / 2.25rem - Hero headlines, KPI numbers
- `type-5xl`: 48px / 3rem - Impact numbers (used sparingly)

Presentation sizes (mapped to pt):

- Section label: 16-18pt (= type-base to type-lg)
- Main headline: 36-44pt (= type-4xl to type-5xl)
- Supporting statement: 20-24pt (= type-xl to type-2xl)
- Body/table text: 16-20pt (= type-base to type-xl)
- Footer/labels: 12-14pt (= type-xs to type-sm)

### 4.3 Weight Usage

- **Regular (400)**: Body text, descriptions, helper text
- **Medium (500)**: Subheadings, card titles, labels. Use when regular is too light but semibold too heavy.
- **Semibold (600)**: Primary headings, KPI numbers, button text, strong emphasis. PREFERRED over bold.
- **Bold (700)**: Reserved for hero headlines and impact numbers only. Never for body emphasis.

**Rule**: Prefer semibold over bold. Bold is only for the single biggest text element on a view.

### 4.4 Color in Typography

- **Default**: COLOR-NAVY (`#14213A`) for all text unless specified otherwise
- **Secondary**: COLOR-SLATE (`#536078`) for helper text, captions, metadata
- **Emphasis**: COLOR-PRIMARY (`#2C5ED6`) for the most important number or phrase ONLY
- **Inverse**: COLOR-WHITE (`#FFFFFF`) on dark/blue backgrounds (buttons, banners)

**Rule**: Blue text = the ONE most important thing on this screen. If you blue two things, neither is important. Same principle as bold in writing.

### 4.5 Line Height and Letter Spacing

- Body text (type-base, type-lg): line-height 1.5 (24px at 16px base)
- Headings (type-2xl and above): line-height 1.2-1.3
- Compact (tables, badges, buttons): line-height 1.25
- Letter spacing: `[TYPE-LETTER-SPACING-HEADING]` for headings (estimated -0.01em to -0.02em), 0 for body

## 5. Spacing and Layout

### 5.1 Spacing Scale

Base unit: SPACE-BASE = 4px. All spacing values are multiples:

- `space-0`: 0px
- `space-1`: 4px (0.25rem) - Tight gaps: between icon and label
- `space-2`: 8px (0.5rem) - Small gaps: between badge and text, inline elements
- `space-3`: 12px (0.75rem) - Medium-small: input padding vertical
- `space-4`: 16px (1rem) - Standard gap: between list items, card content padding
- `space-5`: 20px (1.25rem) - Medium: between form fields
- `space-6`: 24px (1.5rem) - Section padding, card padding
- `space-8`: 32px (2rem) - Between cards, between sections within a page region
- `space-10`: 40px (2.5rem) - Large section gaps
- `space-12`: 48px (3rem) - Between major page sections
- `space-16`: 64px (4rem) - Page-level top/bottom padding
- `space-20`: 80px (5rem) - Hero section vertical padding
- `space-24`: 96px (6rem) - Maximum vertical breathing room

### 5.2 Layout Grid

- **Content max-width**: `[LAYOUT-MAX-WIDTH]` (estimated 1200px)
- **Page margin (desktop)**: `[LAYOUT-PAGE-MARGIN]` (estimated space-8 to space-16 depending on viewport)
- **Column gutter**: space-6 (24px)

Format-specific layout rules (canvas dimensions, container strategies) are defined in Section 16 per output type.

### 5.3 Alignment Rules

- **Body text**: Left-aligned always
- **Headlines**: Left-aligned in web apps; centered on presentation slides when standalone (no accompanying body text)
- **Cards in grid**: Left-aligned content within cards
- **Numbers/KPIs**: Left-aligned or centered depending on layout (centered in KPI blocks, left in tables)
- **Never**: Center-align body paragraphs or long text

### 5.4 Responsive Breakpoints

*Applies to: web applications only.*

- `breakpoint-sm`: `[LAYOUT-BP-SM]` (estimated 640px) - Mobile
- `breakpoint-md`: `[LAYOUT-BP-MD]` (estimated 768px) - Tablet
- `breakpoint-lg`: `[LAYOUT-BP-LG]` (estimated 1024px) - Desktop
- `breakpoint-xl`: `[LAYOUT-BP-XL]` (estimated 1280px) - Wide desktop

**Responsive behavior**: Cards stack vertically on mobile. Header elements stack (logo above, tool name below). Tables become scrollable. KPI blocks go from row to column.

## 6. Iconography

### 6.1 Icon Source

**Phosphor Icons** (https://phosphoricons.com) - Primary icon set for all Delphios materials.

**Fallback**: Lucide Icons (https://lucide.dev) may be used ONLY when Phosphor does not offer a suitable icon for the required concept. All Lucide icons must match Phosphor's visual weight (stroke-width 1.5-2px, consistent with Phosphor Light).

Rationale: Consistent stroke weight, extensive library (6000+ icons), multiple weight variants, open source (MIT), available as SVG and web font. React: `@phosphor-icons/react`. Vanilla: `@phosphor-icons/web` or SVG sprites.

### 6.2 Weight Conventions

- **Thin**: Large decorative/hero icons (48px+). Used on landing pages, section headers, empty states.
- **Light**: Application UI icons at 20px+ (icon-md and above) on WHITE/light backgrounds. Card icons, section markers, feature icons, navigation. Also used as thin white icons on dark-filled backgrounds (buttons, colored boxes) for elegant contrast.
- **Regular**: Small inline icons below 20px (icon-sm: 16px, text-lg: 18px). Status indicators, inline badges, alert icons. Also used for button icons on dark backgrounds (standard weight for readability at button text size). Light weight becomes visually noisy and loses clarity at small sizes. [VERIFIED - S05 visual testing 2026-08-16]
- **Bold**: `[ICON-BOLD-USAGE]` - Use case TBD.
- **Fill**: Active/selected states (e.g., filled check circle). Avoid for general use.

**Background-dependent weight rule:**
- White/light bg, large (24px+): `ph-light` (thin strokes, elegant on white)
- White/light bg, small (16px): `ph` (regular, readable at small size)
- Dark/colored bg, icon-only boxes: `ph-light` (thin white for elegance)
- Dark/colored bg, button with text: `ph` (regular, matches text weight)
[VERIFIED - S05 visual testing 2026-08-16]

### 6.3 Size Scale

- `icon-sm`: 16px - Inline with text (badges, list markers)
- `icon-md`: 20px - Buttons, form elements, navigation
- `icon-lg`: 24px - Card headers, section markers
- `icon-xl`: 32px - Feature cards, comparison matrix headers
- `icon-2xl`: 48px - Hero sections, landing page features
- `icon-3xl`: `[ICON-SIZE-3XL]` - Full-page empty states (estimated 64-80px)

### 6.4 Color Rules

**Icons are NEVER multi-colored.** Every icon uses exactly ONE color from the palette below. Colored/branded icons are prohibited unless explicitly approved as an intentional design exception by the designer (not agent-decided).

**Anti-pattern** (BP01 current state): Category cards with teal, purple, pink, gradient icons. Each icon a different color. Correct: All icons COLOR-NAVY in default state, or all COLOR-PRIMARY if active.

- **Default state**: COLOR-NAVY (`#14213A`)
- **Active/selected state**: COLOR-PRIMARY (`#2C5ED6`)
- **On blue background**: COLOR-WHITE (`#FFFFFF`)
- **Disabled state**: COLOR-SLATE (`#536078`) at 50% opacity
- **Severity icons**: Inherit severity color (red/orange/amber/green) - single color only, not multi-toned

### 6.5 Brand-Associated Icons (Semantic Mapping)

These icons appear consistently in Delphios materials for specific concepts:

- **Shield** (shield-check): Compliance, security, trust (appears in footer)
- **Check circle**: Passed/compliant/verified state
- **X circle**: Failed/prohibited/blocked state
- **Layers/stack**: Compliance layers, multi-level architecture
- **Lock**: Data sovereignty, encryption, on-premise
- **Document**: Policies, rules, contracts
- **Chart line up**: Growth, market data, projections
- **Grid/table**: Matrix, comparison, structured data
- **User/people**: Team, personas, roles
- **Calendar**: Timeline, milestones, deadlines

## 7. Components

### 7.1 Cards

The primary content container across all Delphios interfaces.

**Default card:**
- Background: COLOR-WHITE (`#FFFFFF`)
- Border: 1px solid COLOR-BORDER (`#C8D6E5`)
- Border radius: RADIUS-BASE * 2 = `[COMP-CARD-RADIUS]` (estimated 8-12px from slides)
- Padding: space-6 (24px)
- Shadow: `[SHADOW-CARD]` (estimated: none or very subtle `0 1px 3px rgba(0,0,0,0.04)`)

**Highlighted card** (selected column in comparison, active state):
- Background: COLOR-BG-HIGHLIGHT (`#E8F0FA`)
- Border: 1px solid COLOR-BORDER-BLUE (`#A3BFE8`)
- All other properties same as default

**KPI card** (number + conclusion + evidence):
- Icon: top-left or centered, icon-xl, thin weight
- Number: type-4xl or type-5xl, semibold, COLOR-PRIMARY
- Conclusion: type-lg, semibold, COLOR-NAVY
- Evidence: type-sm, regular, COLOR-SLATE

### 7.2 Buttons

**Primary button:**
- Background: COLOR-PRIMARY (`#2C5ED6`)
- Text: COLOR-WHITE, semibold, type-base
- Border radius: `[COMP-BUTTON-RADIUS]` (estimated 6-8px, derived from RADIUS-BASE)
- Padding: space-3 vertical, space-5 horizontal
- Hover: COLOR-PRIMARY-DARK (`#1D4ED8`)
- Focus: `[COMP-BUTTON-FOCUS-RING]` (2px ring in COLOR-PRIMARY-LIGHT offset 2px)
- Disabled: 50% opacity, cursor not-allowed

**Secondary button:**
- Background: transparent
- Border: 1px solid COLOR-BORDER (`#C8D6E5`)
- Text: COLOR-NAVY, semibold
- Hover: background COLOR-BG-HIGHLIGHT

**Ghost button:**
- Background: transparent
- Border: none
- Text: COLOR-PRIMARY, semibold
- Hover: background `[COLOR-PRIMARY-SUBTLE]`

**Destructive button (Delete/Remove):**
- Background: `#EA2A2A` (severity-critical red)
- Text: COLOR-WHITE, semibold
- Only exception to the single-color button rule below

**Button color rule:** All action buttons use COLOR-PRIMARY (`#2C5ED6`) regardless of action type. Do NOT color-code buttons by function (green for confirm, purple for schedule, navy for export). The only exception is destructive actions (delete, remove) which use severity-critical red to signal irreversibility. This keeps the UI calm and prevents a rainbow of button colors that conflicts with the 70/20/10 emphasis rule. [VERIFIED - S05 visual testing 2026-08-16]

### 7.3 Badges and Tags

- Background: `[COLOR-PRIMARY-SUBTLE]` (very pale blue) or severity color at 10% opacity
- Text: COLOR-PRIMARY or severity color, type-sm, medium weight
- Border radius: `[COMP-BADGE-RADIUS]` (full-round: 9999px for pill shape)
- Padding: space-1 vertical, space-2 horizontal
- "Kostenlos" badge (lead magnets): `[COMP-BADGE-FREE-BG]` / `[COMP-BADGE-FREE-TEXT]` - likely green-subtle or blue-subtle

### 7.4 Form Inputs

- Background: COLOR-WHITE
- Border: 1px solid COLOR-BORDER
- Border radius: `[COMP-INPUT-RADIUS]` (derived from RADIUS-BASE, estimated 6px)
- Padding: space-3 vertical, space-4 horizontal
- Text: COLOR-NAVY, type-base
- Placeholder: COLOR-SLATE
- Focus: border COLOR-PRIMARY + `box-shadow: 0 0 0 3px rgba(44, 94, 214, 0.15)` [PROVEN - S05 template]
- Error: border `#EA2A2A`, ring red at 10%

### 7.5 Tables and Matrices

- Header row: Background COLOR-BG-HIGHLIGHT, text COLOR-NAVY semibold type-sm uppercase
- Body rows: Background COLOR-WHITE, border-bottom 1px COLOR-BORDER
- Hover row: Background COLOR-BG
- Selected/highlighted column: Background `[COLOR-PRIMARY-SUBTLE]`, border-top 2px COLOR-PRIMARY
- Check icon (feature present): Filled circle COLOR-PRIMARY + white check
- Dash (feature absent): Short line COLOR-SLATE
- Partial dot: Small filled circle COLOR-PRIMARY

### 7.6 Progress Indicators

**Step indicator** (wizard/decision tree):
- Active step: COLOR-PRIMARY circle with white number, semibold
- Completed step: COLOR-PRIMARY filled check circle
- Future step: COLOR-BORDER circle with COLOR-SLATE number
- Connector line: COLOR-BORDER (completed: COLOR-PRIMARY)

**Progress bar:**
- Track: COLOR-BG-HIGHLIGHT, full-round radius
- Fill: COLOR-PRIMARY, full-round radius
- Height: `[COMP-PROGRESS-HEIGHT]` (estimated 8px)

### 7.7 Modals and Overlays

- Backdrop: `rgba(20, 33, 58, 0.5)` (COLOR-NAVY at 50%)
- Modal surface: COLOR-WHITE
- Border radius: `[COMP-MODAL-RADIUS]` (estimated 12-16px, larger than cards)
- Shadow: `[SHADOW-MODAL]` (estimated `0 20px 60px rgba(0,0,0,0.15)`)
- Padding: space-8
- Max width: `[COMP-MODAL-MAX-WIDTH]` (estimated 560px for standard, 800px for wide)

### 7.8 Alerts and Banners

- Border-left: 4px solid severity color
- Background: severity color at 10% opacity
- Icon: severity color, light weight, icon-lg
- Title: COLOR-NAVY, semibold, type-base
- Body: COLOR-NAVY, regular, type-sm
- Border radius: RADIUS-BASE (right corners only) or `[COMP-ALERT-RADIUS]`

## 8. Chrome: Header and Footer

*Applies to: web applications and presentations. Each subsection is labeled by format.*

### 8.1 Web App Header

```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo] Delphios           Tool Name                            │
├─────────────────────────────────────────────────────────────────┤
│  Welcome   Wizard   Result   Checklist   Gap Report   ...       │
└─────────────────────────────────────────────────────────────────┘
```

- **Layout**: 3-column grid (`grid-cols-3 items-center`). Logo+brand left, tool name centered, empty/actions right. [PROVEN - S05 template]
- **Height**: `py-3 px-6` (approx 52px with content). Sticky: `position: sticky; top: 0; z-index: 50`
- **Background**: COLOR-WHITE. Bottom border: 1px solid COLOR-BORDER
- **Logo block** (left column): SVG logo `h-9 w-9` + wordmark text `font-bold text-xl tracking-tight` in COLOR-LOGO-TEXT (`#1A2E5A`), gap-2 between icon and text
- **Tool name** (center column): `font-semibold text-lg` in COLOR-LOGO-TEXT (`#1A2E5A`)
- **No badge**: Removed "Kostenlos" badge - cleaner, more professional appearance. [PROVEN - S05 template, user decision 2026-08-16]
- **Tab navigation**: Separate `<nav>` below header, also sticky (`top-[52px]`). Tab bar uses `px-2` so first tab's `px-4` internal padding aligns text at 24px matching logo's `px-6` offset. [PROVEN - S05 template]
- **Responsive**: Logo and tool name stack vertically on mobile

### 8.2 Web App Footer

```
┌─────────────────────────────────────────────────────────────────┐
│  [Disclaimer text]                                              │
│  [Copyright] [Year] Delphios.ai          [Link to delphios.ai] │
└─────────────────────────────────────────────────────────────────┘
```

- Background: `[COMP-FOOTER-BG]` (estimated COLOR-BG or slightly darker)
- Text: COLOR-SLATE, type-sm
- Top border: 1px solid COLOR-BORDER
- Padding: space-6 vertical
- Disclaimer: Legal text about tool purpose and limitations
- Copyright: "(c) [YEAR] `[DLPHS-BRAND-NAME]`"

### 8.3 Presentation Header

```
┌─────────────────────────────────────────────────────────────────┐
│  Section Title          [Delphios Logo]                     NN  │
│  ─────────────────────────────────────────────────────────────  │
```

- Section title: Left-aligned, COLOR-NAVY, type-base, regular
- Logo: Centered, `[LOGO-HEIGHT-SLIDE]` (estimated 24-28px)
- Slide number: Right-aligned, COLOR-NAVY, type-base, regular
- Divider: Thin line (1px) in COLOR-PRIMARY, full width below header

### 8.4 Presentation Footer

```
│  ─────────────────────────────────────────────────────────────  │
│  [Shield Icon] Built for enterprises. Trusted by compliance.    │
│                                                     delphios.ai │
└─────────────────────────────────────────────────────────────────┘
```

- Shield icon: Phosphor shield-check, light weight, COLOR-SLATE
- Tagline: COLOR-SLATE, type-xs. Uses `[DLPHS-FOOTER-TAGLINE]` (currently resolves to `[DLPHS-SLOGAN-07-EN]`). Change role assignment in DLPHS-IN07 Section 8.3 to update all footers.
- Domain: `[DLPHS-DOMAIN]`, right-aligned, COLOR-SLATE, type-xs
- No divider line above (only the header has a colored divider)

## 9. Information Design Patterns

### 9.1 KPI Blocks

The primary pattern for presenting data. Structure: **number → conclusion → evidence**.

```
┌──────────────────┐
│  [Icon]          │
│  89%             │  ← type-4xl/5xl, semibold, COLOR-PRIMARY
│  never reach     │  ← type-lg, semibold, COLOR-NAVY
│  production      │
│  AI projects die │  ← type-sm, regular, COLOR-SLATE
│  before deploy.  │
└──────────────────┘
```

- Layout: 2-4 KPI cards in a row (desktop), stack on mobile
- Always prefer this pattern over bullet lists for quantitative claims
- The number is ALWAYS COLOR-PRIMARY (the one blue element per card)

### 9.2 Comparison Matrices

Feature grids with check/dash/dot states. See Slide 8 (Competitive Analysis).

- Left column: Feature names with icons, left-aligned
- Data columns: Centered check/dash/dot states
- Highlighted column (Delphios): COLOR-BG-HIGHLIGHT background, COLOR-PRIMARY header
- Column headers: Company logos or names, centered

### 9.3 Decision Trees and Wizards

Multi-step flows for interactive tools (BP01, BP03, BP10).

- Step indicator at top (numbered circles with connector lines)
- One question per view with clear answer options
- Answer options as clickable cards (not radio buttons)
- Back/Reset navigation always visible
- Result page: Classification badge + obligations list + next steps

### 9.4 Timelines and Phased Plans

Numbered steps with period labels. See Slide 7 (Go-to-Market).

```
  ┌───┐
  │ 1 │  Phase title (months X - Y)
  └───┘  Supporting description text
    │
  ┌───┐
  │ 2 │  Phase title (months X - Y)
  └───┘  Supporting description text
```

- Numbers: COLOR-PRIMARY circle, white number, semibold
- Title: COLOR-NAVY, semibold, type-lg
- Periods: COLOR-PRIMARY, semibold (e.g., "Months 1 - 6")
- Description: COLOR-SLATE or COLOR-NAVY, regular, type-base
- Connector: Thin vertical line COLOR-BORDER

### 9.5 Three-Column Value Cards

Feature/benefit presentation. See Slide 4 (Value Proposition), Slide 6 (Business Model).

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│    [Icon]   │  │    [Icon]   │  │    [Icon]   │
│             │  │             │  │             │
│  Title      │  │  Title      │  │  Title      │
│  ─────────  │  │  ─────────  │  │  ─────────  │
│  Body text  │  │  Body text  │  │  Body text  │
│  here.      │  │  here.      │  │  here.      │
└─────────────┘  └─────────────┘  └─────────────┘
```

- Icon: Centered, icon-2xl, thin weight, COLOR-PRIMARY
- Title: Centered or left, semibold, type-lg, COLOR-NAVY
- Divider: Optional thin line (COLOR-BORDER)
- Body: Left-aligned, regular, type-base, COLOR-NAVY or COLOR-SLATE
- Card style: Default card (white, border, radius)

### 9.6 Radar Charts and Score Visualizations

For multi-dimensional assessments (BP04 quiz results).

- Chart lines: COLOR-BORDER for grid
- Fill: COLOR-PRIMARY at 20% opacity
- Stroke: COLOR-PRIMARY, 2px
- Labels: COLOR-NAVY, type-sm
- Score display: type-4xl, semibold, COLOR-PRIMARY

## 10. Page Layout Patterns

*Applies to: web applications (lead magnets). Presentation layouts are defined in Section 16.1.*

### 10.1 Landing/Hero Page

Every lead magnet starts with a landing page:

```
┌────────────────────────────────────────────┐
│  [Header Chrome]                           │
├────────────────────────────────────────────┤
│                                            │
│  [Hero Title - type-3xl/4xl, semibold]     │
│  [Subtitle - type-xl, regular, SLATE]      │
│                                            │
│  [CTA Button - Primary, large]             │
│                                            │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  │
│  │ KPI  │  │ KPI  │  │ KPI  │  │ KPI  │  │
│  │ Card │  │ Card │  │ Card │  │ Card │  │
│  └──────┘  └──────┘  └──────┘  └──────┘  │
│                                            │
├────────────────────────────────────────────┤
│  [Footer Chrome]                           │
└────────────────────────────────────────────┘
```

### 10.2 Interactive Tool Page

Full-width layout for decision trees, quizzes, checklists:

```
┌────────────────────────────────────────────┐
│  [Header Chrome]                           │
├────────────────────────────────────────────┤
│  [Progress/Step Indicator]                 │
│                                            │
│  [Question/Content Area]                   │
│                                            │
│  [Options / Input / Controls]              │
│                                            │
│  [Navigation: Back | Next/Submit]          │
├────────────────────────────────────────────┤
│  [Footer Chrome]                           │
└────────────────────────────────────────────┘
```

### 10.3 Results Page

Classification, score, or report output:

```
┌────────────────────────────────────────────┐
│  [Header Chrome]                           │
├────────────────────────────────────────────┤
│  [Classification Badge / Score]            │
│  [Summary Statement]                       │
│                                            │
│  [Detailed Breakdown - cards/list]         │
│                                            │
│  [Recommendations / Next Steps]            │
│                                            │
│  [CTA: Download PDF | Restart | Share]     │
├────────────────────────────────────────────┤
│  [Footer Chrome]                           │
└────────────────────────────────────────────┘
```

### 10.4 Matrix/Dashboard Page

Filterable data display (BP05, BP06, BP08):

```
┌────────────────────────────────────────────┐
│  [Header Chrome]                           │
├────────────────────────────────────────────┤
│  [Filters: Search | Category | Status]     │
│                                            │
│  [Tab Navigation (if multi-view)]          │
│                                            │
│  [Data Table / Matrix / Card Grid]         │
│                                            │
│  [Pagination or Load More]                 │
├────────────────────────────────────────────┤
│  [Footer Chrome]                           │
└────────────────────────────────────────────┘
```

## 11. States and Interactions

*Applies to: interactive web applications only. Non-interactive formats (PDF, print, presentations) do not use states or motion.*

### 11.1 Interactive States

- **Default**: Normal resting state
- **Hover**: Subtle background change or border darkening. Transition: `[MOTION-DURATION-FAST]` (estimated 150ms) ease-out
- **Focus**: `border-color: COLOR-PRIMARY` + `box-shadow: 0 0 0 3px rgba(44, 94, 214, 0.15)`. Applied globally via CSS on `input:focus, select:focus, textarea:focus`. Buttons/links use `outline: 3px solid COLOR-PRIMARY, offset 2px` via `:focus-visible`. Must be clearly visible on both click and keyboard navigation.
- **Active/Pressed**: Slightly darker than hover (scale 0.98 or darken 5%)
- **Disabled**: 50% opacity, cursor not-allowed, no hover/focus response
- **Loading**: Pulse animation or spinner replacing content

### 11.2 Transitions

- **Duration fast**: `[MOTION-DURATION-FAST]` (estimated 150ms) - Hover states, color changes
- **Duration normal**: `[MOTION-DURATION-NORMAL]` (estimated 200-250ms) - Expanding panels, tab switches
- **Duration slow**: `[MOTION-DURATION-SLOW]` (estimated 300-400ms) - Modal open/close, page transitions
- **Easing**: `[MOTION-EASING-DEFAULT]` (estimated `cubic-bezier(0.4, 0, 0.2, 1)` or `ease-out`)

### 11.3 Empty States

When no data is available:
- Large icon (icon-3xl, thin weight, COLOR-SLATE)
- Title: type-xl, COLOR-NAVY, semibold
- Description: type-base, COLOR-SLATE
- Optional CTA button

### 11.4 Error States

- Input error: Red border + red helper text below
- Page error: Alert banner (red severity) with retry CTA
- Network error: Empty state pattern with error icon

### 11.5 Interaction Philosophy

UX principles derived from WhizzyApps (predecessor company) and evolved for the Delphios Benevolent Ruler archetype. Each principle maps to a brand pillar.

- **Explorative over instructive** (Flow): Users are free to explore on their own. If they need help, they will click. Never force tutorials, onboarding overlays, tooltips-on-first-visit, or "did you know" prompts.
- **Self-explanatory** (Order): No proactive help by default. Provide tool-tips with keyboard shortcuts and context-related help when the user seeks it. Provide documentation on- and offline.
- **Zero friction** (Care): Reduce cognitive burden because the user's mental energy deserves protection. Offer simple, safe defaults while allowing depth for those who seek it. Simplify the solution, not the problem.
- **Always just works** (Reliability): Architecture that expects the unexpected. Weird usage patterns or inputs should never break the app. Designed for the worst case.

## 12. Writing for UI

### 12.1 Headlines are Conclusions

**Rule**: Every headline states the conclusion, not the category.

- GOOD: "Only Delphios combines governance, sovereignty and deployment."
- BAD: "Competitive Analysis"
- GOOD: "35 paying customers get us to 1.8M ARR."
- BAD: "Financial Projections"

### 12.2 Bullet Format

Bold summary label + colon + thin detail:

- **89% never reach production:** AI agent projects die before deployment
- **Not a technology problem:** 73% blame governance, 0% blame model capability

### 12.3 Number Formatting

- Currency: "EUR 36K" or "EUR 36,000" (formal). Never "36K EUR" or "36.000 EUR".
- Presentation slides: "EUR 750K - 1M" with the number in COLOR-PRIMARY
- Percentages: "89%" with number in COLOR-PRIMARY, "percent" spelled out only in body text
- Ranges: "EUR 36K – 72K" with en-dash (–) and spaces

### 12.4 German Language Conventions

- Address: `[DLPHS-ADDRESS-STYLE]` (formal B2B, never Du)
- Compound nouns: Written as single word (Risikoklassifizierung, not Risiko-Klassifizierung)
- Umlauts: Always proper Unicode (ae → ä, oe → ö, ue → ü). Never ASCII substitutions.
- Legal/regulatory terms: Use official German terminology (Bundesanstalt für Finanzdienstleistungsaufsicht, not "German financial authority")

### 12.5 Microcopy Tone

**Base rules**: Apply DLPHS-IN07 Section 9 (DO/DONT) to all UI text. Key constraints: authoritative, functional, frugal, no hedging, no buzzwords, no casual tone.

**UI-specific additions** (not in brand doc):
- German hedging words prohibited in UI: "vielleicht", "eventuell", "unter Umständen"
- Button labels: verb-first imperative ("Analyse starten", not "Starten Sie die Analyse")
- Error messages: state what failed + what to do next (never "Etwas ist schiefgelaufen")

## 13. Accessibility

### 13.1 Contrast Requirements

WCAG 2.1 AA minimum:
- Normal text (type-base and smaller): 4.5:1 contrast ratio
- Large text (type-xl and above): 3:1 contrast ratio
- Non-text elements (icons, borders, focus indicators): 3:1

**Verified ratios** (against COLOR-BG `#F7FAFC`):
- COLOR-NAVY `#14213A` on COLOR-BG: `[A11Y-CONTRAST-NAVY-BG]` (estimated >12:1, passes AAA)
- COLOR-SLATE `#536078` on COLOR-BG: `[A11Y-CONTRAST-SLATE-BG]` (estimated ~5:1, passes AA)
- COLOR-PRIMARY `#2C5ED6` on COLOR-WHITE: `[A11Y-CONTRAST-PRIMARY-WHITE]` (estimated ~4.5:1, verify)
- COLOR-WHITE on COLOR-PRIMARY: `[A11Y-CONTRAST-WHITE-PRIMARY]` (inverse of above, passes)

### 13.2 Focus Management

*Sections 13.2-13.3 apply to interactive web applications only.*

- All interactive elements must have visible focus indicators
- Input/select/textarea focus: `border-color: COLOR-PRIMARY` + `box-shadow: 0 0 0 3px rgba(44, 94, 214, 0.15)` (global CSS rule)
- Button/link focus-visible: `outline: 3px solid COLOR-PRIMARY`, offset 2px
- Tab order follows visual order (left-to-right, top-to-bottom)
- Modals trap focus until dismissed
- Skip-to-content link on every page

### 13.3 Keyboard Navigation

- All functionality accessible via keyboard
- Decision tree: Arrow keys for option navigation, Enter to select
- Tables: Tab through interactive cells
- Modals: Escape to close

### 13.4 Screen Reader Considerations

- Semantic HTML (headings, landmarks, lists)
- ARIA labels on icon-only buttons
- Progress indicators announce current step
- Chart alternatives: Data table or text summary
- Status badges include text (not color alone)

## 14. Anti-Patterns

Things to NEVER use in any Delphios material. These anti-patterns were identified in the V3C pitch critique and remain permanently prohibited.

**Visual effects:**
- No gradients (except within the existing brand mark/logo)
- No glowing UI elements (including glowing logos, beveled type, bright checkmarks)
- No 3D effects
- No heavy drop shadows (subtle `0 1px 3px` maximum for cards)
- No oversized rounded rectangles (max radius is COMP-MODAL-RADIUS)

**Decorative elements:**
- No decorative "AI" imagery (neural networks, brains, robots)
- No stock photography
- No more than 2-3 levels of visual hierarchy per view
- No background patterns or textures

**Charts and data:**
- No pie charts (use comparison matrices or bar equivalents)
- No dense bullet walls (max 5 bullets per section, then restructure)
- No decorative icons without semantic meaning

**Typography:**
- No shadows, outlines, glow, or decorative typography effects
- No more than 2 font weights on a single view (regular + semibold is the norm)
- No italic for emphasis (use semibold or COLOR-PRIMARY)
- No underlined text except hyperlinks
- No "everything bold" pattern - if all text is emphasized, nothing is prioritized

**Color:**
- No large colored surfaces (the 70% neutral rule)
- No more than ONE element in COLOR-PRIMARY per card/section
- No color as the SOLE indicator of state (always pair with icon or text)

**Onboarding and overlays:**
- No auto-show modals, tutorials, or welcome dialogs on first visit
- No "did you know" tooltips, coach marks, or guided tours
- No cookie-wall-style interruptions before the user can see content
- Help content is available but never forced (user clicks "Help" or "?" when ready)

## 15. Design Tokens Reference

*Applies to: web applications. Token implementations for other formats (PowerPoint theme, PDF generation) will be added when those formats are actively produced.*

### 15.1 CSS Custom Properties

Canonical `:root` block for all Delphios web applications:

```css
:root {
  /* Core Palette (App Implementation - Section 3.2) */
  --color-primary: #2C5ED6;
  --color-primary-dark: #1D4ED8;
  --color-primary-text: #003EDA;
  --color-primary-light: #C3D9F0;
  --color-primary-subtle: #EAF3FC;
  --color-navy: #14213A;
  --color-chrome: #283552;
  --color-slate: #536078;
  --color-bg: #F7FAFC;
  --color-bg-highlight: #E8F0FA;
  --color-white: #FFFFFF;
  --color-border: #C8D6E5;
  --color-border-blue: #A3BFE8;

  /* Confirmation (4 levels - Section 3.9) */
  --confirm-yes: #16A34A;
  --confirm-yes-bg: #F0FDF4;
  --confirm-no: #F63341;
  --confirm-no-bg: #FFF0F1;
  --confirm-partial: #92845D;
  --confirm-partial-bg: #F7F3E3;
  --confirm-na: #6B7280;
  --confirm-na-bg: #F3F4F6;

  /* Severity */
  --color-error: #EA2A2A;
  --color-warning: #EA580C;
  --color-caution: #CA8A04;
  --color-success: #16A34A;

  /* Typography */
  --font-sans: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --type-base: 1rem;
  --type-xs: 0.75rem;
  --type-sm: 0.875rem;
  --type-lg: 1.125rem;
  --type-xl: 1.25rem;
  --type-2xl: 1.5rem;
  --type-3xl: 1.875rem;
  --type-4xl: 2.25rem;
  --type-5xl: 3rem;
  --weight-regular: 400;
  --weight-medium: 500;
  --weight-semibold: 600;
  --weight-bold: 700;
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-20: 5rem;

  /* Radii */
  --radius-sm: [RADIUS-SM];
  --radius-md: [RADIUS-MD];
  --radius-lg: [RADIUS-LG];
  --radius-full: 9999px;

  /* Shadows */
  --shadow-card: [SHADOW-CARD];
  --shadow-modal: [SHADOW-MODAL];
  --shadow-dropdown: [SHADOW-DROPDOWN];

  /* Motion */
  --motion-fast: [MOTION-DURATION-FAST];
  --motion-normal: [MOTION-DURATION-NORMAL];
  --motion-slow: [MOTION-DURATION-SLOW];
  --easing-default: [MOTION-EASING-DEFAULT];

  /* Layout */
  --layout-max-width: [LAYOUT-MAX-WIDTH];
  --layout-page-margin: [LAYOUT-PAGE-MARGIN];
}
```

**Realtime theming architecture**: In the S05 design template, all brand colors reference CSS variables (`var(--d-blue)`, `var(--d-bg)`, etc.) in the Tailwind config instead of hardcoded hex values. This allows the color panel to update the entire app in realtime by setting `document.documentElement.style.setProperty(varName, value)`. Semantic colors (severity, progress, confirmation) also use CSS variables. The `:root` block above defines both brand and semantic variables.

### 15.2 Tailwind Config

Canonical `tailwind.config.js` for all Delphios web applications.

**Token-to-Tailwind key mapping**: `COLOR-PRIMARY` = `delphios-blue`, `COLOR-PRIMARY-TEXT` = `delphios-blue-text`, `COLOR-NAVY` = `delphios-navy`, `COLOR-CHROME` = `delphios-chrome`, `COLOR-SLATE` = `delphios-slate`, `COLOR-BG` = `delphios-bg`, `COLOR-BG-HIGHLIGHT` = `delphios-bg-highlight`, `COLOR-BORDER` = `delphios-border`, `COLOR-BORDER-BLUE` = `delphios-border-blue`, `COLOR-PRIMARY-LIGHT` = `delphios-blue-light`, `COLOR-PRIMARY-SUBTLE` = `delphios-blue-subtle`.

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        delphios: {
          blue: '#2C5ED6',
          'blue-dark': '#1D4ED8',
          'blue-text': '#003EDA',
          'blue-light': '#C3D9F0',
          'blue-subtle': '#EAF3FC',
          navy: '#14213A',
          chrome: '#283552',
          slate: '#536078',
          bg: '#F7FAFC',
          'bg-highlight': '#E8F0FA',
          white: '#FFFFFF',
          border: '#C8D6E5',
          'border-blue': '#A3BFE8',
        },
        confirm: {
          yes: '#16A34A',
          'yes-bg': '#F0FDF4',
          no: '#F63341',
          'no-bg': '#FFF0F1',
          partial: '#92845D',
          'partial-bg': '#F7F3E3',
          na: '#6B7280',
          'na-bg': '#F3F4F6',
        },
        severity: {
          error: '#EA2A2A',
          'error-bg': '#FEF2F2',
          warning: '#EA580C',
          'warning-bg': '#FFF7ED',
          caution: '#CA8A04',
          'caution-bg': '#FAF8EB',
          success: '#16A34A',
          'success-bg': '#F0FDF4',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        'card': '[COMP-CARD-RADIUS]',
        'button': '[COMP-BUTTON-RADIUS]',
        'input': '[COMP-INPUT-RADIUS]',
        'modal': '[COMP-MODAL-RADIUS]',
        'badge': '9999px',
      },
      boxShadow: {
        'card': '[SHADOW-CARD]',
        'modal': '[SHADOW-MODAL]',
        'dropdown': '[SHADOW-DROPDOWN]',
      },
      maxWidth: {
        'content': '[LAYOUT-MAX-WIDTH]',
      },
    },
  },
  plugins: [],
};
```

### 15.3 Presentation Token Mapping

How design tokens translate to presentation (PowerPoint/Keynote) values. Uses Brand Reference Palette (Section 3.3):

- `type-base` (16px) → 16pt slide body text
- `type-4xl` (36px) → 36pt main headline
- `type-5xl` (48px) → 44-48pt impact headline
- COLOR-PRIMARY (`#003EDA`) → Bold blue accent (fill for numbers, icons, domain link)
- COLOR-NAVY (`#162444`) → Slide titles, heading text
- COLOR-CHROME (`#283552`) → Footer tagline, table column headers
- COLOR-SLATE (`#54637D`) → Body text, descriptions, evidence statements
- COLOR-BG (`#F5F9FB`) → Slide background fill
- COLOR-BG-HIGHLIGHT (`#EAF3FC`) → Header bar background
- COLOR-BORDER (`#DFE5EB`) → Thin dividers (0.5pt)
- COLOR-BORDER-CARD (`#D9E0E7`) → Card outlines, table grid lines
- COLOR-PRIMARY-LIGHT (`#C3D9F0`) → Icon/badge background fills
- COLOR-WHITE → Card/container fill

## 16. Application Contexts

### 16.1 Presentations (16:9)

Specific rules that apply only to slide decks:

- Canvas: 1920x1080px (16:9)
- Content area: Central 80-85% of canvas
- Word count: 25-45 words per slide (excluding header/footer chrome). If more, restructure. [VERIFIED - final pitch slides average ~30 words]
- Max 5 bullets per slide at 30pt font (Kawasaki rule)
- One dominant message per slide
- Headline = conclusion statement, not category label (see Section 12.1)
- Source citations ONLY in presenter notes, never on projected slides
- Header: Section title | Logo | Slide number
- Footer: Shield icon + tagline + domain
- Product screenshots on 3+ slides when available
- Comparison slides: Use calm matrix with check/dash/dot states and generous spacing, never dense feature tables

### 16.2 Web Applications (Responsive)

Specific rules that apply only to interactive web apps:

**Tech stack**:
- **CSS framework**: Tailwind CSS with canonical `tailwind.config.js` (Section 15.2)
- **Icons**: `@phosphor-icons/react` (React apps) or `@phosphor-icons/web` (vanilla apps)
- **Framework heuristic**: React (Vite) for multi-step wizards and stateful UIs. Vanilla HTML/CSS/JS for read-display-submit tools. Decision criteria: if >1 interactive state transition, wizard, or real-time update → React.
- **TypeScript**: Optional for lead magnets. Required for Agent Builder.
- **Template**: S05 copy-paste starter (shared header, footer, theme, Tailwind config). New apps start from this template.

**Layout and interaction rules**:
- Mobile-first responsive design
- Max content width: `[LAYOUT-MAX-WIDTH]`
- Touch targets: Minimum 44x44px (mobile)
- Header and footer are fixed layout elements (not position:fixed)
- All interactive elements have hover, focus, and active states
- Loading states for any operation >300ms
- Error states for any fallible operation
- Back/reset navigation always available in multi-step flows

### 16.3 Marketing Materials

Specific rules for landing pages, social media, email:

- Use presentation visual language (KPI blocks, three-column cards)
- Headline = conclusion (same rule as slides)
- CTA button always COLOR-PRIMARY
- Social cards: 1200x630px, headline + one KPI or product screenshot
- Email: System fonts only (Inter may not render), inline styles

## 17. Sources

- `DLPHS-IN10-SC-PTCH-SLDES`: Pitch deck slides 1-14 (S05_AppDesignTemplate/_INPUT_gitignore/DelphiosPitch/) - Visual language reference [VERIFIED]
- `DLPHS-IN10-SC-CGPT-DSGN`: `ChatGPT_DelphiosPitchDesignSystem.md` - Original design system draft, superseded [VERIFIED]
- `DLPHS-IN10-SC-S05-NOTES`: `T05_LEADMGNTS_LeadMagnets/S05_AppDesignTemplate/NOTES.md` - App template design tokens [VERIFIED]
- `DLPHS-IN10-SC-BP02-TWCF`: `BP02_ClauseChecker/tailwind.config.js` - Implementation reference [VERIFIED]
- `DLPHS-IN10-SC-BRND-IN07`: `_INFO_DELPHIOS_BRAND.md [DLPHS-IN07]` - Brand values and archetype [VERIFIED]
- `DLPHS-IN10-SC-CGPT-CRIT`: `ChatGPT_DelphiosPitchV3C-Critique.md` - Structured visual critique that drove the redesign from "bright startup" to "controlled enterprise" [VERIFIED]
- `DLPHS-IN10-SC-WHZY-PHIL`: WhizzyApps design philosophy (https://whizzyapps.com/#philosophy) - Predecessor company UX principles carried forward into Delphios [VERIFIED]

## Next Steps

1. **Resolve LOGO-* placeholders**: Extract logo font, exact blue, dimensions, safe space from brand assets (AI or Figma file)
2. **Resolve COLOR-PRIMARY-LIGHT and COLOR-PRIMARY-SUBTLE**: Generate from COLOR-PRIMARY at specified opacities, verify contrast
3. **Resolve RADIUS-* values**: Measure from pitch slides or existing apps, standardize
4. **Resolve SHADOW-* values**: Define or confirm "almost no shadow" (current apps use none)
5. **Resolve MOTION-* values**: Define transition durations (can use industry standard 150/250/350ms)
6. **Resolve LAYOUT-* values**: Confirm max-width and breakpoints from existing app behavior
7. **Verify accessibility contrast ratios**: Run all color pairs through WCAG calculator
8. **Recreate all 10 lead magnets** with design system template (S05 copy-paste starter): Tailwind + Phosphor Icons + shared header/footer/theme
9. **Migrate icons**: Replace Lucide (BP02, BP10) with Phosphor equivalents. All apps must use `@phosphor-icons/react` or SVG sprites.
10. **Apply framework heuristic** during recreation: BP01, BP02, BP03, BP10 → React (Vite). BP04-BP09 → Vanilla HTML/CSS/JS + Tailwind. All apps use shared S05 template.
11. **Delete** `ChatGPT_DelphiosPitchDesignSystem.md` after team confirms this document is complete

## Document History

**[2026-08-17 00:12]**
- Changed: Section 3.9 confirm-partial from `#92400E` to `#A38940` (Lazer 25% darker, pitch Accent 6) with bg `#F3EFE2` (Lazer 80% lighter)
- Changed: Section 3.10 Decision Guide item 5 - key number uses COLOR-PRIMARY-TEXT (`#003EDA`) not COLOR-PRIMARY
- Added: Section 3.10 Zone isolation rule - each semantic zone must have own distinct colors
- Added: Section 3.10 Common mistakes - progress-done in alerts, severity-moderate in confirmation
- Source: Visual testing revealed zone color bleeding between Severity, Progress, and Confirmation

**[2026-08-17 00:04]**
- Added: Section 3.2 COLOR-PRIMARY-TEXT `#003EDA` - vivid brand blue for emphasis numbers (compensates small text surface)
- Changed: Section 3.9 expanded from 2 to 4 confirmation levels (added Partial, N/A)
- Added: Section 15.1 --color-primary-text, --confirm-partial, --confirm-partial-bg, --confirm-na, --confirm-na-bg variables
- Added: Section 15.2 Tailwind config - `blue-text`, full `confirm` color group
- Changed: Token mapping - added `COLOR-PRIMARY-TEXT` = `delphios-blue-text`
- Source: S05 AppDesignTemplate Confirmation States section + pitch deck color matching

**[2026-08-16 23:41]**
- Changed: Section 8.1 Web App Header - complete rewrite with proven 3-column grid layout, sticky behavior, tab alignment rule, no-badge decision
- Changed: Section 3.2 COLOR-BG updated from `#F1F6FA` to `#F7FAFC` (lighter page background)
- Added: Section 3.2 COLOR-LOGO-TEXT `#1A2E5A` (logo wordmark + tool name color)
- Changed: Section 3.2 COLOR-WHITE - added white-card-border rule (border required for contrast on lighter BG)
- Changed: Section 3.6 severity-critical from `#DC2626` to `#EA2A2A` (warmer red)
- Changed: Section 11.1 Focus state - replaced ring with border-color + box-shadow approach
- Changed: Section 13.2 Focus Management - split into input vs button/link focus patterns
- Changed: Section 3.5 interactive-focus role - now uses COLOR-PRIMARY border + 15% glow
- Changed: Section 15.1 CSS variables - updated --color-bg and --color-error values
- Changed: Section 15.2 Tailwind config - updated bg and error values
- Added: Section 15.1 note on realtime theming architecture via CSS variables
- Changed: Section 3.1 mapping table - updated COLOR-BG mapping
- Source: S05 AppDesignTemplate implementation and user feedback

**[2026-08-16 22:12]**
- Added: Section 3.10 "Choosing the Right Color" decision guide - ordered flowchart for color selection with common mistakes
- Rule: positive outcomes (savings, reductions) = green, NOT blue or teal

**[2026-08-16 22:09]**
- Added: Section 7.2 Destructive button variant (Delete/Remove = severity-critical red)
- Added: Section 7.2 Button color rule - all buttons COLOR-PRIMARY, no color-coding by action type. Only exception: destructive actions (red)

**[2026-08-16 22:05]**
- Added: Section 3.8 Progress (Lifecycle) Indicators - 5-level scale (Done/In Progress/Open/Planned/Inactive) with hex values and background variants
- Added: Section 3.9 Confirmation Feedback Colors - red-orange #F63341 for calm "incorrect" feedback, distinct from severity-critical danger
- Changed: Section 6.2 Weight Conventions - added background-dependent weight rule (ph-light on dark bg for elegance, ph regular for buttons with text)
- Source: S05 AppDesignTemplate visual testing and user feedback

**[2026-08-16 15:02]**
- Changed: Section 3 restructured with Dual-Context Color Model (3.1 explanation + mapping, 3.2 App Implementation, 3.3 Brand Reference)
- Added: COLOR-CHROME token (`#283552`) - footer taglines, table headers, structural text between navy and slate
- Resolved: `[COLOR-PRIMARY-LIGHT]` → `#C3D9F0` (from DLPHS-IN11 pitch extraction, 13 occurrences)
- Resolved: `[COLOR-PRIMARY-SUBTLE]` → `#EAF3FC` (from DLPHS-IN11, pitch header bar background)
- Added: Brand Reference Palette (Section 3.3) with all values from DLPHS-IN11 pitch SVG extraction
- Added: ICON-FILL-DARK (`#1F3868`) and ICON-FILL-DEEP (`#1A2E56`) as brand reference icon path fills
- Changed: Section 15.1 CSS custom properties - resolved placeholders, added `--color-chrome`
- Changed: Section 15.2 Tailwind config - resolved placeholders, added `chrome` key
- Changed: Section 15.3 Presentation Token Mapping - now shows brand reference hex values per Section 3.3
- Changed: Section 3.5 Semantic Roles - added `text-chrome` role, resolved `interactive-focus`
- Changed: Placeholder count 43 → 41 (2 COLOR resolved)

**[2026-08-16 14:38]**
- Changed: Replaced duplicated brand text with `[DLPHS-*]` constant references from DLPHS-IN07 Section 8.3
- Changed: Section 1 now uses `[DLPHS-PRINCIPLE]`, `[DLPHS-ARCHETYPE]`, `[DLPHS-VALUES]`, pillar constants
- Changed: Section 8.2/8.4 footer uses `[DLPHS-FOOTER-TAGLINE]`, `[DLPHS-DOMAIN]`, `[DLPHS-BRAND-NAME]`

**[2026-08-16 14:35]**
- Fixed: Section 1 derivation now connects to all three brand pillars (Flow, Absolute Reliability, Safety and Compliance) per DLPHS-IN07 Section 2
- Fixed: Litmus test expanded with second test for Flow support (minimal friction, non-distracting, focused)
- Added: Section 8.4 tagline note - current text from slides, should align with DLPHS-IN07 Section 8 slogans on refresh

**[2026-08-16 14:30]**
- Added: "Quick Start" reference block after Summary - 7-step compressed essentials for new app development
- Fixed: ToC entry 18 removed (Document History is standard suffix, broken anchor `#18-document-history`)

**[2026-08-16 14:28]**
- Added: Section 16.2 "Tech stack" subsection - framework heuristic, Tailwind universal, icon packages, TypeScript policy, S05 template
- Changed: Next Step 10 reformulated from decision to migration action (decision now lives in 16.2)

**[2026-08-16 14:21]**
- Changed: Section 6.1 icon source - Phosphor primary, Lucide fallback only when Phosphor lacks concept. Added React/Vanilla package names.
- Added: Section 6.4 explicit rule - icons NEVER multi-colored, exceptions must be designer-approved (not agent-decided)
- Added: Next Steps 8-10 - recreate all apps with template, migrate Lucide to Phosphor, framework heuristic (React vs Vanilla)

**[2026-08-16 14:06]**
- Added: "Scope and Coverage" declaration after Summary (covers presentations + lead magnets; defers Agent Builder, website, PDF, print)
- Fixed: Section 5.2 removed presentation-only "80-85% canvas" rule, delegated to Section 16
- Added: Scope markers on format-specific sections (5.4, 8, 10, 11, 13.2-13.3, 15) identifying which output types they apply to

**[2026-08-16 13:04]**
- Added: Design origin note in Section 1 tracing visual direction to V3C pitch critique
- Added: Litmus test ("controlled enterprise AI" vs "energetic SaaS startup")
- Added: Slide word count rule (25-45 words) in Section 16.1 [VERIFIED from final slides]
- Added: "Headline = conclusion" cross-reference and comparison matrix rule in Section 16.1
- Added: Anti-pattern provenance note and "everything bold" prohibition in Section 14
- Added: Source DLPHS-IN10-SC-CGPT-CRIT for the critique document
- Fixed: [DESIGNED] label replaced with [ASSUMED] per verification label rules

**[2026-08-16 13:02]**
- Added: Design decision note for COLOR-PRIMARY explaining why #2C5ED6 over #2563EB and #1F5ED8
- Added: Token-to-Tailwind key mapping in Section 15.2 (bridges COLOR-PRIMARY = delphios-blue naming gap)

**[2026-08-16 13:00]**
- Added: Section 2.4 Placeholder Registry - consolidated index of all 43 unresolved placeholders with derivation rules, estimated values, and resolution sources
- Fixed: Acronyms expanded on first use (CTA, KPI, WCAG, ARIA, SVG)
- Fixed: Arrow symbols `->` replaced with ` → ` per core-conventions
- Fixed: En-dash example uses actual `–` character
- Added: DLPHS-IN10 registered in ID-REGISTRY.md

**[2026-08-16 12:56]**
- Initial design system document created
- Consolidated from: ChatGPT_DelphiosPitchDesignSystem.md + S05_AppDesignTemplate/NOTES.md + BP02 tailwind.config.js
- All confirmed values marked [VERIFIED], unknowns marked with [PREFIX-PLACEHOLDER] notation
- Dependency graph documents how upstream values cascade to component-level tokens
