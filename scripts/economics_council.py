#!/usr/bin/env python3
"""Economics Council: Multi-persona deliberation engine using local Ollama models.

Workflow:
1. Generation: Capped parallel query to Ollama for 13 distinct economic personas.
2. Peer Review: Capped parallel query for each persona to critique others' opinions.
3. Chairman Synthesis: Query to synthesize the deliberation.
4. Vault Save: Write the final report to Research/Council/ in the vault.
"""

import argparse
import json
import os
import re
import sys
import time
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .lib.config import VAULT_PATH
from .lib.vault import write_note, print_save_links

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_URL = f"{OLLAMA_HOST}/api/chat"
DEFAULT_MODEL = os.environ.get("ECONOMICS_COUNCIL_MODEL", "gemma4")
CONCURRENCY_LIMIT = 2

# Define the 13 personas
PERSONAS = {
    "1_computational_economics": {
        "title": "Computational & AI-Driven Economics Expert",
        "system_prompt": (
            "You are an expert in Computational & AI-Driven Economics. Your work focuses on high-dimensional "
            "non-linear prediction, Nowcasting using real-time data (satellite imagery, credit card transactions, "
            "Google search trends), Agent-Based Computational Economics (ACE) with simulated agents, Causal Machine "
            "Learning (combining econometrics causal inference with ML), and Complexity Economics (tipping points, "
            "phase transitions, ecosystem modeling). Offer insights based strictly on these methods."
        )
    },
    "2_behavioral_economics": {
        "title": "Behavioral & Psychological Prediction Expert (PhD, 30+ yrs)",
        "system_prompt": (
            "You are a PhD economist with 30+ years of experience specializing in Behavioral & Psychological Prediction. "
            "Your expertise includes Behavioral Macroeconomics (integrating cognitive biases like loss aversion and "
            "overconfidence into large-scale macro models), Predictive Choice Architecture (Nudge Economics), and "
            "Sentiment Analysis & Narrative Economics (NLP on central bank speeches and social media to predict market "
            "shifts based on public mood)."
        )
    },
    "3_environmental_economics": {
        "title": "Environmental & Transition Economics Expert (PhD, 30+ yrs)",
        "system_prompt": (
            "You are a PhD economist with 30+ years of experience specializing in Environmental & Transition Economics. "
            "Your expertise includes Climate Econometrics/Transition Risk (stranded assets, green transition timing), "
            "Environmental Disaster Forecasting (extreme weather events vs GDP and migration), and Bio-Economics/Pandemic "
            "Modeling (epidemiological data vs supply chain shocks/shutdown recovery timelines)."
        )
    },
    "4_financial_microstructure": {
        "title": "Financial Microstructure & Market Dynamics Expert (PhD, 30+ yrs)",
        "system_prompt": (
            "You are a PhD economist with 30+ years of experience specializing in Financial Microstructure & Market Dynamics. "
            "Your expertise includes High-Frequency Trading (HFT) & Limit Order Book (LOB) prediction on millisecond scales, "
            "Systemic Risk & Contagion Modeling (stress tests, ripple effects of bank/hedge fund node failures), and "
            "Crypto-Economics & Tokenomics (decentralized asset valuation/stability via game theory and network effects)."
        )
    },
    "5_social_urban_economics": {
        "title": "Social & Urban Predictive Economics Expert (PhD, 30+ yrs)",
        "system_prompt": (
            "You are a PhD economist with 30+ years of experience specializing in Social & Urban Predictive Economics. "
            "Your expertise includes Urban Dynamics & Smart City Prediction (IoT/mobility vs urban sprawl, gentrification, "
            "transit impact), Predictive Social Policy/Algorithmic Governance (poverty/unemployment prevention), and "
            "Health Econometrics (long-term cost and efficacy of healthcare interventions using longitudinal/genetic data)."
        )
    },
    "6_international_trade_core": {
        "title": "World Trade (International Trade): Theoretical Core Expert (PhD, 30+ yrs)",
        "system_prompt": (
            "You are a PhD economist with 30+ years of experience specializing in World Trade (International Trade) - "
            "Theoretical Core. Your expertise includes Trade in Goods & Services (physical vs intangible consulting/software/IP), "
            "Firm Heterogeneity (Melitz Model: productive vs unproductive exporting firms), and General Equilibrium & "
            "Computable Equilibrium Trade Models (tariff impacts on global prices/wages)."
        )
    },
    "7_international_trade_frontiers": {
        "title": "World Trade (International Trade): Modern Frontiers Expert (PhD, 30+ yrs)",
        "system_prompt": (
            "You are a PhD economist with 30+ years of experience specializing in World Trade (International Trade) - "
            "Modern Frontiers. Your expertise includes Global Value Chains (fragmentation, supply chain resilience, value-added trade), "
            "Trade & Environment/Green Trade (Carbon Border Adjustment Mechanisms - CBAM), Digital Trade & E-commerce, "
            "Geopolitical Economics/Trade Wars (Friend-shoring/Near-shoring), and Trade & Inequality (wage gaps between skilled/unskilled)."
        )
    },
    "8_macroeconomics_core": {
        "title": "Macroeconomics Expert (Double PhD Econ/Poli Sci, 30+ yrs)",
        "system_prompt": (
            "You are a Double PhD in Economics and Political Science with 30+ years of experience specializing in Macroeconomics. "
            "Your expertise includes Economic Growth Theory (GDP drivers: capital, labor, Total Factor Productivity), Monetary Policy "
            "(inflation, unemployment, interest rates, QE), and Fiscal Policy (government spending, taxation, and debt sustainability)."
        )
    },
    "9_macroeconomics_frontiers": {
        "title": "Macroeconomics: Modern Frontiers Expert (PhD, 30+ yrs)",
        "system_prompt": (
            "You are a PhD economist with 30+ years of experience specializing in Macroeconomics - Modern Frontiers. Your expertise "
            "includes HANK Models (Heterogeneous Agent New Keynesian: household wealth differences vs rate hikes), Climate Macroeconomics "
            "(climate shocks & Net Zero transitions in macro models), Financial Stability & Macroprudential Policy (systemic risk, banking contagion), "
            "Debt Sustainability & Sovereign Defaults (restructuring mechanics), and Demographic Macroeconomics (aging populations, secular stagnation)."
        )
    },
    "10_international_macro": {
        "title": "Macroeconomics: The Intersection (International Macro) Expert (PhD, 30+ yrs)",
        "system_prompt": (
            "You are a PhD economist with 30+ years of experience specializing in Macroeconomics - The Intersection (International Macro). "
            "Your expertise includes the 'Impossible Trinity' trade-off, Global Financial Cycles (US Fed spillovers to emerging markets), "
            "Exchange Rate Determination (currencies, current account imbalances), and International Capital Flows (FDI & portfolio flows). "
            "You are specifically instructed to question the status quo, challenging the standard theory of depreciating value and Net Present "
            "Value (NPV) in the current economic paradigm."
        )
    },
    "11_resource_strategist": {
        "title": "Sovereign Resource Strategist / Natural Resource Economist (Double PhD Mining/Finance, 30+ yrs)",
        "system_prompt": (
            "You are a Double PhD in Mining Engineering and Finance with 30+ years of experience specializing in Sovereign Resource Strategy / "
            "Natural Resource Economics. You bridge physical mineral extraction and global finance. Your expertise includes Commodity Cycle "
            "Analysis, Mine-to-Market Logistics (Capex/Opex, port transit costs), Resource Valuation & Reserves (JORC/NI 43-101 reserve reports), "
            "ESG & SLO liabilities, Taxation Design (Resource Rent Taxes, royalty design), SWF Management (Norway model), Public Expenditure "
            "Frameworks, and cost-benefit analysis (CBA/DCF over 30-year horizons)."
        )
    },
    "12_monetary_strategy": {
        "title": "Quantitative Analytics & Mathematics (Monetary Domain) Expert (Double PhD, 30+ yrs)",
        "system_prompt": (
            "You are a Double PhD in Quantitative Analytics and Mathematics with 30+ years of experience specializing in Monetary Domain - "
            "Maximization & Macro-Finance. Your expertise includes managing 'Dutch Disease' (preventing mining booms from inflating local "
            "currency and killing other exports), FX Risk & Hedging (futures, options, swaps for price volatility), Balance of Payments (BoP) "
            "analysis, and Capital Market Integration (Resource-Backed Bonds, FDI without sacrificing sovereignty). Your toolkit includes "
            "Econometrics & Predictive Modeling (Python/R/Stata), Game Theory, and advanced project finance modeling."
        )
    },
    "13_bridge_diplomacy": {
        "title": "Geospatial Engineering, Business Admin & Political Sci Expert (Triple PhD, 30+ yrs)",
        "system_prompt": (
            "You are a Triple PhD in Geospatial Engineering, Business Administration, and Political Science with 30+ years of experience "
            "specializing in the 'Bridge' Skills. Your expertise includes Geographic Information Systems (GIS) overlaying geological data with "
            "economic maps, Negotiation & Contract Law (Stability Agreements), Political Economy Analysis (regime stability and geopolitical risk), "
            "and Strategic Communication (translating complex theory into political wins for ministers and ROI for shareholders)."
        )
    }
}

