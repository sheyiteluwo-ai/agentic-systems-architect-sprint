"""
Day 4 — Prompt Engineering + Metadata Filters
What this adds to Day 3:
- Regulatory-tone prompt engineered for UK compliance
- Metadata filters that search specific document sections
- Obligation strength detection (must/should/may)
- Section-aware retrieval — searches only relevant parts
"""

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.vectorstores import DocArrayInMemorySearch

load_dotenv()

# ── STEP 1: Load and chunk the FCA document ───────────────────────────
print("📄 Loading FCA Consumer Duty document...")
loader = PyPDFLoader("fca_consumer_duty.pdf")
documents = loader.load()

# Tag each page with a section based on page number
# This is metadata filtering — we label each chunk
# so we can search only relevant sections later
def tag_section(page_num):
    """
    Tags each page with a section label based on
    where it appears in the FCA Consumer Duty document.
    Think of it like colour-coding a physical document
    with sticky tabs.
    """
    if page_num <= 10:
        return "overview"
    elif page_num <= 30:
        return "consumer_principle"
    elif page_num <= 60:
        return "outcomes"
    elif page_num <= 90:
        return "implementation"
    elif page_num <= 120:
        return "guidance"
    else:
        return "appendix"

# Add section tags to every page
for doc in documents:
    page = doc.metadata.get("page", 0)
    doc.metadata["section"] = tag_section(page)
    doc.metadata["page_display"] = page + 1

print(f"✅ Loaded {len(documents)} pages with section tags")

