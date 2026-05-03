import streamlit as st
import requests
import json
from datetime import datetime

# ── Page configuration ────────────────────────────────────────────────
st.set_page_config(
    page_title="FCA Compliance Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS for professional styling ───────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1B2A4A 0%, #2E75B6 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .hitl-badge-safe {
        background-color: #C8E6C9;
        color: #1B5E20;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    .hitl-badge-flag {
        background-color: #FFF9C4;
        color: #F57F17;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    .hitl-badge-escalated {
        background-color: #FFCDD2;
        color: #B71C1C;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    .source-tag {
        background-color: #E3F2FD;
        color: #1565C0;
        padding: 2px 8px;
        border-radius: 8px;
        font-size: 11px;
        margin-right: 5px;
    }
    .compliance-notice {
        background-color: #FFF3E0;
        border-left: 4px solid #FF8C00;
        padding: 10px;
        border-radius: 4px;
        margin-top: 10px;
    }
    .escalated-notice {
        background-color: #FFEBEE;
        border-left: 4px solid #C00000;
        padding: 10px;
        border-radius: 4px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ── API Configuration ─────────────────────────────────────────────────
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except Exception:
        return False, None

def query_api(question, session_id, client_classification):
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={
                "question": question,
                "session_id": session_id,
                "client_classification": client_classification,
            },
            timeout=30,
        )
        if response.status_code == 200:
            return True, response.json()
        return False, {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return False, {"error": str(e)}

def clear_session(session_id):
    try:
        requests.delete(f"{API_BASE_URL}/session/{session_id}", timeout=5)
    except Exception:
        pass

# ── Session state initialisation ─────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = "ui-session-" + datetime.now().strftime("%H%M%S")
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "escalation_count" not in st.session_state:
    st.session_state.escalation_count = 0

# ── Header ────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏦 FCA Compliance Intelligence System</h1>
    <p>Production-grade RAG system — Consumer Duty | 
    Complaints | Vulnerable Customers</p>
    <p>Powered by GPT-4o | Human-in-the-Loop Safety Gates Active</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### System Settings")

    client_classification = st.selectbox(
        "Client Classification",
        ["retail", "professional", "eligible_counterparty"],
        help="Select the FCA client classification for this query"
    )

    st.markdown("---")
    st.markdown("### Session Info")
    st.code(f"Session: {st.session_state.session_id}")
    st.metric("Queries this session", st.session_state.query_count)
    st.metric("Escalations", st.session_state.escalation_count)

    if st.button("Clear Conversation", type="secondary"):
        clear_session(st.session_state.session_id)
        st.session_state.messages = []
        st.session_state.session_id = (
            "ui-session-" + datetime.now().strftime("%H%M%S")
        )
        st.session_state.query_count = 0
        st.session_state.escalation_count = 0
        st.rerun()

    st.markdown("---")
    st.markdown("### API Health")
    api_healthy, health_data = check_api_health()
    if api_healthy and health_data:
        st.success("API Online")
        st.metric("Chunks indexed", health_data.get("chunks_indexed", 0))
        st.metric("Docs loaded", health_data.get("documents_loaded", 0))
        st.caption(f"HITL Gate: {health_data.get('hitl_gate', 'unknown')}")
    else:
        st.error("API Offline")
        st.warning("Start the FastAPI server first: python day08_fastapi.py")

    st.markdown("---")
    st.markdown("### Example Questions")
    example_questions = [
        "What are the four outcomes of the Consumer Duty?",
        "How quickly must a firm respond to a complaint?",
        "What are the drivers of vulnerability?",
        "When did the Consumer Duty come into force?",
        "What is the maximum FOS compensation award?",
    ]
    for q in example_questions:
        if st.button(q, key=f"example_{q[:20]}", use_container_width=True):
            st.session_state.pending_question = q

    st.markdown("---")
    st.markdown("### About")
    st.caption(
        "Built as part of a 42-day Agentic AI sprint. "
        "Phase 1: RAG Knowledge Bot. "
        "github.com/sheyiteluwo-ai/agentic-systems-architect-sprint"
    )

# ── HITL Decision Colours ─────────────────────────────────────────────
def get_hitl_badge(decision):
    if decision == "answer_directly":
        return "hitl-badge-safe", "Safe"
    elif decision == "answer_with_flag":
        return "hitl-badge-flag", "Flagged"
    elif decision == "escalated":
        return "hitl-badge-escalated", "Escalated"
    return "hitl-badge-safe", decision

# ── Main chat area ────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### Compliance Query Interface")

    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar="🏦"):
                st.markdown(message["content"])

                # Show metadata
                if "metadata" in message:
                    meta = message["metadata"]
                    badge_class, badge_text = get_hitl_badge(
                        meta.get("hitl_decision", "")
                    )

                    cols = st.columns([2, 3, 2])
                    with cols[0]:
                        st.markdown(
                            f'<span class="{badge_class}">'
                            f'HITL: {badge_text}</span>',
                            unsafe_allow_html=True
                        )
                    with cols[1]:
                        sources = meta.get("sources_used", [])
                        if sources:
                            source_html = " ".join([
                                f'<span class="source-tag">{s[:25]}</span>'
                                for s in sources
                            ])
                            st.markdown(source_html, unsafe_allow_html=True)
                    with cols[2]:
                        ts = meta.get("timestamp", "")
                        if ts:
                            st.caption(ts[11:19])

    # Handle example question clicks
    if hasattr(st.session_state, "pending_question"):
        pending = st.session_state.pending_question
        del st.session_state.pending_question

        st.session_state.messages.append({
            "role": "user",
            "content": pending,
        })

        with st.spinner("Querying FCA compliance knowledge base..."):
            success, result = query_api(
                pending,
                st.session_state.session_id,
                client_classification,
            )

        if success:
            st.session_state.query_count += 1
            if result.get("escalated"):
                st.session_state.escalation_count += 1

            st.session_state.messages.append({
                "role": "assistant",
                "content": result.get("answer", "No answer returned"),
                "metadata": result,
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "API error: " + str(result.get("error", "")),
                "metadata": {},
            })
        st.rerun()

    # Chat input
    if prompt := st.chat_input(
        "Ask a compliance question about FCA regulations..."
    ):
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
        })

        with st.spinner("Querying FCA compliance knowledge base..."):
            success, result = query_api(
                prompt,
                st.session_state.session_id,
                client_classification,
            )

        if success:
            st.session_state.query_count += 1
            if result.get("escalated"):
                st.session_state.escalation_count += 1

            st.session_state.messages.append({
                "role": "assistant",
                "content": result.get("answer", "No answer returned"),
                "metadata": result,
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Could not connect to API. Make sure the "
                           "FastAPI server is running: "
                           "python day08_fastapi.py",
                "metadata": {},
            })
        st.rerun()

with col2:
    st.markdown("### Documents Loaded")
    documents = [
        ("FCA Consumer Duty", "PS22/9", "161 pages"),
        ("FCA Complaints", "DISP 1", "Rules"),
        ("Vulnerable Customers", "FG21/1", "Guidance"),
        ("Complaints Extended", "DISP", "Handbook"),
    ]
    for name, ref, pages in documents:
        with st.expander(f"{name}"):
            st.caption(f"Reference: {ref}")
            st.caption(f"Content: {pages}")

    st.markdown("### HITL Gate Status")
    st.markdown("""
    🟢 **Safe** — Answered directly

    🟡 **Flagged** — Compliance notice added

    🔴 **Escalated** — Routed to human review
    """)

    st.markdown("### Regulatory Frameworks")
    st.info("FCA Consumer Duty\nPS22/9 — July 2023")
    st.info("Complaints Handling\nDISP 1 — Handbook")
    st.info("Vulnerable Customers\nFG21/1 — Feb 2021")