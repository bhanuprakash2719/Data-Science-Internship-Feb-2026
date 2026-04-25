import os
from typing import TypedDict
from langgraph.graph import StateGraph, END

# --- IMPORT CUSTOM MODULES [cite: 34, 35, 37, 41] ---
from src.loader import load_and_split_pdf
from src.rag_pipeline import build_vectorstore
from src.llm import call_llm

# --- 1. INITIALIZATION (Runs Once) [cite: 15, 144] ---
print("Initializing Knowledge Base and Embedding System...")
# Use the mandatory PDF source [cite: 7, 20]
PDF_PATH = os.path.join("data", "Sample_car.pdf")

if not os.path.exists(PDF_PATH):
    print(f"Error: Could not find {PDF_PATH}. Please ensure your PDF is in the data folder.")
    exit()

# Load, Chunk, and Store [cite: 15, 62, 107]
CHUNKS = load_and_split_pdf(PDF_PATH) 
VECTORSTORE = build_vectorstore(CHUNKS) # Stores embeddings in ChromaDB [cite: 15, 30]

# --- 2. STATE DEFINITION [cite: 73, 76] ---
class AgentState(TypedDict):
    query: str
    context: str
    answer: str
    needs_escalation: bool

# --- 3. GRAPH NODES (Functional Components) [cite: 60, 114] ---

def retrieve_node(state: AgentState):
    """Retrieves relevant chunks from ChromaDB[cite: 31, 39, 64]."""
    # Find top 2 relevant segments [cite: 8]
    docs = VECTORSTORE.similarity_search(state['query'], k=2)
    context = "\n".join([d.page_content for d in docs])
    return {"context": context}

def generate_node(state: AgentState):
    """Processes query using LLM and determines if escalation is needed[cite: 10, 42, 65]."""
    # Check if context is missing [cite: 80, 92]
    if not state.get('context') or len(state['context']) < 10:
        return {"answer": "Information not found in internal docs.", "needs_escalation": True}
    
    prompt = f"Context: {state['context']}\n\nQuestion: {state['query']}\nAnswer:"
    answer = call_llm(prompt) # LLM processing layer [cite: 32, 50]
    
    # Escalation criteria: Low confidence or short answer [cite: 78, 79, 118]
    is_uncertain = len(answer) < 50 or "i don't know" in answer.lower()
    return {"answer": answer, "needs_escalation": is_uncertain}

def escalate_node(state: AgentState):
    """Human-in-the-Loop escalation module[cite: 11, 21, 43, 67, 119]."""
    print(f"\n--- [!] ESCALATION TRIGGERED for query: '{state['query']}' ---")
    human_input = input("Manual response required (Human Agent): ")
    return {"answer": human_input, "needs_escalation": False}

# --- 4. WORKFLOW ORCHESTRATION (LangGraph) [cite: 17, 41, 113] ---
workflow = StateGraph(AgentState)

# Add Nodes [cite: 75]
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)
workflow.add_node("escalate", escalate_node)

# Set Flow [cite: 75, 115]
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")

# Conditional Routing [cite: 19, 77, 116, 118]
workflow.add_conditional_edges(
    "generate",
    lambda x: "escalate" if x["needs_escalation"] else END
)
workflow.add_edge("escalate", END)

# Compile the Graph Execution Module [cite: 66]
app = workflow.compile()

# --- 5. INTERFACE LAYER (CLI) [cite: 29, 85] ---
def main():
    print("\n" + "="*50)
    print("  RAG-BASED CUSTOMER SUPPORT ASSISTANT (HITL)  ")
    print("="*50)
    
    while True:
        user_query = input("\nAsk a Question (or) Exit: ").strip()
        if user_query.lower() in ["exit", "quit"]:
            break
        if not user_query:
            continue

        # Initial Query Life-cycle state [cite: 46, 72]
        initial_state = {
            "query": user_query,
            "context": "",
            "answer": "",
            "needs_escalation": False
        }

        try:
            # Execute the graph workflow [cite: 87]
            final_output = app.invoke(initial_state)
            print(f"\nAnswer: {final_output['answer']}")
        except Exception as e:
            print(f"\n[Error]: {e}") # Basic error handling [cite: 88, 93]

if __name__ == "__main__":
    main()