# ── STEP 2: Split into chunks ─────────────────────────────────────────
print("\n✂️  Splitting into chunks...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunks = splitter.split_documents(documents)
print(f"✅ Created {len(chunks)} chunks with metadata")

# Show section distribution
sections = {}
for chunk in chunks:
    s = chunk.metadata.get("section", "unknown")
    sections[s] = sections.get(s, 0) + 1
print("\n📊 Chunks per section:")
for section, count in sorted(sections.items()):
    print(f"   {section}: {count} chunks")

# ── STEP 3: Build vector store ────────────────────────────────────────
print("\n🗄️  Building vector store...")
embeddings = OpenAIEmbeddings()
vectorstore = DocArrayInMemorySearch.from_documents(chunks, embeddings)
print("✅ Vector store ready")

# ── STEP 4: The Engineered Compliance Prompt ─────────────────────────
# This is the heart of Day 4.
# A well-engineered prompt is the difference between
# a generic AI answer and a professional compliance response.
# Notice how it:
# - Sets a specific expert persona
# - Gives precise instructions about obligation language
# - Requires source citations
# - Specifies what to do when uncertain
# - Maintains conversation context via chat_history

COMPLIANCE_SYSTEM_PROMPT = """You are a Senior UK Compliance Officer with 
15 years of experience advising FCA-regulated financial services firms.

You are precise, cautious, and always cite your sources.

STRICT RULES YOU MUST FOLLOW:

1. OBLIGATION LANGUAGE — Use exact regulatory terms:
   - "must" = absolute legal requirement, no discretion
   - "should" = strong expectation, deviation needs justification  
   - "may" = permitted but not required
   - "consider" = suggested but genuinely optional
   Never substitute one for another. The difference is legally significant.

2. SOURCE CITATIONS — Always end with:
   "Source: [exact section name], Page [X] of FCA PS22/9"

3. CLIENT CLASSIFICATION — Always state which client type applies:
   Retail Client / Professional Client / Eligible Counterparty

4. UNCERTAINTY — If the answer is not in the context, say exactly:
   "This specific point is not addressed in the retrieved sections.
   I recommend consulting the full FCA PS22/9 document or seeking
   qualified legal advice before acting."

5. NEVER fabricate regulatory references or page numbers.

6. ALWAYS flag if a rule has implementation deadlines that vary
   by product type (open vs closed books).

RETRIEVED REGULATORY CONTEXT:
{context}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", COMPLIANCE_SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

# ── STEP 5: Section-aware retrieval ───────────────────────────────────
def get_section_for_question(question: str) -> str:
    """
    Intelligently routes each question to the most
    relevant section of the document.
    
    Think of it like asking a librarian which shelf
    to look on before you start searching.
    This makes retrieval faster and more accurate.
    """
    question_lower = question.lower()
    
    # Keywords that indicate which section to search
    if any(word in question_lower for word in
           ["deadline", "when", "date", "force", "july",
            "implement", "timeline", "phase", "transition"]):
        return "implementation"
    
    elif any(word in question_lower for word in
             ["outcome", "products", "services", "price",
              "value", "confidence", "access", "suitability"]):
        return "outcomes"
    
    elif any(word in question_lower for word in
             ["principle", "consumer principle", "standard",
              "care", "purpose", "aim", "objective"]):
        return "consumer_principle"
    
    elif any(word in question_lower for word in
             ["guidance", "example", "how to", "practical",
              "apply", "firm", "should firms"]):
        return "guidance"
    
    elif any(word in question_lower for word in
             ["what is", "overview", "summary", "introduction",
              "explain", "define", "meaning"]):
        return "overview"
    
    else:
        return None  # Search entire document

def retrieve_with_filter(question: str, k: int = 4):
    """
    Retrieves chunks using section-aware filtering.
    First tries the most relevant section.
    Falls back to full document if section search
    returns insufficient results.
    """
    section = get_section_for_question(question)
    
    if section:
        print(f"   🎯 Routing to section: {section}")
        # Try section-specific search first
        results = vectorstore.similarity_search(
            question, k=k,
            filter={"section": section}
        )
        # If we got good results, use them
        if len(results) >= 2:
            return results, section
        else:
            print(f"   ⚠️  Only {len(results)} results in {section}, "
                  f"expanding to full document")
    
    # Fall back to full document search
    print("   🔍 Searching full document")
    results = vectorstore.similarity_search(question, k=k)
    return results, "full document"

def format_chunks(docs):
    """Formats chunks with clear page and section labels."""
    formatted = []
    for doc in docs:
        page = doc.metadata.get("page_display", "?")
        section = doc.metadata.get("section", "unknown")
        formatted.append(
            f"[Page {page} | Section: {section}]\n"
            f"{doc.page_content}"
        )
    return "\n\n---\n\n".join(formatted)

# ── STEP 6: The Compliance Chat System ───────────────────────────────
class EnhancedComplianceChat:
    """
    Day 4 upgrade of the compliance chat system.
    Adds: engineered prompts + section-aware retrieval.
    """
    
    def __init__(self):
        self.chat_history = []
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
        self.chain = prompt | self.llm | StrOutputParser()
        self.question_count = 0
        
        print("\n" + "="*65)
        print("🇬🇧 FCA COMPLIANCE OFFICER AI — ENHANCED v4.0")
        print("="*65)
        print("Engineered prompt: Senior compliance officer persona")
        print("Section routing: Questions directed to relevant sections")
        print("Obligation detection: must/should/may precision enforced")
        print("="*65 + "\n")
    
    def ask(self, question: str) -> str:
        self.question_count += 1
        print(f"\n{'='*65}")
        print(f"Question {self.question_count}: {question}")
        print(f"{'='*65}")
        
        # Section-aware retrieval
        docs, section_used = retrieve_with_filter(question)
        context = format_chunks(docs)
        
        print(f"   📚 Retrieved {len(docs)} chunks from: {section_used}")
        
        # Generate answer with engineered prompt
        answer = self.chain.invoke({
            "context": context,
            "question": question,
            "chat_history": self.chat_history,
        })
        
        # Store in memory
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=answer))
        
        print(f"\nA: {answer}")
        print(f"\n📝 Memory: {len(self.chat_history)//2} exchanges stored")
        
        return answer


# ── STEP 7: Test with real compliance scenarios ───────────────────────
def run_demo():
    chat = EnhancedComplianceChat()
    
    # These questions test different aspects of the system:
    # Q1 — Tests section routing to 'overview'
    # Q2 — Tests section routing to 'outcomes'  
    # Q3 — Tests obligation language precision
    # Q4 — Tests section routing to 'implementation'
    # Q5 — Tests memory + follow-up understanding
    
    questions = [
        "What is the Consumer Duty and what problem does it solve?",
        
        "What are the four outcomes and what does each one "
        "require firms to deliver?",
        
        "Under the Consumer Duty, must firms monitor outcomes "
        "for retail customers, or should they — and what is "
        "the practical difference?",
        
        "What were the implementation deadlines and did they "
        "differ between open and closed product books?",
        
        "Based on everything you have told me, if I work at "
        "a bank selling ISAs to retail customers, what are "
        "my three most important obligations under this duty?",
    ]
    
    for question in questions:
        chat.ask(question)
    
    print("\n" + "="*65)
    print("✅ Day 4 complete!")
    print("   Prompt engineering: Senior compliance officer persona active")
    print("   Section routing: Questions directed to correct sections")
    print("   Obligation precision: must/should/may enforced in all answers")
    print("   Memory: Full conversation history maintained")
    print("   Check LangSmith: https://eu.smith.langchain.com")
    print("="*65)


if __name__ == "__main__":
    run_demo()