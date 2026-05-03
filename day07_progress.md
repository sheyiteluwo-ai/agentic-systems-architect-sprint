# Day 7 Progress Log — 04 May 2026

## Completed
- Fixed 3 failing evaluation questions from Day 6
- Added fca_complaints_extended.txt with FOS limits
- Reduced chunk size to 800 and increased overlap to 300
- Re-ran evaluation — score jumped from 0.66 to 0.94/1.0
- Built Human-in-the-Loop gate with 30 escalation triggers
- Built flag system with 11 obligation keywords
- Tested HITL with 7 questions — 2 correctly escalated
- Sue/legal action questions routed to human review
- Pension compensation questions routed to human review
- FOS 415000 compensation answer now correct
- Complaint record keeping answer now correct

## Key Learnings
- Smaller chunks (800) with more overlap (300) fixes context loss
- Adding missing source document fixes factual gaps immediately
- Evaluation score is a feedback loop not a one-time measure
- HITL triggers must be specific enough to catch real risks
- Personal situation questions always need human review
- Legal liability questions always need human review
- 0.94 eval score means system is production-grade

## Metrics
- Eval score Day 6: 0.66/1.0
- Eval score Day 7: 0.94/1.0
- Improvement: +0.28 points (+42%)
- HITL escalations: 2 of 7 questions
- Flagged with notice: 2 of 7 questions
- Direct answers: 3 of 7 questions
- Documents in knowledge base: 4
- Commits today: 1

## Day 8 Preview
- FastAPI REST wrapper
- Expose RAG system as a proper API endpoint
- Test with Postman
- Makes system callable from any application

## Interview Talking Point
"On Day 6 my evaluation score was 0.66 — borderline.
I identified three root causes: missing source documents,
chunk size too large causing context loss, and insufficient
overlap between chunks. I fixed all three and re-ran the
evaluation on Day 7. Score jumped to 0.94. That is how
enterprise AI quality assurance works — measure, identify,
fix, measure again. The HITL gate correctly escalated
legal liability and personal situation questions to human
review, leaving the AI to answer only safe general queries."