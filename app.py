import streamlit as st
import os
import time
from dotenv import load_dotenv

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ArXiv Multi-Agent Research Summarizer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    .stApp { background: #0d1117; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 50%, #a5f3fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-sub {
        color: #8b949e;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }
    .agent-badge {
        display: inline-block;
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.78rem;
        color: #58a6ff;
        font-family: 'JetBrains Mono', monospace;
        margin: 2px;
    }
    .paper-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
    }
    .paper-title {
        font-weight: 600;
        color: #e6edf3;
        font-size: 0.95rem;
    }
    .paper-meta {
        color: #8b949e;
        font-size: 0.8rem;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 4px;
    }
    .metric-box {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .metric-num {
        font-size: 2rem;
        font-weight: 700;
        color: #58a6ff;
        font-family: 'Space Grotesk', sans-serif;
    }
    .metric-label {
        color: #8b949e;
        font-size: 0.8rem;
        margin-top: 4px;
    }
    .status-log {
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: #7ee787;
        max-height: 200px;
        overflow-y: auto;
    }
    .report-container {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 2rem;
    }
    div[data-testid="stSidebar"] {
        background: #161b22;
        border-right: 1px solid #30363d;
    }
    .stButton > button {
        background: linear-gradient(135deg, #238636, #2ea043);
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.6rem 2rem;
        width: 100%;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    api_key = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Get your key at https://aistudio.google.com/app/apikey",
    )
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key

    st.divider()

    num_questions = st.slider("Sub-questions to generate", 3, 5, 4,
                               help="More questions = broader coverage, slower runtime")
    papers_per_query = st.slider("Papers per sub-question", 5, 10, 7)

    st.divider()
    st.markdown("### 🤖 Agent Pipeline")
    for badge in ["Orchestrator", "Retriever", "Synthesizer"]:
        st.markdown(f'<span class="agent-badge">● {badge}</span>', unsafe_allow_html=True)

    st.divider()
    st.markdown(
        '<div style="color:#8b949e;font-size:0.8rem;">Powered by Google Gemini + ArXiv API<br>Multi-Agent System</div>',
        unsafe_allow_html=True,
    )

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🔬 ArXiv Research Summarizer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Multi-agent AI that decomposes your topic, retrieves papers from ArXiv, and synthesizes a structured literature review in minutes.</div>',
    unsafe_allow_html=True,
)

# ── Input ─────────────────────────────────────────────────────────────────────
topic = st.text_input(
    "Research Topic",
    placeholder="e.g., 'vision transformers for medical image segmentation'",
    label_visibility="collapsed",
)

col_btn, col_example = st.columns([2, 5])
with col_btn:
    run_btn = st.button("🚀 Generate Report", use_container_width=True)
with col_example:
    examples = [
        "diffusion models for drug discovery",
        "large language models for code generation",
        "federated learning for privacy preservation",
        "graph neural networks for molecular property prediction",
    ]
    example_pick = st.selectbox("Try an example →", [""] + examples, label_visibility="collapsed")
    if example_pick:
        topic = example_pick

# ── Session state ─────────────────────────────────────────────────────────────
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "log_messages" not in st.session_state:
    st.session_state.log_messages = []

# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn and topic:
    if not os.getenv("GEMINI_API_KEY"):
        st.error("❌ Please enter your Gemini API Key in the sidebar.")
        st.stop()

    from agents.orchestrator import decompose_topic
    from agents.retriever import retrieve_all_papers
    from agents.synthesizer import generate_final_report

    st.session_state.report_data = None
    st.session_state.log_messages = []

    log_placeholder = st.empty()
    progress_bar = st.progress(0, text="Initializing agents...")

    logs = []

    def log(msg: str):
        logs.append(f"› {msg}")
        st.session_state.log_messages = logs.copy()
        log_placeholder.markdown(
            '<div class="status-log">' + "<br>".join(logs[-8:]) + '</div>',
            unsafe_allow_html=True,
        )

    try:
        t0 = time.time()

        # Step 1: Decompose
        log("🧩 Orchestrator: decomposing research topic...")
        progress_bar.progress(10, text="Decomposing topic into sub-questions...")
        sub_questions = decompose_topic(topic, num_questions=num_questions)
        log(f"✅ Generated {len(sub_questions)} sub-questions")
        for q in sub_questions:
            log(f"  • {q}")

        # Step 2: Retrieve
        progress_bar.progress(25, text="Retrieving papers from ArXiv...")
        retrieval_results = retrieve_all_papers(
            sub_questions,
            topic,
            max_per_query=papers_per_query,
            progress_callback=log,
        )
        total_papers = sum(len(r["papers"]) for r in retrieval_results)
        progress_bar.progress(60, text="Summarizing papers...")

        # Step 3: Synthesize
        report_data = generate_final_report(
            topic,
            retrieval_results,
            progress_callback=log,
        )

        elapsed = time.time() - t0
        log(f"🎉 Done in {elapsed:.1f}s — report ready!")
        progress_bar.progress(100, text="Complete!")

        st.session_state.report_data = report_data
        st.session_state.elapsed = elapsed
        st.session_state.total_papers = total_papers

    except Exception as e:
        progress_bar.empty()
        log_placeholder.empty()
        st.error(f"❌ Pipeline error: {e}")
        st.exception(e)

elif run_btn and not topic:
    st.warning("Please enter a research topic.")

# ── Display Results ───────────────────────────────────────────────────────────
if st.session_state.report_data:
    data = st.session_state.report_data
    elapsed = st.session_state.get("elapsed", 0)
    total_papers = st.session_state.get("total_papers", 0)

    st.divider()

    # Metrics row
    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (len(data["sub_summaries"]), "Sub-questions"),
        (total_papers, "Papers Retrieved"),
        (sum(len(s["papers"]) for s in data["sub_summaries"]), "Papers Analyzed"),
        (f"{elapsed:.0f}s", "Time Taken"),
    ]
    for col, (val, label) in zip([c1, c2, c3, c4], metrics):
        with col:
            st.markdown(
                f'<div class="metric-box"><div class="metric-num">{val}</div><div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs
    tab_report, tab_papers, tab_questions = st.tabs(["📄 Full Report", "📚 Papers Found", "🔍 Sub-Questions"])

    with tab_report:
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.markdown(data["final_report"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.download_button(
            "⬇️ Download Report (.md)",
            data=data["final_report"],
            file_name=f"literature_review_{topic[:40].replace(' ', '_')}.md",
            mime="text/markdown",
        )

    with tab_papers:
        for section in data["sub_summaries"]:
            with st.expander(f"📂 {section['question']} ({len(section['papers'])} papers)", expanded=False):
                st.markdown(f"**ArXiv Query used:** `{section['query']}`")
                st.divider()
                for paper in section["papers"]:
                    authors = ", ".join(paper.get("authors", [])[:3])
                    st.markdown(
                        f'<div class="paper-card">'
                        f'<div class="paper-title">📄 {paper["title"]}</div>'
                        f'<div class="paper-meta">👥 {authors} &nbsp;|&nbsp; 📅 {paper.get("published","N/A")} &nbsp;|&nbsp; '
                        f'<a href="{paper["url"]}" target="_blank" style="color:#58a6ff;">ArXiv ↗</a></div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

    with tab_questions:
        st.markdown("### Decomposed Sub-Questions & Summaries")
        for i, section in enumerate(data["sub_summaries"], 1):
            with st.expander(f"Q{i}: {section['question']}", expanded=(i == 1)):
                st.markdown(section["summary"])
