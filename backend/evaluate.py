# evaluate.py
import os
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
from datasets import Dataset
from rag_core import get_retriever
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Your RAG Generation Model
generation_model = genai.GenerativeModel(model_name='gemini-1.5-pro-latest')

# --- Your RAG Pipeline Logic (simplified for evaluation) ---
def get_rag_response(question):
    """Gets a response from your RAG pipeline."""
    retriever = get_retriever()
    if not retriever:
        raise ValueError("Vector store not found. Make sure you have indexed documents.")
    
    retrieved_docs = retriever.invoke(question)
    context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # --- ADD THIS DEBUGGING CODE ---
    print("="*50)
    print(f"QUESTION: {question}")
    print(f"RETRIEVED CONTEXT:\n{context}")
    print("="*50)
    # -----------------------------

    prompt = f"""Using ONLY the following context, answer the question.
    
    Context:
    {context}
    
    Question: {question}
    """
    
    response = generation_model.generate_content(prompt)
    
    return {
        "answer": response.text,
        "contexts": [doc.page_content for doc in retrieved_docs]
    }

# --- Evaluation Dataset ---
# NOTE: You MUST create your own questions and ground-truth answers based on your documents.
eval_data = {
    'question': [
        "What is a language according to Automata Theory?",
        "What is an application of DFA mentioned in the text?"
    ],
    'ground_truth': [
        "A language is a collection of sentences of finite length all constructed from a finite alphabet of symbols.",
        "An application of DFA is text search for keywords."
    ]
}
eval_dataset = Dataset.from_dict(eval_data)

# --- Run the RAG Pipeline and Generate Responses ---
results = []
for entry in eval_dataset:
    question = entry['question']
    response_data = get_rag_response(question)
    results.append({
        "question": question,
        "answer": response_data["answer"],
        "contexts": response_data["contexts"],
        "ground_truth": entry["ground_truth"]
    })

# Convert results to a Ragas-compatible dataset
results_dataset = Dataset.from_list(results)

# --- Evaluate the Results ---
ragas_llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
ragas_embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# --- Evaluate the Results ---
score = evaluate(
    results_dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_recall,
        context_precision,
    ],
    llm=ragas_llm,
    embeddings=ragas_embeddings,
)

print(score)