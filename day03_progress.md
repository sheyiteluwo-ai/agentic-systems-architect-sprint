# Day 3 Progress Log — 02 May 2026

## ✅ Completed
- Added conversation memory to RAG system
- AI now remembers full conversation history across questions
- Added source page citations to every answer
- Tested with 4 consecutive questions that build on each other
- Memory confirmed working — 4 exchanges stored
- Citations confirmed working — Page 8 and Page 68 cited correctly

## 🧠 Key Learnings
- MessagesPlaceholder is the memory slot in LangChain prompts
- HumanMessage and AIMessage objects store conversation history
- Metadata from PDF loader contains page numbers automatically
- format_docs_with_citations() extracts page numbers from metadata
- Conversation history grows with each exchange and is passed
  to every new call — this is how the AI remembers context

## 📊 Day 3 Metrics
- Chunks loaded: 494
- Questions answered with memory: 4
- Source citations working: Yes — page numbers in every answer
- Memory exchanges stored: 4
- Commits today: 2

## 🎯 Day 4 Preview
- Prompt engineering for regulatory tone
- Add metadata filters to search specific sections
- Test with multiple UK compliance question types

## 💡 Interview Talking Point
"The system uses MessagesPlaceholder to maintain conversation 
history. Every exchange is stored as HumanMessage and AIMessage 
objects and passed to each new call. Combined with page-level 
source citations from the PDF metadata, every answer is both 
contextually aware and fully auditable — which is the standard 
required for FCA-regulated AI systems."