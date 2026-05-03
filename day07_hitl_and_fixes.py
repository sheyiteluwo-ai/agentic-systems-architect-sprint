import json
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.vectorstores import DocArrayInMemorySearch

load_dotenv()

print("Loading documents...")

def load_and_tag(loader, source_doc, doc_type):
    docs = loader.load()
    for doc in docs:
        doc.metadata["source_doc"] = source_doc
        doc.metadata["doc_type"] = doc_type
        doc.metadata["page_display"] = doc.metadata.get("page", 0) + 1
    return docs

consumer_duty_docs = load_and_tag(
    PyPDFLoader("fca_consumer_duty.pdf"),
    "FCA Consumer Duty PS22/9", "Policy Statement"
)
complaints_docs = load_and_tag(
    TextLoader("fca_complaints_rules.txt", encoding="utf-8"),
    "FCA Complaints DISP 1", "Handbook Rules"
)
vulnerable_docs = load_and_tag(
    TextLoader("fca_vulnerable_customers.txt", encoding="utf-8"),
    "FCA Vulnerable Customers FG21/1", "Finalised Guidance"
)
extended_docs = load_and_tag(
    TextLoader("fca_complaints_extended.txt", encoding="utf-8"),
    "FCA Complaints Extended DISP", "Handbook Rules"
)

all_documents = (consumer_duty_docs + complaints_docs +
                 vulnerable_docs + extended_docs)
print(f"Loaded {len(all_documents)} total document sections")

print("Building vector store...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=300,
)
all_chunks = splitter.split_documents(all_documents)
print(f"Created {len(all_chunks)} chunks")

