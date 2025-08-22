# main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
from agent import run_conversation
from rag_core import create_vector_store

app = FastAPI()

# Allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Endpoint to upload PDF files and create the vector store."""
    file_paths = [file.file for file in files]
    create_vector_store(file_paths)
    return {"message": f"Successfully indexed {len(files)} documents."}

@app.post("/chat/")
async def chat_with_agent(prompt: dict):
    """Endpoint to handle chat messages with the agent."""
    user_prompt = prompt.get("prompt")
    if not user_prompt:
        return {"error": "Prompt not provided."}
    
    agent_response = run_conversation(user_prompt)
    return {"response": agent_response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)