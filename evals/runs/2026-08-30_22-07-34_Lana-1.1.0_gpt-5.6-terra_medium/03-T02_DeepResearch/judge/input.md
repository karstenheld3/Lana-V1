# PROMPTS

The task the agent received (prompt-queue format: fenced prompts separated by ---).

PROMPTS.md
````
```
/deep-research When exactly did the Berlin Wall fall, and which three political events of the same year directly preceded it?

Requirements:
- Use live web research: search the web and read at least 3 source pages
- Write the result to `_INFO_BERLINWALL.md` in the workspace root with: a `## Summary` section stating the exact fall date, a findings section covering the three preceding events, and a `## Sources` section
- Every source entry needs a full https URL and an access date; label key findings with verification labels ([VERIFIED] when confirmed by 2+ sources, [ASSUMED] otherwise)
- Minimum 5 distinct sources
```
````

# AGENT OUTPUT

The output to judge. Full workspace folder structure:

```
└─ .gitkeep
```

(no output files found)