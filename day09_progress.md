# Day 9 Progress Log — 04 May 2026

## Completed
- Built professional Streamlit chat UI
- Connected UI to FastAPI backend via HTTP requests
- Professional navy gradient header with system description
- Left sidebar: client classification, session info, API health
- Real-time query and escalation counters
- Colour-coded HITL badges: Safe/Flagged/Escalated
- Source document tags on every answer
- Timestamp on every response
- Four document expandable panels on right
- HITL Gate Status legend visible at all times
- Regulatory Frameworks quick reference
- Clear Conversation button with session reset
- Example questions in sidebar for quick testing
- Tested safe answer — green HITL badge
- Tested escalated question — red HITL badge, REF-0001
- Escalation counter updated automatically to 1

## Key Learnings
- Streamlit session_state persists data across reruns
- st.chat_message creates professional chat bubbles
- st.rerun() refreshes the UI after each query
- Two terminals needed — one FastAPI, one Streamlit
- Split terminal in VS Code is the cleanest approach
- CSS styling in st.markdown makes Streamlit look professional
- API health check in sidebar gives real-time system status

## Metrics
- UI components built: 15+
- Questions tested: 2
- Safe answers: 1
- Escalations: 1
- Session counter: Working
- API health indicator: Working
- Source tags: Working on every answer
- Commits today: 1

## Day 10 Preview
- Production hardening
- Error handling for edge cases
- Rate limiting
- Retry logic for API failures
- Logging

## Interview Talking Point
"My compliance system has a professional Streamlit chat
interface that non-technical users can use without knowing
anything about code. Every answer shows a colour-coded
HITL safety badge — green for safe, yellow for flagged,
red for escalated to human review. A compliance officer
at Barclays could open this in their browser today and
start querying FCA regulatory documents immediately.
The session tracks all queries and escalations in real
time on the sidebar."