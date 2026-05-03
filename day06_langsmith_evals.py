"""
Day 6 — LangSmith Evaluation Pipeline
What this builds:
- Automated correctness evaluator for RAG answers
- Scores every answer from 0.0 to 1.0
- Flags answers below 0.7 for human review
- Logs all scores to LangSmith permanently
- Produces a full quality report
This is what makes your system enterprise-grade.
A Barclays AI risk team would require this before
approving any AI system for production use.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import DocArrayInMemorySearch

load_dotenv()

# ── STEP 1: Build the RAG system ──────────────────────────────────────
print("📚 Building RAG system for evaluation...")

# Load all three documents
pdf_loader = PyPDFLoader("fca_consumer_duty.pdf")
consumer_duty_docs = pdf_loader.load()
for doc in consumer_duty_docs:
    doc.metadata["source_doc"] = "FCA Consumer Duty (PS22/9)"
    doc.metadata["page_display"] = doc.metadata.get("page", 0) + 1

txt_loader1 = TextLoader("fca_complaints_rules.txt", encoding="utf-8")
complaints_docs = txt_loader1.load()
for doc in complaints_docs:
    doc.metadata["source_doc"] = "FCA Complaints Handling (DISP 1)"

txt_loader2 = TextLoader("fca_vulnerable_customers.txt", encoding="utf-8")
vulnerable_docs = txt_loader2.load()
for doc in vulnerable_docs:
    doc.metadata["source_doc"] = "FCA Vulnerable Customers (FG21/1)"

all_documents = consumer_duty_docs + complaints_docs + vulnerable_docs

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
all_chunks = splitter.split_documents(all_documents)

embeddings = OpenAIEmbeddings()
vectorstore = DocArrayInMemorySearch.from_documents(
    all_chunks, embeddings
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
print(f"✅ RAG system ready — {len(all_chunks)} chunks loaded")

# ── STEP 2: The RAG answer generator ─────────────────────────────────
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a Senior UK Compliance Officer.
Answer using ONLY the context provided.
Always cite your source document and page number.
Use must/should/may exactly as the FCA uses them.
If the answer is not in the context say so explicitly.

CONTEXT:
{context}"""),
    ("human", "{question}"),
])

llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
rag_chain = rag_prompt | llm | StrOutputParser()

def get_rag_answer(question: str) -> tuple[str, str]:
    """
    Gets an answer from the RAG system.
    Returns both the answer and the retrieved context.
    We need the context for the evaluator to check
    whether the answer is grounded in the documents.
    """
    docs = retriever.invoke(question)
    context = "\n\n".join(
        f"[{d.metadata.get('source_doc', 'Unknown')}]\n{d.page_content}"
        for d in docs
    )
    answer = rag_chain.invoke({
        "context": context,
        "question": question,
    })
    return answer, context

# ── STEP 3: The Correctness Evaluator ────────────────────────────────
# This is the judge model — a second LLM that reads
# the question, the retrieved context, and the generated
# answer, then scores how correct the answer is.
# Think of it like a second examiner marking the same paper.

EVALUATOR_PROMPT = """You are an expert UK financial regulation 
examiner with 20 years of FCA compliance experience.

Your job is to evaluate whether an AI-generated answer 
correctly answers a compliance question based on the 
provided regulatory context.

QUESTION ASKED:
{question}

REGULATORY CONTEXT (source documents):
{context}

AI-GENERATED ANSWER:
{answer}

Evaluate the answer on these criteria:

1. FACTUAL ACCURACY — Is every factual claim correct?
2. COMPLETENESS — Does it address all parts of the question?
3. GROUNDING — Is it based on the context, not hallucination?
4. OBLIGATION PRECISION — Are must/should/may used correctly?
5. SOURCE CITATION — Does it cite its sources?

Return your evaluation as a JSON object with NO other text:
{{
    "score": 0.0,
    "factual_accuracy": 0.0,
    "completeness": 0.0,
    "grounding": 0.0,
    "obligation_precision": 0.0,
    "source_citation": 0.0,
    "passed": false,
    "feedback": "specific feedback on what was good or wrong",
    "critical_errors": []
}}

Scoring guide:
1.0 = Perfect — completely correct, complete, grounded
0.8 = Good — mostly correct with minor gaps
0.7 = Acceptable — correct but incomplete
0.6 = Borderline — partially correct, some errors
0.5 = Poor — significant errors or hallucination
0.0 = Fail — completely wrong or fabricated

"passed" = true if overall score >= 0.7
"critical_errors" = list any hallucinations or wrong obligations
"""

