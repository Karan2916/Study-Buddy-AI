# rag_core.py

import os
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

# --- SETUP ---
# Load environment variables from .env file
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Initialize the Google embeddings model
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
vector_store_path = "faiss_index"


# --- FUNCTIONS ---
def create_vector_store(pdf_files):
    """
    Processes uploaded PDF files, chunks them with page number metadata,
    and creates or updates a FAISS vector store.
    """
    all_docs = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    # Process each PDF file
    for pdf_file in pdf_files:
        try:
            pdf_reader = PdfReader(pdf_file)
            file_name = getattr(pdf_file, 'name', 'unknown_file')
            print(f"Processing file: {file_name}...")
            
            # Process each page in the PDF
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    # Split the text from a single page into smaller chunks
                    chunks = text_splitter.split_text(page_text)
                    for chunk in chunks:
                        # Create a Document object for each chunk with metadata
                        doc = Document(
                            page_content=chunk,
                            metadata={"page": i + 1, "source": file_name} # Added source file name
                        )
                        all_docs.append(doc)
        except Exception as e:
            print(f"Error processing a PDF file: {e}")

    if not all_docs:
        print("No text could be extracted from the provided PDFs.")
        return

    # Create or update the FAISS vector store
    if os.path.exists(vector_store_path) and os.listdir(vector_store_path):
        print("Existing vector store found. Adding new documents...")
        vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        vector_store.add_documents(all_docs)
    else:
        print("No existing vector store found. Creating a new one...")
        vector_store = FAISS.from_documents(all_docs, embedding=embeddings)

    vector_store.save_local(vector_store_path)
    print(f"Vector store created/updated successfully with {len(all_docs)} chunks!")

def get_retriever():
    """
    Loads the FAISS vector store from the local path and returns a retriever object.
    The retriever is configured to fetch the top 'k' most relevant documents.
    """
    if not os.path.exists(vector_store_path):
        return None
        
    vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
    
    # UPDATED: Retrieve the top 6 relevant chunks to provide more context.
    # You can experiment with this 'k' value to tune performance.
    return vector_store.as_retriever(search_kwargs={'k': 6})