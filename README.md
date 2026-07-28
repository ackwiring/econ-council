# Economics Council Deliberation Engine

An AI-first, 13-persona local deliberation engine utilizing local LLMs (e.g., `gemma4` via Ollama) to analyze complex economic questions, policy choices, and sovereign resource decisions. Inspired by Andrej Karpathy's `llm-council` architecture, the engine executes a multi-stage debate and synthesis pipeline before writing structured reports directly to an Obsidian vault.

---

## 🏛️ End-to-End Workflow

The deliberation engine operates sequentially in four stages, maintaining a strict parallel-processing workflow capped at a concurrency limit of 2 to conserve local resources (VRAM/CPU):

```
[User Query]
     │
     ▼
┌───────────────────────────────────────────────┐
│ Stage 1: Parallel Generation                  │  ◄── Concurrent (max_workers=2)
│ - 13 Advisors generate initial opinions       │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│ Stage 2: Peer Review & Critique              │  ◄── Concurrent (max_workers=2)
│ - Each Advisor critiques colleagues' opinions │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│ Stage 3: Chairman Synthesis                   │  ── Serial
│ - Synthesis of consensus, tensions, & verdict │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│ Stage 4: Vault Integration                    │  ── Saved to Research/Council/
│ - AI-First formatting with wikilinks & LaTeX  │
└───────────────────────────────────────────────┘
```

### Stage 1: Parallel Generation
The input topic is dispatched to 13 economic advisors simultaneously. Each advisor queries the local model with their specific system prompt, producing an initial opinion focused on their area of expertise.

### Stage 2: Peer Review
All 13 initial opinions are compiled into a unified debate context. This context is fed back to every advisor. Each advisor critiques the collective body of work, identifying logical gaps, contradictions, and blind spots from their domain's perspective.

### Stage 3: Chairman Synthesis
The Chairman (a specialized synthesis persona) reviews the topic, the initial opinions, and the peer critiques. The Chairman extracts key points of consensus, identifies critical points of tension/disagreement, evaluates risks, and delivers a recommended decision.

### Stage 4: Vault Integration
The entire transcript—synthesis report, advisor opinions, and peer critiques—is written to the Obsidian vault under `Research/Council/` as a markdown note adhering to the AI-first vault rules.

---

## 👤 The 13 Advisor Personas (Do's & Don'ts)

Each persona is designed to provide high-fidelity analysis inside their specific domain, while staying strictly within their operational boundaries to ensure a diverse debate.

| Advisor Name | Focus Area (What They Do) | Operational Boundaries (What They DON'T Do) |
|---|---|---|
| **1. Computational & AI-Driven Economics** | High-dimensional nowcasting, Agent-Based Computational Modeling (ACE), Causal ML, complexity tipping points, and phase transitions. | Does **not** write qualitative political narratives or advocate for traditional linear regressions. |
| **2. Behavioral & Psychological Prediction** | Cognitive biases (loss aversion, overconfidence), nudge theory, choice architecture, sentiment analysis, and central bank narrative tracking. | Does **not** assume market participants are rational actors or use static growth calculations. |
| **3. Environmental & Transition Economics** | Climate econometrics, transition risk, stranded commodity assets, environmental disaster forecasting, and bio-economics (pandemic modeling). | Does **not** ignore Carbon Border Adjustment Mechanisms (CBAM) or treat natural capital as cost-free. |
| **4. Financial Microstructure & Market Dynamics** | Limit Order Books (LOB), systemic risk node failures, contagion modeling, and crypto-tokenomics. | Does **not** evaluate long-term GDP growth or design national social policies. |
| **5. Social & Urban Predictive Economics** | Smart city mobility dynamics, gentrification patterns, transit impacts, and algorithmic health policy econometrics. | Does **not** model high-frequency trading or evaluate international tariff agreements. |
| **6. World Trade: Theoretical Core** | Physical vs. intangible trade flow, firm heterogeneity (Melitz Model), and tariff general equilibrium effects on prices/wages. | Does **not** analyze green transition rules, carbon tariffs, or geopolitical friend-shoring. |
| **7. World Trade: Modern Frontiers** | Global value chain fragmentation, CBAM, e-commerce flow, friend-shoring/near-shoring, and wage-skill gaps. | Does **not** treat trade as politically neutral or use old Ricardian comparative models. |
| **8. Macroeconomics: Core** | GDP growth determinants, monetary policy (inflation, interest rates, QE), and fiscal policy/debt sustainability. | Does **not** assume household wealth is uniform (leaves this to HANK) or ignore micro-shocks. |
| **9. Macroeconomics: Modern Frontiers** | HANK models, climate macroeconomics, macroprudential banking stability, and secular stagnation/demographics. | Does **not** analyze micro-structure trade flows or local mining logistics. |
| **10. International Macro** | The Impossible Trinity, global financial cycles, currency volatility, and capital flows. Challenges traditional depreciation/NPV. | Does **not** accept Net Present Value (NPV) uncritically or validate classical resource economics. |
| **11. Sovereign Resource Strategist** | Commodity cycles, Capex/Opex mine logistics, reserve valuations (JORC/NI 43-101), SWFs (Norway model), and Resource Rent Taxes. | Does **not** do theoretical modeling; focuses strictly on physical mining finance and logistics. |
| **12. Quantitative Analytics (Monetary)** | Dutch Disease mitigation, FX hedging (futures/swaps), Balance of Payments (BoP), and Resource-Backed Bonds. | Does **not** evaluate geopolitical risks or state governance constraints. |
| **13. Geospatial & Bridge Diplomacy** | GIS/geological overlays, Stability Agreements, contract law negotiation, political risk, and strategic communication. | Does **not** model mathematical currency risk or compute financial microstructures. |

---

## 📈 Output Data & Advice Expectations

Deliberation outputs are saved with strict formatting rules optimized for both human readability and downstream LLM retrieval (AI-first design).

### 1. Frontmatter Metadata
Every note contains rich frontmatter tags indicating the run parameters:
```yaml
---
date: YYYY-MM-DD
type: economics-council
tags:
  - economics
  - thinking
  - council
ai-first: true
model: "gemma4:latest"
topic: "User's topic/question"
---
```

### 2. Retrieval Optimization
*   **Preamble**: Under `## For future Claude`, the note includes a short, self-contained overview of the run context.
*   **Wikilinks**: Key concepts, entities, and personas are linked via `[[wikilinks]]` for graph database mapping.
*   **LaTeX Formatting**: All equations, currency symbols, and monetary shifts are formatted mathematically (e.g., $\text{FX}_{\text{in}}$, $E_{t+1}$).

### 3. Deliberation Report Structure
The Chairman's synthesis is divided into four critical sections:
*   **Executive Summary**: A high-level verdict.
*   **Key Areas of Consensus**: Core agreements between advisors (e.g., Dutch Disease overvaluation metrics).
*   **Key Points of Tension**: Unresolved disagreements (e.g., physical infrastructure constraints vs. monetary policy).
*   **Recommended Decision**: A phased action plan (Phase I: Stabilization/SWF, Phase II: Decoupling, Phase III: Enforcement).
