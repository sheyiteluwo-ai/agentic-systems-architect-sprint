"""
Day 5 — Multi-Document RAG System
What this builds:
- Loads 3 FCA documents simultaneously (PDF + TXT)
- Tags every chunk with its source document
- Answers questions across all three documents at once
- Shows which document and page each answer came from
- Handles questions that require cross-document knowledge
"""

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.vectorstores import DocArrayInMemorySearch

load_dotenv()

# ── STEP 1: Load all three FCA documents ─────────────────────────────
print("📚 Loading 3 FCA documents...")
print()

# Document 1 — FCA Consumer Duty (PDF)
print("   📄 Loading Document 1: FCA Consumer Duty...")
pdf_loader = PyPDFLoader("fca_consumer_duty.pdf")
consumer_duty_docs = pdf_loader.load()
# Tag every page with its source
for doc in consumer_duty_docs:
    doc.metadata["source_doc"] = "FCA Consumer Duty (PS22/9)"
    doc.metadata["doc_type"]   = "Policy Statement"
    doc.metadata["page_display"] = doc.metadata.get("page", 0) + 1
print(f"   ✅ Loaded {len(consumer_duty_docs)} pages")

# Document 2 — FCA Complaints Rules (TXT)
print("   📄 Loading Document 2: FCA Complaints Rules...")
txt_loader1 = TextLoader("fca_complaints_rules.txt", encoding="utf-8")
complaints_docs = txt_loader1.load()
# Tag with source
for doc in complaints_docs:
    doc.metadata["source_doc"]   = "FCA Complaints Handling (DISP 1)"
    doc.metadata["doc_type"]     = "Handbook Rules"
    doc.metadata["page_display"] = 1
print(f"   ✅ Loaded {len(complaints_docs)} section(s)")

# Document 3 — FCA Vulnerable Customers (TXT)
print("   📄 Loading Document 3: FCA Vulnerable Customers...")
txt_loader2 = TextLoader("fca_vulnerable_customers.txt", encoding="utf-8")
vulnerable_docs = txt_loader2.load()
# Tag with source
for doc in vulnerable_docs:
    doc.metadata["source_doc"]   = "FCA Vulnerable Customers (FG21/1)"
    doc.metadata["doc_type"]     = "Finalised Guidance"
    doc.metadata["page_display"] = 1
print(f"   ✅ Loaded {len(vulnerable_docs)} section(s)")

# ── STEP 2: Combine all documents ────────────────────────────────────
all_documents = consumer_duty_docs + complaints_docs + vulnerable_docs
print(f"\n📊 Total documents loaded: {len(all_documents)}")
print(f"   Consumer Duty pages:      {len(consumer_duty_docs)}")
print(f"   Complaints sections:      {len(complaints_docs)}")
print(f"   Vulnerable Customers:     {len(vulnerable_docs)}")

