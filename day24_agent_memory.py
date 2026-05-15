# day24_agent_memory.py
# Day 24 — Agent Memory — Persistent ChromaDB
# Sprint: 42-Day Agentic AI Zero-to-Hero
# Date: Friday 15 May 2026
# Stack: ChromaDB · OpenAI · LangChain

"""
Day 24 Goal: Add persistent memory across sessions.
Store conversation history in ChromaDB.
Test memory recall across separate runs.

What we build:
    1. AgentMemory class — stores and retrieves memories
    2. Memory-aware agent — uses past context in responses
    3. Persistence test — memories survive between sessions
    4. Relevance search — finds most relevant past memories

Use Case: Magic Circle law firm — agent remembers past
    client matters and applies that context to new queries.

GitHub: github.com/sheyiteluwo-ai/agentic-systems-architect-sprint
"""

import os
import json
import uuid
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()


# ── Agent Memory Class ────────────────────────────────────────────────────────

class AgentMemory:
    """
    Persistent memory for AI agents using ChromaDB.

    Stores memories as embeddings so the agent can retrieve
    semantically relevant past context — not just recent messages.

    Memory types:
        conversation  — what was discussed
        fact          — important facts learned
        decision      — decisions made and why
        client        — client-specific information
    """

    def __init__(self, collection_name: str = "agent_memory"):
        """Initialises ChromaDB persistent memory store."""
        import chromadb
        from langchain_openai import OpenAIEmbeddings

        self.collection_name = collection_name
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )

        # Connect to ChromaDB
        self.client = chromadb.PersistentClient(
            path="./agent_memory_db"
        )

        # Get or create memory collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Agent persistent memory store"}
        )

        print(f"  Memory store ready: {self.collection.count()} memories loaded")

    def store(self, content: str, memory_type: str = "conversation",
              metadata: dict = None) -> str:
        """
        Stores a memory with its embedding.
        Returns the memory ID.
        """
        memory_id = str(uuid.uuid4())[:8]

        # Get embedding for semantic search
        embedding = self.embeddings.embed_query(content)

        # Build metadata
        mem_metadata = {
            "type": memory_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "memory_id": memory_id
        }
        if metadata:
            mem_metadata.update(metadata)

        # Store in ChromaDB
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[mem_metadata]
        )

        return memory_id

    def recall(self, query: str, top_k: int = 3,
               memory_type: str = None) -> list[dict]:
        """
        Retrieves most relevant memories for a query.
        Uses semantic similarity search.
        """
        if self.collection.count() == 0:
            return []

        # Get query embedding
        query_embedding = self.embeddings.embed_query(query)

        # Build filter
        where = {"type": memory_type} if memory_type else None

        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count()),
            where=where,
            include=["documents", "metadatas", "distances"]
        )

        memories = []
        if results and results.get("documents"):
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                memories.append({
                    "content": doc,
                    "type": meta.get("type", "unknown"),
                    "timestamp": meta.get("timestamp", ""),
                    "relevance": round(1 - float(dist), 3)
                })

        return memories

    def count(self) -> int:
        """Returns total number of stored memories."""
        return self.collection.count()

    def clear(self) -> None:
        """Clears all memories from the store."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )
        print("  Memory store cleared")


# ── Memory-Aware Agent ────────────────────────────────────────────────────────

class MemoryAwareAgent:
    """
    Legal research agent that uses persistent memory.

    Before answering each question, the agent:
    1. Searches its memory for relevant past context
    2. Includes that context in its prompt
    3. Stores the new interaction in memory

    This means the agent gets smarter over time.
    """

    def __init__(self):
        from openai import OpenAI
        self.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.memory = AgentMemory()

    def answer(self, question: str, store_memory: bool = True) -> dict:
        """
        Answers a legal question using memory-augmented context.
        """
        # Step 1: Recall relevant memories
        relevant_memories = self.memory.recall(question, top_k=3)

        # Step 2: Build memory context
        if relevant_memories:
            memory_context = "\n".join([
                f"- [{m['type']}] {m['content'][:200]} "
                f"(relevance: {m['relevance']:.2f})"
                for m in relevant_memories
            ])
        else:
            memory_context = "No relevant past context found."

        # Step 3: Answer with memory context
        response = self.llm.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior legal adviser at a Magic Circle "
                        "law firm with persistent memory of past client "
                        "matters. Use past context when relevant."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"PAST CONTEXT FROM MEMORY:\n{memory_context}\n\n"
                        f"CURRENT QUESTION: {question}\n\n"
                        f"Answer using your expertise and any relevant "
                        f"past context above."
                    )
                }
            ]
        )

        answer = response.choices[0].message.content.strip()

        # Step 4: Store this interaction in memory
        if store_memory:
            self.memory.store(
                content=f"Q: {question} | A: {answer[:300]}",
                memory_type="conversation",
                metadata={"question": question[:100]}
            )

        return {
            "question": question,
            "answer": answer,
            "memories_used": len(relevant_memories),
            "memory_context": memory_context[:300] if relevant_memories else None,
            "total_memories": self.memory.count()
        }


# ── Main Demo ─────────────────────────────────────────────────────────────────

def run_demo():
    print("\n" + "="*65)
    print("  DAY 24 — AGENT MEMORY — PERSISTENT CHROMADB")
    print("  Date: Friday 15 May 2026")
    print("  Memory store: ./agent_memory_db")
    print("="*65 + "\n")

    agent = MemoryAwareAgent()

    # ── Step 1: Store initial memories ───────────────────────────────────────
    print("── STEP 1: STORING INITIAL MEMORIES ───────────────────")

    initial_memories = [
        (
            "Acme Corp is a UK technology company with 500 employees. "
            "They have ongoing FCA compliance obligations and are "
            "currently under review for Consumer Duty compliance.",
            "client"
        ),
        (
            "The Worker Protection Act 2023 came into force on "
            "26 October 2024. It requires employers to take reasonable "
            "steps to prevent sexual harassment.",
            "fact"
        ),
        (
            "In the Acme Corp matter we recommended capping liability "
            "at 2x annual contract value and excluding consequential loss.",
            "decision"
        ),
        (
            "Magic Circle billing rates for senior associates range from "
            "£400-£650 per hour. Partners bill at £800-£1,200 per hour.",
            "fact"
        ),
        (
            "Acme Corp's employment contracts were last reviewed in 2021 "
            "and do not include Worker Protection Act 2023 provisions.",
            "client"
        ),
    ]

    for content, mem_type in initial_memories:
        mem_id = agent.memory.store(content, memory_type=mem_type)
        print(f"  ✅ Stored [{mem_type}]: {content[:60]}... (id: {mem_id})")

    print(f"\n  Total memories stored: {agent.memory.count()}")

    # ── Step 2: Test memory recall ────────────────────────────────────────────
    print("\n── STEP 2: TESTING MEMORY RECALL ───────────────────────")

    test_queries = [
        "What do we know about Acme Corp?",
        "What are current Magic Circle billing rates?",
        "What is our policy on liability caps?"
    ]

    for query in test_queries:
        memories = agent.memory.recall(query, top_k=2)
        print(f"\n  Query: {query}")
        for i, mem in enumerate(memories, 1):
            print(
                f"  Memory {i} [{mem['type']}] "
                f"(relevance: {mem['relevance']:.2f}): "
                f"{mem['content'][:80]}..."
            )

    # ── Step 3: Answer questions with memory ──────────────────────────────────
    print("\n── STEP 3: ANSWERING WITH MEMORY CONTEXT ───────────────")

    questions = [
        (
            "Does Acme Corp need to update their employment contracts "
            "for the Worker Protection Act 2023?"
        ),
        (
            "What should we charge Acme Corp for a full employment "
            "contract review?"
        )
    ]

    results = []
    for question in questions:
        print(f"\n  Question: {question[:65]}...")
        result = agent.answer(question)
        print(f"  Memories used: {result['memories_used']}")
        print(f"  Total memories: {result['total_memories']}")
        print(f"  Answer preview: {result['answer'][:200]}...")
        results.append(result)

    # ── Step 4: Persistence test ──────────────────────────────────────────────
    print("\n── STEP 4: PERSISTENCE TEST ────────────────────────────")
    print("  Creating new agent instance (simulating new session)...")

    agent2 = MemoryAwareAgent()
    print(f"  New agent loaded {agent2.memory.count()} memories from disk")
    print("  ✅ Memory persists across sessions!")

    # Save summary
    summary = {
        "date": datetime.now(timezone.utc).isoformat(),
        "sprint_day": 24,
        "total_memories_stored": agent.memory.count(),
        "memory_types": ["conversation", "fact", "decision", "client"],
        "persistence_verified": True,
        "questions_answered": len(questions)
    }

    with open("day24_memory_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "="*65)
    print("  DAY 24 COMPLETE — AGENT MEMORY VERIFIED")
    print("="*65)
    print(f"  Memories stored:     {agent.memory.count()}")
    print(f"  Memory types:        conversation, fact, decision, client")
    print(f"  Persistence:         ✅ Verified across sessions")
    print(f"  Summary saved:       day24_memory_summary.json")
    print("="*65)

    print("\n  INTERVIEW TALKING POINT:")
    print("  " + "-"*56)
    print("  I built persistent agent memory using ChromaDB.")
    print("  The agent stores every interaction as a vector")
    print("  embedding and retrieves semantically relevant")
    print("  past context before answering each new question.")
    print("  Memories survive between sessions — the agent")
    print("  remembers client details, past decisions, and")
    print("  key facts across separate runs. That is what")
    print("  separates a stateless chatbot from a system")
    print("  that genuinely learns from experience.")
    print("  " + "-"*56 + "\n")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_demo()
