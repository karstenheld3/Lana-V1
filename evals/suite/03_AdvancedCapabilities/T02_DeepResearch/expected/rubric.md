# Rubric: DeepResearch Quality

The input is a research INFO document answering: "When exactly did the Berlin Wall fall, and which three political events of the same year directly preceded it?" Score these dimensions:

## Dimension: Answer Correctness

The fall date is stated as November 9, 1989 (1989-11-09) in the Summary. The three preceding 1989 events are historically real and causally relevant (target-quality examples: Hungary opening its border to Austria, the Pan-European Picnic, the Monday demonstrations in Leipzig, mass emigration via Prague embassy, Schabowski's press conference). Wrong date = score 0.

## Dimension: Citation Auditability

Every factual claim traces to a source: sources carry full https URLs (clickable, with scheme), access dates, and the document uses verification labels ([VERIFIED]/[ASSUMED]) distinguishing multi-source-confirmed facts from single-source claims. Bare domains, missing URLs, or unlabeled key claims = major deduction.

## Dimension: Source Diversity

At least 5 distinct sources across at least 3 distinct domains (e.g., encyclopedia, museum/archive, news organization). Fewer than 3 domains or fewer than 5 sources = proportional deduction.

## Dimension: No Invention

No invented events, dates, quotes, or sources. Any source URL that is obviously fabricated (implausible path patterns) or any historical claim contradicting well-established facts = score below 50.
