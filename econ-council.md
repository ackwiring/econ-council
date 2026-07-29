---
description: Convene a 13-persona Economics Council using local gemma4 to deliberate on a complex economic topic or decision
category: thinking
triggers_en: ["economics council", "convene the economics council", "run economics council", "ask the economics council"]
triggers_es: ["consejo economico", "convocar el consejo economico"]
triggers_pt: ["conselho economico", "convocar o conselho economico"]
---

Use the econ-council skill. Execute `/econ-council [topic or question]`:

This command deliberates on a complex economic question or decision by running a 13-persona specialized economics council. It executes in three stages (generation, peer review, and chairman synthesis) locally using Ollama.

1. Resolve the topic or question from the user's argument. If none, ask: "What topic/decision do you want to put to the Economics Council?"
2. Run the script from the skill root:
   ```bash
   uv run --directory "/Users/sooty_webster/local_git_projects/Skills/econ-council" -m scripts.economics_council "<topic>"
   ```
3. Show the Chairman's final synthesis and recommended decision to the user.
4. Report the absolute path of the generated markdown note in the vault (`Research/Council/`).

---

**AI-first rule:** Every note created or updated by this command MUST follow `references/ai-first-rules.md` - `## For future Claude` preamble, rich frontmatter (`type`, `date`, `tags`, `ai-first: true`, plus type-specific fields), recency markers per external claim, mandatory `[[wikilinks]]` for every person/project/concept referenced, sources preserved verbatim with URLs inline, and confidence levels where applicable. The vault is for future-Claude retrieval - not human reading.