# ── STEP 3: Split into chunks ─────────────────────────────────────────
print("\n✂️  Splitting all documents into chunks...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
all_chunks = splitter.split_documents(all_documents)
print(f"✅ Created {len(all_chunks)} total chunks across all 3 documents")

# Show chunk distribution per document
chunk_counts = {}
for chunk in all_chunks:
    src = chunk.metadata.get("source_doc", "Unknown")
    chunk_counts[src] = chunk_counts.get(src, 0) + 1

print("\n📊 Chunks per document:")
for src, count in chunk_counts.items():
    print(f"   {src}: {count} chunks")

# ── STEP 4: Build unified vector store ───────────────────────────────
print("\n🗄️  Building unified vector store across all 3 documents...")
embeddings  = OpenAIEmbeddings()
vectorstore = DocArrayInMemorySearch.from_documents(
    all_chunks, embeddings
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
print("✅ Unified vector store ready")

# ── STEP 5: Multi-document aware prompt ──────────────────────────────
MULTI_DOC_PROMPT = """You are a Senior UK Compliance Officer with 
expertise across FCA Consumer Duty, complaints handling, and 
vulnerable customer regulations.

You have access to THREE FCA regulatory documents:
1. FCA Consumer Duty (PS22/9) — retail customer outcomes
2. FCA Complaints Handling (DISP 1) — complaints procedures  
3. FCA Vulnerable Customers (FG21/1) — vulnerability guidance

STRICT RULES:
1. Always cite which document your answer comes from
2. Format citations as: [Document Name, Page/Section X]
3. If the answer spans multiple documents, cite all of them
4. Use exact obligation language: must/should/may
5. Highlight when rules from different documents interact
6. If information is not in any document say so explicitly

RETRIEVED CONTEXT FROM ALL THREE DOCUMENTS:
{context}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", MULTI_DOC_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

# ── STEP 6: Format chunks with full source information ────────────────
def format_multi_doc_chunks(docs):
    """
    Formats retrieved chunks showing which document
    each chunk came from.
    This is the key feature of multi-document RAG —
    you can see exactly which document answered your question.
    """
    formatted = []
    for doc in docs:
        source = doc.metadata.get("source_doc", "Unknown")
        doc_type = doc.metadata.get("doc_type", "")
        page = doc.metadata.get("page_display", "?")
        formatted.append(
            f"[SOURCE: {source} | {doc_type} | Page/Section {page}]\n"
            f"{doc.page_content}"
        )
    return "\n\n---\n\n".join(formatted)

# ── STEP 7: Multi-document chat system ───────────────────────────────
class MultiDocComplianceChat:
    """
    Queries across all three FCA documents simultaneously.
    Shows exactly which document each answer came from.
    """

    def __init__(self):
        self.chat_history = []
        self.llm   = ChatOpenAI(model="gpt-4o", temperature=0.1)
        self.chain = prompt | self.llm | StrOutputParser()
        self.question_count = 0

        print("\n" + "="*65)
        print("🇬🇧 MULTI-DOCUMENT FCA COMPLIANCE SYSTEM")
        print("="*65)
        print("Documents loaded:")
        print("  1. FCA Consumer Duty (PS22/9)")
        print("  2. FCA Complaints Handling (DISP 1)")
        print("  3. FCA Vulnerable Customers (FG21/1)")
        print("="*65 + "\n")

    def ask(self, question: str) -> str:
        self.question_count += 1
        print(f"\n{'='*65}")
        print(f"Q{self.question_count}: {question}")
        print(f"{'='*65}")

        # Retrieve from ALL documents simultaneously
        docs    = retriever.invoke(question)
        context = format_multi_doc_chunks(docs)

        # Show which documents were retrieved
        sources = list(set(
            d.metadata.get("source_doc", "Unknown") for d in docs
        ))
        print(f"📚 Sources retrieved: {', '.join(sources)}")

        # Generate answer
        answer = self.chain.invoke({
            "context":      context,
            "question":     question,
            "chat_history": self.chat_history,
        })

        # Store in memory
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=answer))

        print(f"\nA: {answer}")
        print(f"\n📝 Memory: {len(self.chat_history)//2} exchanges")
        return answer


# ── STEP 8: Test with cross-document questions ────────────────────────
def run_demo():
    chat = MultiDocComplianceChat()

    questions = [
        # Tests Consumer Duty document
        "What are a firm's main obligations under "
        "the FCA Consumer Duty?",

        # Tests Complaints document
        "What are the FCA rules on how quickly a firm "
        "must respond to a customer complaint?",

        # Tests Vulnerable Customers document
        "What does the FCA expect firms to do when "
        "they identify a vulnerable customer?",

        # CROSS-DOCUMENT question — requires knowledge
        # from Consumer Duty AND Vulnerable Customers
        "How do the Consumer Duty requirements interact "
        "with the FCA's vulnerable customer guidance? "
        "What must a firm do differently for vulnerable "
        "customers under both frameworks?",

        # CROSS-DOCUMENT question — requires all 3 documents
        "If a vulnerable customer makes a complaint about "
        "an investment product, what obligations does the "
        "firm have under all three regulatory frameworks?",
    ]

    for question in questions:
        chat.ask(question)

    print("\n" + "="*65)
    print("✅ Day 5 complete!")
    print(f"   Documents loaded: 3 FCA regulatory sources")
    print(f"   Total chunks: {len(all_chunks)}")
    print(f"   Cross-document queries: Working")
    print(f"   Source attribution: Every answer cites its document")
    print("   Check LangSmith: https://eu.smith.langchain.com")
    print("="*65)


if __name__ == "__main__":
    run_demo()