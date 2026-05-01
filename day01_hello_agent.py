import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

def run_hello_agent(query: str) -> str:
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.2,
        max_tokens=512,
        metadata={"phase": "1", "day": "1", "domain": "uk_finance"}
    )
    messages = [
        SystemMessage(content=(
            "You are a helpful AI assistant specialising in UK financial "
            "services regulation. Give concise, accurate answers. "
            "Never fabricate regulatory references."
        )),
        HumanMessage(content=query),
    ]
    response = llm.invoke(messages)
    return response.content

if __name__ == "__main__":
    queries = [
        "What is the FCA Consumer Duty and when did it come into force?",
        "Explain MiFID II in one sentence for a UK retail investor.",
        "What does SMCR stand for and why does it matter?",
    ]
    for i, q in enumerate(queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"Q: {q}")
        answer = run_hello_agent(q)
        print(f"A: {answer}")
    print("\nDone! Check LangSmith at https://smith.langchain.com")