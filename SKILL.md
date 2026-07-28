---
name: econ-council
description: Convene a 13-persona Economics Council using local gemma4 to deliberate on a complex economic topic or decision
---

# Economics Council Deliberation Skill

This skill allows the agent to execute a 13-persona specialized economics council locally using Ollama.

## How to use

Run the python script from the skill directory:

```bash
uv run --with requests --with python-dotenv -m scripts.economics_council "<topic>"
```

1. Pass the user's economic topic or question as the argument.
2. The deliberation executes in three stages (generation, peer review, and chairman synthesis).
3. The final synthesized note is saved in the vault under `Research/Council/`.