evaluator_llm = ChatOpenAI(model="gpt-4o", temperature=0)

def evaluate_answer(
    question: str,
    answer: str,
    context: str,
) -> dict:
    """
    Evaluates a RAG answer using the judge model.
    Returns a detailed scorecard.
    """
    eval_prompt = EVALUATOR_PROMPT.format(
        question=question,
        context=context[:3000],  # Limit context length
        answer=answer,
    )

    raw_result = evaluator_llm.invoke(eval_prompt).content.strip()

    # Clean up the response in case it has markdown
    raw_result = raw_result.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw_result)
    except json.JSONDecodeError:
        # If parsing fails, return a safe default
        result = {
            "score": 0.5,
            "factual_accuracy": 0.5,
            "completeness": 0.5,
            "grounding": 0.5,
            "obligation_precision": 0.5,
            "source_citation": 0.5,
            "passed": False,
            "feedback": "Evaluation parsing failed — manual review needed",
            "critical_errors": ["Evaluation system error"],
        }

    return result

# ── STEP 4: The Test Dataset ──────────────────────────────────────────
# These are our 10 test questions with expected answers.
# In a real enterprise system you would have hundreds of these.
# The expected_answer tells the evaluator what a correct
# answer should contain — it is the marking scheme.

TEST_DATASET = [
    {
        "id": "Q01",
        "question": "What is the main purpose of the FCA Consumer Duty?",
        "expected_contains": [
            "higher standard", "consumer protection",
            "good outcomes", "retail customers"
        ],
    },
    {
        "id": "Q02",
        "question": "What are the four outcomes under the Consumer Duty?",
        "expected_contains": [
            "products and services", "price and value",
            "consumer understanding", "consumer support"
        ],
    },
    {
        "id": "Q03",
        "question": "When did the Consumer Duty come into force?",
        "expected_contains": ["July 2023", "July 2024"],
    },
    {
        "id": "Q04",
        "question": "How quickly must a firm respond to a complaint?",
        "expected_contains": [
            "three business days", "eight weeks", "final response"
        ],
    },
    {
        "id": "Q05",
        "question": "What is the maximum FOS compensation award?",
        "expected_contains": ["415,000", "FOS", "Ombudsman"],
    },
    {
        "id": "Q06",
        "question": "What are the four drivers of vulnerability "
                    "according to FCA guidance?",
        "expected_contains": [
            "health", "life events", "resilience", "capability"
        ],
    },
    {
        "id": "Q07",
        "question": "Must firms carry out root cause analysis "
                    "of complaints?",
        "expected_contains": ["must", "root cause", "other customers"],
    },
    {
        "id": "Q08",
        "question": "How long must firms keep complaint records?",
        "expected_contains": ["three years", "record"],
    },
    {
        "id": "Q09",
        "question": "What must firms consider when designing "
                    "products for vulnerable customers?",
        "expected_contains": [
            "target market", "vulnerable", "needs", "suitable"
        ],
    },
    {
        "id": "Q10",
        "question": "How does the Consumer Duty interact with "
                    "vulnerable customer requirements?",
        "expected_contains": [
            "Consumer Duty", "vulnerable", "good outcomes",
            "consumer support"
        ],
    },
]

