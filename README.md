# Tamil Nadu Class 6 English RAG System

This project implements a Retrieval-Augmented Generation (RAG) system using the Tamil Nadu State Board Class 6 English textbook. It uses **ChromaDB** for semantic search and **Neo4j** for structured knowledge graph retrieval.

## Prerequisites
1. **Python 3.8+**
2. **Neo4j Database**: A running instance (AuraDB or local).
3. **ChromaDB**: Cloud account or local setup (script uses Cloud Client).
4. **OpenAI API Key**: For embeddings and chat.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Open `.env` and fill in your details:
```ini
OPENAI_API_KEY=sk-...
CHROMADB_API_KEY=...
CHROMADB_TENANT=...
CHROMADB_DATABASE=...
NEO4J_URI=neo4j+s://...
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...
```

### 3. Prepare Data
Ensure `data/textbook.pdf` exists.
```bash
python download_textbook.py
```

### 4. Initialize Database
Sets up Neo4j constraints.
```bash
python setup_database.py
```

### 5. Ingest Data
Processes PDF, stores vectors in ChromaDB, and builds graph in Neo4j.
```bash
python ingest_data.py
```

## Running the Bot
### CLI Mode
```bash
python rag_bot.py
```

### Web UI (Streamlit)
To run the interactive web interface:
```bash
streamlit run app.py
```

## Verification
```bash
python test_rag.py
```
