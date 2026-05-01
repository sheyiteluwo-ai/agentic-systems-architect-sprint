"""
Day 2 — RAG Document Loader (Windows Compatible)
Loads a real FCA PDF and answers questions from it.
Uses in-memory vector store — faster and cleaner on Windows.
"""

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import DocArrayInMemorySearch

load_dotenv()

# ── STEP 1: Load the PDF ──────────────────────────────────────────────
print("📄 Step 1: Loading FCA PDF...")
loader = PyPDFLoader("fca_consumer_duty.pdf")
documents = loader.load()
print(f"✅ Loaded {len(documents)} pages from the PDF")

# ── STEP 2: Split into chunks ─────────────────────────────────────────
print("\n✂️  Step 2: Splitting into chunks...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunks = splitter.split_documents(documents)
print(f"✅ Created {len(chunks)} chunks")

# ── STEP 3: Store in memory ───────────────────────────────────────────
print("\n🗄️  Step 3: Building vector store...")
embeddings = OpenAIEmbeddings()
vectorstore = DocArrayInMemorySearch.from_documents(
    chunks,
    embeddings
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
print("✅ Vector store ready")

# ── STEP 4: Build RAG chain ───────────────────────────────────────────
print("\n🤖 Step 4: Building RAG chain...")
llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

prompt = ChatPromptTemplate.from_template("""
You are an expert on UK financial regulation.
Answer the question using ONLY the context below.
If the answer is not in the context, say "Not found in document."

Context:
{context}

Question: {question}
""")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
print("✅ RAG chain ready")

# ── STEP 5: Ask questions ─────────────────────────────────────────────
print("\n" + "="*60)
print("🇬🇧 FCA CONSUMER DUTY — DOCUMENT Q&A")
print("="*60)

questions = [
    "What is the main purpose of the Consumer Duty?",
    "What are the four outcomes of the Consumer Duty?",
    "When did the Consumer Duty come into force?",
]

for i, question in enumerate(questions, 1):
    print(f"\n--- Question {i} ---")
    print(f"Q: {question}")
    answer = rag_chain.invoke(question)
    print(f"A: {answer}")

print("\n✅ Day 2 complete!")
print("   Your AI answered questions from a REAL 161-page FCA document.")
print("   Check LangSmith at https://eu.smith.langchain.com")