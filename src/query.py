import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chromadb
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Get API key — works both locally and on Streamlit Cloud
try:
    import streamlit as st
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
except:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

from config import DB_PATH, COLLECTION_NAME, TOP_K, GENERATION_MODEL

client_genai = genai.Client(api_key=GEMINI_API_KEY)

def get_query_embedding(text: str) -> list:
    response = client_genai.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return response.embeddings[0].values

def query_rag_pipeline(user_query: str, k: int = TOP_K) -> dict:
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)

    query_embedding = get_query_embedding(user_query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    context_blocks = []
    citations = []
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        source_name = meta['source']
        page_num = meta['page']
        citation_str = f"Source: {source_name}, Page: {page_num}"
        context_blocks.append(f"[{citation_str}]\nContext: {doc}")
        citations.append(citation_str)

    context_payload = "\n\n---\n\n".join(context_blocks)

    system_prompt = (
        "You are a professional, accurate document Q&A assistant. "
        "Answer the user's question using ONLY the provided document context below. "
        "Cite the sources (filenames and pages) inline next to facts you cite. "
        "If the answer cannot be found in the context, clearly state: "
        "'I am sorry, but the provided documents do not contain the answer to your question.' "
        "Do not make up facts or use external knowledge sources."
    )

    prompt = (
        f"{system_prompt}\n\n"
        f"CONTEXT INFORMATION:\n{context_payload}\n\n"
        f"USER QUESTION: {user_query}\n\n"
        f"GROUNDED ANSWER:"
    )

    response = client_genai.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt
    )

    return {
        "answer": response.text,
        "citations": citations,
        "raw_context": results['documents'][0]
    }