# agent.py
import os
import requests
import google.generativeai as genai
from rag_core import get_retriever
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from urllib.parse import urlparse, parse_qs

# Configure the Gemini model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- CORRECTED MODEL DEFINITION ---
# Combine instructions, tools, and safety settings into ONE agent model.
# ------------------------------------

# 1. Define the RAG Retriever Tool
def course_material_retriever(query: str) -> dict:
    """Searches and retrieves relevant context with page numbers from course materials."""
    retriever = get_retriever()
    if not retriever:
        return {"context": "Error: Vector store not found. Please upload documents first."}
    
    relevant_docs = retriever.invoke(query)
    
    context_parts = []
    for doc in relevant_docs:
        page_num = doc.metadata.get('page', 'N/A')
        context_parts.append(f"Source (Page {page_num}):\n{doc.page_content}")
    
    context = "\n\n---\n\n".join(context_parts)
    return {"context": context}

# 2. Define the YouTube Search Tool
def youtube_search(topic: str) -> dict:
    """Searches YouTube for a relevant video and returns its title, link, and thumbnail."""
    search_api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    url = f"https://www.googleapis.com/customsearch/v1?key={search_api_key}&cx={search_engine_id}&q={topic} youtube video tutorial"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json()
        if "items" in results and len(results["items"]) > 0:
            first_result = results["items"][0]
            video_url = first_result.get("link")
            
            video_id = None
            if "watch?v=" in video_url:
                parsed_url = urlparse(video_url)
                video_id = parse_qs(parsed_url.query).get("v", [None])[0]
            
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id else None

            return {
                "title": first_result.get("title"),
                "link": video_url,
                "thumbnail": thumbnail_url
            }
        else:
            return {"link": "No relevant YouTube video found."}
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}
    
agent = genai.GenerativeModel(
    model_name='gemini-1.5-pro-latest',
    tools=[course_material_retriever, youtube_search],
    system_instruction="""You are 'StudyBuddy', a helpful AI assistant for BMSCE students.
    Your goal is to answer questions based on the user's uploaded course materials.
    1. First, ALWAYS use the 'course_material_retriever' tool to find relevant context from the documents.
    2. Formulate your answer based *only* on the retrieved context.
    3. You MUST cite the page number for the information you use. Your citations should look like this: (Source: Page 5).
    4. If the user asks for a general summary, use the tool with a query like "introduction and key concepts" to find relevant sections and then summarize them.
    5. After answering, use the 'youtube_search' tool to find a relevant educational video on the topic.
    6. CRITICAL INSTRUCTION: For YouTube videos, you MUST ONLY use this exact markdown format and nothing else: [![video title](thumbnail url)](video url)
    If the documents do not contain an answer, state that clearly and do not attempt to answer from your own knowledge.
    """,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }
)

# Start a chat session using the single, correct agent
chat = agent.start_chat(enable_automatic_function_calling=True)

def run_conversation(user_prompt):
    """Sends a prompt to the agent and gets the response."""
    response = chat.send_message(user_prompt)
    return response.text