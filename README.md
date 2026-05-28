# 🔬 ArXiv Multi-Agent Research Summarizer

A multi-agent AI system that decomposes a research topic into targeted sub-questions, retrieves and processes ArXiv papers, and synthesizes a structured literature review — reducing literature review time from ~3 hours to under 5 minutes.

## 🏗️ Architecture

```
User Topic
    │
    ▼
┌─────────────────────┐
│   Orchestrator      │  Gemini decomposes topic → 3–5 sub-questions
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│   Retriever         │  ArXiv API fetches 5–10 papers per sub-question
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│   Synthesizer       │  Gemini summarizes papers → structured report
└─────────────────────┘
    │
    ▼
Structured Literature Review (Markdown)
```

## 📁 File Structure

```
arxiv-multi-agent/
├── app.py                  # Streamlit frontend
├── agents/
│   ├── orchestrator.py     # Topic decomposition agent
│   ├── retriever.py        # ArXiv paper retrieval agent
│   └── synthesizer.py      # Summarization & report generation agent
├── utils/
│   ├── gemini_client.py    # Google Gemini API wrapper
│   └── arxiv_client.py     # ArXiv API wrapper
├── prompts/
│   ├── decompose.py        # Sub-question generation prompts
│   ├── summarize.py        # Paper summarization prompts
│   └── synthesize.py       # Final report prompts
├── requirements.txt
├── .env.example
└── .streamlit/config.toml
```

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/arxiv-multi-agent.git
cd arxiv-multi-agent
pip install -r requirements.txt
```

### 2. Set API Key

```bash
cp .env.example .env
# Edit .env and add your Gemini API key
# Get one free at: https://aistudio.google.com/app/apikey
```

### 3. Run Locally

```bash
streamlit run app.py
```

## ☁️ Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo → set `app.py` as main file
4. Under **Advanced settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_key_here"
   ```
5. Click **Deploy** — live in ~60 seconds

## 🔑 Getting a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with Google
3. Click **Create API Key**
4. Copy and paste into the app sidebar or `.env` file

The free tier is sufficient for dozens of reports per day.

## 📊 Tech Stack

- **Python** — Core language
- **Google Gemini API** (`google-generativeai`) — NLU, summarization, synthesis
- **ArXiv API** — Open-access paper retrieval (no API key needed)
- **Streamlit** — Web UI and deployment
- **Prompt Engineering** — Structured multi-step prompts per agent
- **Multi-Agent Design** — Orchestrator → Retriever → Synthesizer pipeline

## ⚡ Performance

| Metric | Value |
|--------|-------|
| Topic decomposition | ~5 seconds |
| Paper retrieval (4 queries × 7 papers) | ~15 seconds |
| Summarization + report | ~30–60 seconds |
| **Total end-to-end** | **~1–3 minutes** |
| Traditional manual review | ~3+ hours |

## 📄 License

MIT
