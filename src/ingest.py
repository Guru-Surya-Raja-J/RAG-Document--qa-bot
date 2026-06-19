import os
import chromadb
from google import genai
from google.genai import types
from pypdf import PdfReader
from docx import Document
from tqdm import tqdm
from src.config import GEMINI_API_KEY, DB_PATH, DATA_PATH, COLLECTION_NAME, CHUNK_SIZE, CHUNK_OVERLAP

client_genai = genai.Client(api_key=GEMINI_API_KEY)

def extract_pdf_pages(file_path: str) -> list:
    extracted_data = []
    file_name = os.path.basename(file_path)
    try:
        reader = PdfReader(file_path)
        for index, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                clean_text = " ".join(text.split())
                extracted_data.append({
                    "text": clean_text,
                    "metadata": {"source": file_name, "page": index + 1}
                })
    except Exception as e:
        print(f"Error reading PDF {file_name}: {e}")
    return extracted_data

def extract_docx_pages(file_path: str) -> list:
    extracted_data = []
    file_name = os.path.basename(file_path)
    try:
        doc = Document(file_path)
        full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        clean_text = " ".join(full_text.split())
        if clean_text:
            extracted_data.append({
                "text": clean_text,
                "metadata": {"source": file_name, "page": 1}
            })
    except Exception as e:
        print(f"Error reading DOCX {file_name}: {e}")
    return extracted_data

def chunk_extracted_pages(pages: list, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> list:
    chunks = []
    for page in pages:
        text = page["text"]
        metadata = page["metadata"]
        start = 0
        text_length = len(text)
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk_text = text[start:end]
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": metadata["source"],
                    "page": metadata["page"],
                    "chunk_range": f"{start}-{end}"
                }
            })
            start += (chunk_size - chunk_overlap)
    return chunks

def get_embeddings(texts: list) -> list:
    embeddings = []
    for text in tqdm(texts, desc="Generating embeddings"):
        response = client_genai.models.embed_content(
           model="gemini-embedding-001",
            contents=text
        )
        embeddings.append(response.embeddings[0].values)
    return embeddings

def save_to_vector_db(chunks: list, db_path: str = DB_PATH):
    client = chromadb.PersistentClient(path=db_path)

    # Delete existing collection to avoid duplicate id errors
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    texts = [chunk["text"] for chunk in chunks]
    embeddings = get_embeddings(texts)

    ids = [f"id_{i}" for i in range(len(chunks))]
    metadatas = [chunk["metadata"] for chunk in chunks]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )
    print(f"Successfully indexed {len(chunks)} chunks in the vector database.")

def run_ingestion():
    all_pages = []
    files = os.listdir(DATA_PATH)
    print(f"Found {len(files)} files in {DATA_PATH}")
    for file_name in tqdm(files, desc="Processing files"):
        file_path = os.path.join(DATA_PATH, file_name)
        if file_name.endswith(".pdf"):
            all_pages.extend(extract_pdf_pages(file_path))
        elif file_name.endswith(".docx"):
            all_pages.extend(extract_docx_pages(file_path))
        else:
            print(f"Skipping unsupported file: {file_name}")
    print(f"Extracted {len(all_pages)} pages total.")
    chunks = chunk_extracted_pages(all_pages)
    print(f"Created {len(chunks)} chunks total.")
    save_to_vector_db(chunks)

if __name__ == "__main__":
    run_ingestion()