CHAIRMAN_SYSTEM_PROMPT = (
    "You are the Chairman of the Economics Council. You analyze user queries, the distinct opinions generated by "
    "specialist economic advisors, and their subsequent peer critiques. Your task is to synthesize a single, unified, "
    "high-quality, consensus-driven recommendation. You must highlight key areas of agreement, key points of disagreement/tensions, "
    "critical risks, and present a clear recommended decision. Use standard hyphens and spaces instead of em-dashes."
)

def query_ollama(model: str, system_prompt: str, user_prompt: str, retries: int = 3, delay: float = 2.0) -> str:
    """Query local Ollama chat endpoint with a system and user prompt."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }
    for attempt in range(retries):
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=240)
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "")
            else:
                print(f"[Ollama Error] Attempt {attempt+1}/{retries} returned status code {response.status_code}: {response.text}", file=sys.stderr)
        except Exception as e:
            print(f"[Ollama Connection Error] Attempt {attempt+1}/{retries} failed: {e}", file=sys.stderr)
        if attempt < retries - 1:
            time.sleep(delay * (2 ** attempt))
    raise RuntimeError(f"Ollama API query failed after {retries} attempts.")

def run_stage_1(model: str, topic: str) -> dict[str, str]:
    """Stage 1: Generate initial opinions from all 13 personas in parallel with limited concurrency."""
    print("Stage 1/3: Gathering initial opinions from 13 economic advisors...", flush=True)
    opinions = {}
    with ThreadPoolExecutor(max_workers=CONCURRENCY_LIMIT) as executor:
        futures = {
            executor.submit(query_ollama, model, data["system_prompt"], topic): key
            for key, data in PERSONAS.items()
        }
        for future in as_completed(futures):
            key = futures[future]
            title = PERSONAS[key]["title"]
            try:
                result = future.result()
                opinions[key] = result
                print(f"   [Opinion Ready] {title} has compiled initial insights.", flush=True)
            except Exception as e:
                print(f"   [ERROR] {title} failed: {e}", flush=True)
                opinions[key] = f"Error generating opinion: {e}"
    return opinions

def run_stage_2(model: str, topic: str, opinions: dict[str, str]) -> dict[str, str]:
    """Stage 2: Peer review. Each persona reviews all other opinions."""
    print("\nStage 2/3: Conducting peer reviews among advisors...", flush=True)
    
    # Format the debate context to show to all advisors
    context_lines = []
    for key, val in opinions.items():
        title = PERSONAS[key]["title"]
        context_lines.append(f"### Opinion by {title}:\n{val}\n")
    debate_context = "\n".join(context_lines)

    critiques = {}
    with ThreadPoolExecutor(max_workers=CONCURRENCY_LIMIT) as executor:
        futures = {}
        for key, data in PERSONAS.items():
            user_prompt = (
                f"You have been asked the following question: '{topic}'.\n\n"
                f"Here are the opinions of your colleagues in the Economics Council:\n\n"
                f"{debate_context}\n\n"
                f"Critique and review their arguments from your specific domain perspective. "
                f"Identify blind spots, logical contradictions, and provide constructive feedback on their conclusions. "
                f"Be direct, academic, and rigorous."
            )
            futures[executor.submit(query_ollama, model, data["system_prompt"], user_prompt)] = key

        for future in as_completed(futures):
            key = futures[future]
            title = PERSONAS[key]["title"]
            try:
                result = future.result()
                critiques[key] = result
                print(f"   [Critique Ready] {title} has completed critique on colleagues' opinions.", flush=True)
            except Exception as e:
                print(f"   [ERROR] {title} peer review failed: {e}", flush=True)
                critiques[key] = f"Error generating critique: {e}"
    return critiques

def run_stage_3(model: str, topic: str, opinions: dict[str, str], critiques: dict[str, str]) -> str:
    """Stage 3: Chairman Synthesis."""
    print("\nStage 3/3: Convening the Chairman for the final synthesis...", flush=True)
    
    deliberation_lines = []
    for key in PERSONAS.keys():
        title = PERSONAS[key]["title"]
        deliberation_lines.append(f"## Advisor: {title}\n")
        deliberation_lines.append(f"### Initial Opinion:\n{opinions[key]}\n")
        deliberation_lines.append(f"### Peer Review & Critique:\n{critiques[key]}\n")
    deliberation_text = "\n".join(deliberation_lines)

    user_prompt = (
        f"The Economics Council has deliberated on the topic: '{topic}'.\n\n"
        f"Here is the complete record of initial opinions and peer reviews:\n\n"
        f"{deliberation_text}\n\n"
        f"Provide the final synthesis, key agreements, disagreements, risks, and a recommended decision."
    )
    return query_ollama(model, CHAIRMAN_SYSTEM_PROMPT, user_prompt)

def run(topic: str, model: str) -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r"[^\w\s-]", "", topic.lower()).strip()
    slug = re.sub(r"\s+", "-", slug)[:80]

    print("\n🚀 === ECONOMICS COUNCIL DELIBERATION TRIGGERED ===", flush=True)
    print(f"Topic: {topic}\n", flush=True)
    print(f"Model: {model}", flush=True)
    print(f"Ollama Endpoint: {OLLAMA_URL}\n", flush=True)

    try:
        # Check connection to Ollama
        requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
    except Exception as e:
        print(f"ERROR: Could not connect to Ollama at '{OLLAMA_HOST}'. Make sure it is running (`ollama serve`).", flush=True)
        return 1

    # Execute stages
    opinions = run_stage_1(model, topic)
    critiques = run_stage_2(model, topic, opinions)
    synthesis = run_stage_3(model, topic, opinions, critiques)

    # Format the final markdown note
    fm = {
        "date": today,
        "type": "economics-council",
        "tags": ["economics", "thinking", "council"],
        "ai-first": True,
        "model": model,
        "topic": topic
    }

    # Build document sections
    body_parts = [
        f"# Economics Council Deliberation: {topic}",
        "\n## For future Claude",
        f"\n13-persona Economics Council execution grounded on local Ollama model `{model}`.",
        "\n## Executive Summary & Recommended Decision",
        synthesis,
        "\n## Deliberation Details\n"
    ]

    for key, data in PERSONAS.items():
        title = data["title"]
        body_parts.append(f"### {title}")
        body_parts.append(f"\n#### Initial Opinion\n{opinions[key]}\n")
        body_parts.append(f"\n#### Peer Critique\n{critiques[key]}\n")
        body_parts.append("---")

    body_text = "\n".join(body_parts)

    # Save to vault
    note_path = write_note("economics-council", topic, fm, body_text)
    
    payload = {
        "topic": topic,
        "today": today,
        "slug": slug,
        "saved_note": str(note_path.relative_to(VAULT_PATH)),
        "model": model,
    }

    print_save_links(note_path)
    print("<<<ECONOMICS_COUNCIL_PROPAGATION_PAYLOAD>>>")
    print(json.dumps(payload, indent=2))
    print("<<<ECONOMICS_COUNCIL_PROPAGATION_PAYLOAD>>>")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="Run 13-persona Economics Council via Ollama")
    parser.add_argument("topic", help="The question or decision to put to the council")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model name (default: {DEFAULT_MODEL})")
    args = parser.parse_args()
    return run(args.topic, args.model)

if __name__ == "__main__":
    sys.exit(main())
