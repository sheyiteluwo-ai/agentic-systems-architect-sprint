"""
Day 3 — RAG with Conversation Memory + Source Citations
What this adds to Day 2:
- The AI remembers previous questions in the same session
- Every answer shows exactly which page it came from
- Conversation history is maintained throughout the chat
"""

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.vectorstores import DocArrayInMemorySearch

load_dotenv()

# ── STEP 1: Load and process the FCA document ─────────────────────────
print("📄 Loading FCA Consumer Duty document...")
loader = PyPDFLoader("fca_consumer_duty.pdf")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunks = splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()
vectorstore = DocArrayInMemorySearch.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
print(f"✅ Document ready — {len(chunks)} chunks loaded")

# ── STEP 2: Build the LLM ─────────────────────────────────────────────
llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

# ── STEP 3: Build prompt with memory slot ────────────────────────────
# MessagesPlaceholder is the memory slot
# It holds the full conversation history
# Think of it like a notepad the AI carries through the conversation
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert UK financial regulation assistant 
        specialising in FCA compliance. 

        Answer questions using ONLY the context provided below.
        
        IMPORTANT RULES:
        - Always cite the page number your answer comes from
        - Use exact obligation language from the document 
          (must/should/may)
        - If the answer spans multiple pages, cite all of them
        - If you cannot find the answer, say exactly:
          "This information was not found in the available 
          FCA documentation. Please consult the full document 
          or your compliance team."
        - Never fabricate regulatory references
        
        RETRIEVED CONTEXT:
        {context}"""
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

# ── STEP 4: Format docs with page citations ───────────────────────────
def format_docs_with_citations(docs):
    """
    Formats retrieved chunks AND includes page numbers.
    This is what gives us source citations in every answer.
    Think of it like footnotes in a legal document.
    """
    formatted = []
    for doc in docs:
        page = doc.metadata.get("page", "unknown")
        source = doc.metadata.get("source", "FCA document")
        formatted.append(
            f"[Page {page + 1}]\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(formatted)

# ── STEP 5: Build the chain ───────────────────────────────────────────
def create_rag_chain_with_memory():
    """
    Creates the RAG chain.
    This chain takes: question + chat_history + context
    Returns: answer with citations
    """
    chain = (
        {
            "context": lambda x: format_docs_with_citations(
                retriever.invoke(x["question"])
            ),
            "question": lambda x: x["question"],
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain

# ── STEP 6: The conversation manager ─────────────────────────────────
class FCAComplianceChat:
    """
    Manages the conversation session.
    Stores chat history so the AI remembers previous questions.
    
    This is what makes it feel like talking to a real expert
    rather than asking isolated questions.
    """
    
    def __init__(self):
        self.chat_history = []
        self.chain = create_rag_chain_with_memory()
        self.question_count = 0
        print("\n" + "="*60)
        print("🇬🇧 FCA COMPLIANCE ASSISTANT — READY")
        print("="*60)
        print("Ask any question about the FCA Consumer Duty.")
        print("The AI will remember your previous questions.")
        print("Every answer includes the source page number.")
        print("Type 'quit' to exit.")
        print("="*60 + "\n")
    
    def ask(self, question: str) -> str:
        """
        Takes a question, runs it through the RAG chain
        with full conversation history, returns answer.
        """
        self.question_count += 1
        
        # Get answer from chain
        answer = self.chain.invoke({
            "question": question,
            "chat_history": self.chat_history,
        })
        
        # Add this exchange to memory
        # This is how the AI remembers the conversation
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=answer))
        
        return answer
    
    def show_memory_summary(self):
        """Shows what the AI currently remembers."""
        print(f"\n📝 Memory: {len(self.chat_history) // 2} "
              f"exchanges stored in conversation history")


# ── STEP 7: Run the conversation ──────────────────────────────────────
def run_demo():
    """
    Runs a demonstration conversation showing memory working.
    Three questions that build on each other — 
    the third question references the first two.
    """
    chat = FCAComplianceChat()
    
    # These three questions are designed to show memory working
    # Question 3 asks about "the outcomes you mentioned" 
    # which only makes sense if the AI remembers Question 2
    demo_questions = [
        "What is the main purpose of the FCA Consumer Duty?",
        
        "What are the four outcomes and what does each one require?",
        
        "Based on the outcomes you just described, which one "
        "would be most relevant to a firm that sells investment "
        "products to retail customers?",
        
        "When did these rules come into force and were there "
        "different deadlines for different types of products?",
    ]
    
    for question in demo_questions:
        print(f"Question {chat.question_count + 1}:")
        print(f"Q: {question}")
        print()
        
        answer = chat.ask(question)
        
        print(f"A: {answer}")
        print()
        chat.show_memory_summary()
        print("\n" + "-"*60 + "\n")
    
    print("✅ Day 3 complete!")
    print("   Memory working — AI remembered context across 4 questions")
    print("   Source citations showing page numbers in every answer")
    print("   Check LangSmith: https://eu.smith.langchain.com")


if __name__ == "__main__":
    run_demo()