embeddings = OpenAIEmbeddings()
vectorstore = DocArrayInMemorySearch.from_documents(all_chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
print("Vector store ready")

class HITLDecision(Enum):
    ANSWER_DIRECTLY   = "answer_directly"
    ANSWER_WITH_FLAG  = "answer_with_flag"
    ESCALATE_TO_HUMAN = "escalate_to_human"

ESCALATION_TRIGGERS = [
    "sue", "legal action", "court", "tribunal",
    "liability", "compensation claim", "damages",
    "enforcement", "investigation", "prosecution",
    "my specific case", "my complaint", "my situation",
    "should i complain", "can i get compensation",
    "am i entitled", "what should i do",
    "mental health", "dementia", "power of attorney",
    "bereavement", "suicide", "crisis",
    "pension", "inheritance", "redundancy",
]

FLAG_TRIGGERS = [
    "must", "legally required", "mandatory", "obligation",
    "breach", "deadline", "enforcement", "penalty",
    "maximum", "minimum", "limit",
]

def assess_hitl(question):
    q = question.lower()
    escalation = [t for t in ESCALATION_TRIGGERS if t in q]
    if escalation:
        return (HITLDecision.ESCALATE_TO_HUMAN,
                "High-stakes terms: " + ", ".join(escalation[:3]))
    flags = [t for t in FLAG_TRIGGERS if t in q]
    if flags:
        return (HITLDecision.ANSWER_WITH_FLAG,
                "Regulatory obligation language detected")
    return (HITLDecision.ANSWER_DIRECTLY,
            "Safe to answer directly")

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a Senior UK Compliance Officer.
Answer using ONLY the context provided.
Always cite source document and page number.
Use must/should/may exactly as the FCA uses them.
If the answer is not in the context say so explicitly.

CONTEXT:
{context}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
chain = rag_prompt | llm | StrOutputParser()

def get_answer(question, chat_history):
    docs = retriever.invoke(question)
    context = "\n\n".join(
        "[" + d.metadata.get("source_doc","Unknown") + " | Page " +
        str(d.metadata.get("page_display","?")) + "]\n" + d.page_content
        for d in docs
    )
    answer = chain.invoke({
        "context": context,
        "question": question,
        "chat_history": chat_history,
    })
    return answer, context

class HITLComplianceSystem:

    def __init__(self):
        self.chat_history = []
        self.review_queue = []
        self.question_count = 0
        self.escalated = 0
        self.flagged = 0
        self.direct = 0
        print("\n" + "="*65)
        print("FCA COMPLIANCE SYSTEM WITH HITL GATE v7.0")
        print("="*65)
        print("HITL Gate: Active")
        print("Documents: 4 FCA regulatory sources")
        print("="*65 + "\n")

    def ask(self, question):
        self.question_count += 1
        print("\n" + "="*65)
        print("Q" + str(self.question_count) + ": " + question)

        decision, reason = assess_hitl(question)
        print("HITL: " + decision.value + " | " + reason)

        if decision == HITLDecision.ESCALATE_TO_HUMAN:
            self.escalated += 1
            ref = "REF-" + str(self.question_count).zfill(4)
            self.review_queue.append({
                "id": self.question_count,
                "question": question,
                "reason": reason,
                "ref": ref,
                "status": "pending_human_review",
            })
            print("ESCALATED TO HUMAN REVIEW")
            print("Reference: " + ref)
            print("Reason: " + reason)
            print("Expected response: Within 2 business hours")
            return "ESCALATED - " + ref

        elif decision == HITLDecision.ANSWER_WITH_FLAG:
            self.flagged += 1
            answer, _ = get_answer(question, self.chat_history)
            self.chat_history.append(HumanMessage(content=question))
            self.chat_history.append(AIMessage(content=answer))
            print("\nA: " + answer)
            print("\nCOMPLIANCE NOTICE: Verify with your compliance team.")
            return answer

        else:
            self.direct += 1
            answer, _ = get_answer(question, self.chat_history)
            self.chat_history.append(HumanMessage(content=question))
            self.chat_history.append(AIMessage(content=answer))
            print("\nA: " + answer)
            return answer

    def show_summary(self):
        print("\n" + "="*65)
        print("HITL GATE SUMMARY")
        print("="*65)
        print("Total questions:    " + str(self.question_count))
        print("Answered directly:  " + str(self.direct))
        print("Answered with flag: " + str(self.flagged))
        print("Escalated to human: " + str(self.escalated))
        if self.review_queue:
            print("\nQuestions in human review queue:")
            for item in self.review_queue:
                print("  [" + item["ref"] + "] " + item["question"][:55] + "...")


def run_improved_evaluation():
    print("\n" + "="*65)
    print("RE-RUNNING EVALUATION WITH FIXES")
    print("="*65)

    evaluator = ChatOpenAI(model="gpt-4o", temperature=0)

    test_cases = [
        ("Q05", "What is the maximum FOS compensation award?"),
        ("Q08", "How long must firms keep complaint records?"),
        ("Q09", "What must firms consider when designing products for vulnerable customers?"),
        ("Q01", "What is the main purpose of the FCA Consumer Duty?"),
        ("Q04", "How quickly must a firm respond to a complaint?"),
    ]

    results = []
    passed = 0

    for qid, question in test_cases:
        answer, context = get_answer(question, [])

        prompt = (
            "Rate this answer 0.0-1.0. Return ONLY valid JSON with no extra text.\n"
            "Question: " + question + "\n"
            "Context: " + context[:1500] + "\n"
            "Answer: " + answer + "\n"
            '{"score": 0.0, "passed": false, "feedback": "brief feedback here"}\n'
            "Set passed to true if score >= 0.7"
        )

        raw = evaluator.invoke(prompt).content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        try:
            result = json.loads(raw)
        except Exception:
            result = {"score": 0.5, "passed": False, "feedback": "parse error"}

        score = result.get("score", 0)
        pass_check = result.get("passed", False)
        if pass_check:
            passed += 1

        status = "PASS" if pass_check else "FAIL"
        print("  " + status + " | " + qid + " | " +
              str(round(score, 2)) + " | " +
              result.get("feedback", "")[:55] + "...")
        results.append(score)

    avg = sum(results) / len(results)
    print("\nAverage score: " + str(round(avg, 2)) + "/1.0")
    print("Passed: " + str(passed) + "/" + str(len(test_cases)))

    if avg >= 0.8:
        print("TARGET ACHIEVED - Score above 0.80!")
    elif avg >= 0.7:
        print("IMPROVED - Above pass threshold")
    else:
        print("Still improving - more fixes may be needed")

    return avg


def run_demo():
    improved_score = run_improved_evaluation()

    system = HITLComplianceSystem()

    questions = [
        "What are the four outcomes of the Consumer Duty?",
        "What must a firm do within eight weeks of receiving a complaint?",
        "What are the four drivers of vulnerability according to FCA guidance?",
        "My bank has not responded to my complaint. Should I sue them?",
        "Am I entitled to compensation from my bank for mis-selling a pension?",
        "How does Consumer Duty interact with vulnerable customer requirements?",
        "What is the maximum FOS compensation award?",
    ]

    for q in questions:
        system.ask(q)

    system.show_summary()

    print("\n" + "="*65)
    print("Day 7 complete!")
    print("Improved eval score: " + str(round(improved_score, 2)) + "/1.0")
    print("HITL gate active - " + str(system.escalated) + " questions escalated")
    print("Flagged answers: " + str(system.flagged))
    print("Direct answers: " + str(system.direct))
    print("Check LangSmith: https://eu.smith.langchain.com")
    print("="*65)


if __name__ == "__main__":
    run_demo()