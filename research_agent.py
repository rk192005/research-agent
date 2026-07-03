#!/usr/bin/env python3
"""
Research Agent — 100% Free Version
====================================
DuckDuckGo (web search, no API key) → Gemini 2.0 Flash (synthesis, free tier)

Zero cost. Zero credit card. Just a free Google API key from aistudio.google.com.

Usage:
    1. Get a free API key: https://aistudio.google.com/apikey
    2. export GEMINI_API_KEY="your-key"
    3. pip install google-genai duckduckgo-search
    4. python research_agent.py "Your research topic here"
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

REPORTS_DIR = Path(__file__).parent / "reports"
GEMINI_MODEL = "gemini-2.5-flash"


def search_web(topic: str, depth: str = "deep") -> str:
    """Agent 1: DuckDuckGo — free web search, no API key needed."""
    from duckduckgo_search import DDGS

    max_results = 15 if depth == "deep" else 7

    print(f"   Searching: {topic}")
    with DDGS() as ddgs:
        # Text search
        text_results = list(ddgs.text(topic, max_results=max_results))
        # News search for recent coverage
        news_results = list(ddgs.news(topic, max_results=5))

    # Format results into structured context
    findings = f"## Web Search Results for: {topic}\n\n"

    findings += "### Top Results\n"
    for i, r in enumerate(text_results, 1):
        findings += f"\n**{i}. {r.get('title', 'No title')}**\n"
        findings += f"   URL: {r.get('href', 'N/A')}\n"
        findings += f"   {r.get('body', 'No snippet')}\n"

    if news_results:
        findings += "\n### Recent News\n"
        for i, r in enumerate(news_results, 1):
            findings += f"\n**{i}. {r.get('title', 'No title')}**\n"
            findings += f"   Source: {r.get('source', 'N/A')} | Date: {r.get('date', 'N/A')}\n"
            findings += f"   URL: {r.get('url', 'N/A')}\n"
            findings += f"   {r.get('body', 'No snippet')}\n"

    return findings


def synthesize_report(topic: str, raw_findings: str) -> str:
    """Agent 2: Gemini 2.5 Flash — free-tier synthesis into a polished report."""
    from google import genai

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    system_prompt = """You are a senior research analyst who produces executive-grade research reports. 
You receive raw web search results and transform them into a polished, structured report.

Rules:
1. Lead with an executive summary (3-4 sentences max)
2. Organize findings by theme, not by source
3. Include a "So What?" section explaining practical implications
4. End with concrete next steps or recommendations
5. Preserve all source URLs in a References section
6. Use markdown formatting throughout
7. Be concise — every sentence must earn its place
8. If search results are thin on a subtopic, say so honestly — don't fabricate"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=f"""Create a research report on: {topic}

Here are the raw web search findings:

{raw_findings}

Produce a complete, well-structured report following your formatting rules.""",
        config={
            "system_instruction": system_prompt,
            "temperature": 0.3,
            "max_output_tokens": 8000,
        },
    )

    return response.text


def save_report(topic: str, raw_findings: str, final_report: str) -> Path:
    """Agent 3: Save the report locally as markdown."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in topic)[:80]
    date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"{date_str}_{safe_name}.md"
    filepath = REPORTS_DIR / filename

    full_doc = f"""# Research Report: {topic}

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}  
**Agent Pipeline**: DuckDuckGo (search) → Gemini 2.5 Flash (synthesis)  
**Cost**: $0.00

---

{final_report}

---

<details>
<summary>📋 Raw Search Results</summary>

{raw_findings}

</details>
"""

    filepath.write_text(full_doc, encoding="utf-8")
    return filepath


def run(topic: str, depth: str = "deep"):
    """Run the full 3-agent research pipeline — completely free."""
    print(f"\n{'='*60}")
    print(f"🔍 Research Agent (Free Edition)")
    print(f"📋 Topic: {topic}")
    print(f"📊 Depth: {depth}")
    print(f"💰 Cost: $0.00")
    print(f"{'='*60}\n")

    # --- Agent 1: DuckDuckGo ---
    print("🔍 Agent 1/3: DuckDuckGo — searching the web (free, no API key)...")
    try:
        raw_findings = search_web(topic, depth)
        result_count = raw_findings.count("**")
        print(f"   ✅ Got {len(raw_findings):,} chars across ~{result_count // 2} results\n")
    except Exception as e:
        print(f"   ❌ Search failed: {e}")
        sys.exit(1)

    # --- Agent 2: Gemini ---
    print("🧠 Agent 2/3: Gemini 2.5 Flash — synthesizing report (free tier)...")
    try:
        final_report = synthesize_report(topic, raw_findings)
        print(f"   ✅ Generated {len(final_report):,} char report\n")
    except Exception as e:
        # Save raw findings even if Gemini fails
        emergency = REPORTS_DIR / f"PARTIAL_{datetime.now():%Y%m%d_%H%M}.md"
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        emergency.write_text(raw_findings)
        print(f"   ❌ Gemini failed: {e}")
        print(f"   💾 Raw search results saved to: {emergency}")
        sys.exit(1)

    # --- Agent 3: Save ---
    print("📄 Agent 3/3: Saving report...")
    filepath = save_report(topic, raw_findings, final_report)
    print(f"   ✅ Saved to: {filepath}\n")

    print(f"{'='*60}")
    print(f"✅ Pipeline complete! Cost: $0.00")
    print(f"📄 Report: {filepath}")
    print(f"{'='*60}\n")

    return filepath


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python research_agent.py \"Your research topic\"")
        print("       python research_agent.py \"Your topic\" deep")
        print("       python research_agent.py \"Your topic\" quick")
        sys.exit(1)

    topic = sys.argv[1]
    depth = sys.argv[2] if len(sys.argv) > 2 else "deep"
    run(topic, depth)