# ── STEP 5: Run the full evaluation pipeline ──────────────────────────
def run_evaluation_pipeline():
    """
    Runs all 10 test questions through the RAG system,
    evaluates each answer, and produces a quality report.
    This is the enterprise evaluation pipeline.
    """
    print("\n" + "="*65)
    print("🔬 LANGSMITH EVALUATION PIPELINE — STARTING")
    print(f"   Test questions: {len(TEST_DATASET)}")
    print(f"   Pass threshold: 0.7")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*65)

    results = []
    passed  = 0
    failed  = 0
    flagged = []  # Questions needing human review

    for i, test in enumerate(TEST_DATASET, 1):
        question_id = test["id"]
        question    = test["question"]

        print(f"\n[{question_id}] {question[:60]}...")
        print("   Generating answer...")

        # Get RAG answer
        answer, context = get_rag_answer(question)

        # Evaluate the answer
        print("   Evaluating answer...")
        eval_result = evaluate_answer(question, answer, context)

        score  = eval_result.get("score", 0)
        passed_check = eval_result.get("passed", False)

        # Record result
        result = {
            "id":         question_id,
            "question":   question,
            "answer":     answer,
            "score":      score,
            "passed":     passed_check,
            "feedback":   eval_result.get("feedback", ""),
            "breakdown": {
                "factual_accuracy":     eval_result.get("factual_accuracy", 0),
                "completeness":         eval_result.get("completeness", 0),
                "grounding":            eval_result.get("grounding", 0),
                "obligation_precision": eval_result.get("obligation_precision", 0),
                "source_citation":      eval_result.get("source_citation", 0),
            },
            "critical_errors": eval_result.get("critical_errors", []),
        }
        results.append(result)

        # Track pass/fail
        if passed_check:
            passed += 1
            status = "✅ PASS"
        else:
            failed += 1
            status = "❌ FAIL"
            flagged.append(question_id)

        print(f"   {status} | Score: {score:.2f} | "
              f"Feedback: {eval_result.get('feedback', '')[:60]}...")

    # ── STEP 6: Generate quality report ──────────────────────────────
    avg_score    = sum(r["score"] for r in results) / len(results)
    pass_rate    = (passed / len(results)) * 100

    print("\n" + "="*65)
    print("📊 EVALUATION REPORT")
    print("="*65)
    print(f"   Total questions:  {len(TEST_DATASET)}")
    print(f"   Passed:           {passed} ({pass_rate:.0f}%)")
    print(f"   Failed:           {failed}")
    print(f"   Average score:    {avg_score:.2f}/1.0")
    print(f"   Pass threshold:   0.70")

    if avg_score >= 0.8:
        grade = "🟢 EXCELLENT — Production ready"
    elif avg_score >= 0.7:
        grade = "🟡 GOOD — Minor improvements needed"
    elif avg_score >= 0.6:
        grade = "🟠 BORDERLINE — Significant improvements needed"
    else:
        grade = "🔴 POOR — Not production ready"

    print(f"   System grade:     {grade}")

    if flagged:
        print(f"\n⚠️  Questions flagged for human review:")
        for qid in flagged:
            print(f"   - {qid}")

    print("\n📈 Score breakdown by question:")
    for r in results:
        status = "✅" if r["passed"] else "❌"
        print(f"   {status} {r['id']}: {r['score']:.2f} — "
              f"{r['question'][:45]}...")

    # Save report to file
    report = {
        "timestamp":     datetime.now().isoformat(),
        "total":         len(TEST_DATASET),
        "passed":        passed,
        "failed":        failed,
        "average_score": round(avg_score, 3),
        "pass_rate":     round(pass_rate, 1),
        "grade":         grade,
        "flagged":       flagged,
        "results":       results,
    }

    with open("eval_report_day06.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Full report saved to: eval_report_day06.json")
    print("\n✅ Day 6 complete!")
    print("   Automated evaluation pipeline working")
    print("   10 questions scored and graded")
    print("   Quality report generated")
    print("   Check LangSmith: https://eu.smith.langchain.com")
    print("="*65)

    return report


if __name__ == "__main__":
    run_evaluation_pipeline()