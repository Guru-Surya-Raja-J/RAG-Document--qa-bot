# 📄 Document Q&A Bot

A RAG (Retrieval-Augmented Generation) based chatbot that answers questions from your own PDF and DOCX files using Google Gemini AI, ChromaDB vector search, and a Streamlit chat UI.

---

## 🧠 How It Works

1. Your documents are split into chunks and converted into vector embeddings
2. When you ask a question, the most relevant chunks are retrieved from the database
3. Those chunks are passed to Gemini AI to generate a grounded answer with citations

---

## 🛠️ Tech Stack

- **Google Gemini AI** — Embeddings (`gemini-embedding-001`) + Text Generation (`gemini-2.5-flash-lite`)
- **ChromaDB** — Local vector database for semantic search
- **Streamlit** — Chat UI
- **pypdf + python-docx** — Document parsing

---

## 📁 Project Structure
document-qa-bot/

├── .env                  # Your Gemini API key (never push this)

├── requirements.txt      # All dependencies

├── data/                 # Put your PDF and DOCX files here

├── db/                   # Auto-generated vector database (never push this)

└── src/

├── config.py         # App settings and constants

├── ingest.py         # Reads, chunks, embeds and indexes documents

├── query.py          # Handles search and answer generation

└── main.py           # Streamlit chat UI

---

## ⚙️ Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/document-qa-bot.git
cd document-qa-bot
```

### 2. Create and activate virtual environment
```bash
py -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API key
Create a `.env` file in the root folder:
GEMINI_API_KEY=your_api_key_here
Get your free API key at: https://aistudio.google.com/app/apikey

### 5. Add your documents
Drop your PDF or DOCX files into the `data/` folder.

### 6. Index your documents
```bash
python -m src.ingest
```

### 7. Run the app
```bash
streamlit run src/main.py
```

Open your browser at `http://localhost:8501`

---

## 🔁 Running the Project Again Later

```bash
venv\Scripts\activate
streamlit run src/main.py
```

Only re-run `python -m src.ingest` if you add new documents to the `data/` folder.

---

## 📌 Notes

- Answers are grounded strictly in your documents — the AI will not make things up
- Each answer includes citations showing which file and page the answer came from
- Supports PDF and DOCX files