# Research Agent — Autopilot System (Free Edition)

**$0 total cost.** No credit card needed anywhere.

| Component | What it does | Cost |
|-----------|-------------|------|
| **DuckDuckGo** | Web search + news | Free, no API key |
| **Gemini 2.5 Flash** | Report synthesis | Free tier (1,500 req/day) |
| **Make.com** | Cloud automation | Free tier (1,000 ops/month) |

## Quick Start (5 minutes)

### Step 1: Get a free Gemini API key
1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click **Create API Key** → copy it
4. No credit card. No billing. Just free.

### Step 2: Run it

```bash
cd ~/Automation/research-agent
python3 -m venv .venv
source .venv/bin/activate
pip install google-genai duckduckgo-search

export GEMINI_API_KEY="your-key-here"  # DON'T paste real keys in files

# Single topic
python research_agent.py "Latest trends in edge AI for IoT" deep

# Batch mode — process all pending from CSV
cp research_queue_template.csv research_queue.csv
python batch_runner.py

# Daemon mode — auto-check every 15 min
python batch_runner.py --watch
```

### Step 3 (Optional): Make.com cloud automation
1. Sign up at [make.com](https://www.make.com) (free)
2. Import `make_scenario_blueprint.json`
3. Swap the Perplexity module for an **HTTP module** calling DuckDuckGo
4. Swap the Claude module for the **Google Gemini** module (free API key)

## Files

| File | Purpose |
|------|---------|
| `research_agent.py` | Core 3-agent pipeline (single topic) |
| `batch_runner.py` | Queue processor with watch mode |
| `research_queue_template.csv` | CSV queue with sample topics |
| `make_scenario_blueprint.json` | Make.com scenario (original paid version) |
| `reports/` | Output directory for generated reports |

## Free Tier Limits (Gemini 2.5 Flash)

| Limit | Value | What it means |
|-------|-------|---------------|
| Requests/min | 15 | Max 15 reports started per minute |
| Requests/day | 1,500 | Plenty for personal use |
| Tokens/min | 1,000,000 | ~750K words — more than enough |

At 3-5 reports per day you won't hit any of these.
