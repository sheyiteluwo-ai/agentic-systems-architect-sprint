# Day 2 Progress Log — 01 May 2026

## ✅ Completed
- Downloaded real FCA Consumer Duty PDF (161 pages)
- Loaded PDF using PyPDFLoader
- Split into 494 chunks using RecursiveCharacterTextSplitter
- Built vector store using OpenAI embeddings
- Built RAG chain using modern LangChain LCEL syntax
- Asked 3 real UK compliance questions — all answered correctly
- Answers sourced directly from FCA document, not AI memory

## 🧠 Key Learnings
- RAG = giving AI a filing cabinet of real documents to search
- chunk_size=1000 and chunk_overlap=200 is the sweet spot for regulatory docs
- DocArrayInMemorySearch works better than ChromaDB on Windows
- Modern LangChain uses LCEL syntax: retriever | prompt | llm | parser

## 📊 Day 2 Metrics
- PDF pages loaded: 161
- Chunks created: 494
- Questions answered correctly: 3/3
- Commits today: 2

## 🎯 Day 3 Preview
- Add conversation memory so the AI remembers previous questions
- Add source page citations to every answer
- Build a simple chat interface