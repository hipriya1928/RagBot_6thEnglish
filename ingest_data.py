import os
import json
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
from neo4j import GraphDatabase

load_dotenv()

# Configuration
PDF_PATH = os.path.join("data", "textbook.pdf")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ChromaDB Config
CHROMA_API_KEY = os.getenv("CHROMADB_API_KEY")
CHROMA_TENANT = os.getenv("CHROMADB_TENANT")
CHROMA_DATABASE = os.getenv("CHROMADB_DATABASE")

# Neo4j Config
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Define Output Structures for Graph Extraction
class GraphEdge(BaseModel):
    source: str = Field(description="The source node name")
    target: str = Field(description="The target node name")
    relationship: str = Field(description="The type of relationship (e.g., 'is_a', 'part_of', 'knows')")

class GraphNode(BaseModel):
    name: str = Field(description="The unique name of the entity")
    type: str = Field(description="The type of entity (e.g., 'Character', 'Concept', 'Location')")

class GraphExtraction(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

def ingest_data():
    if not os.path.exists(PDF_PATH):
        print(f"Error: {PDF_PATH} not found.")
        return
    
    print("Loading PDF...")
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()
    
    # Split text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    print(f"Split into {len(splits)} chunks.")

    # 1. Vector Store Ingestion (ChromaDB)
    print("Ingesting into ChromaDB...")
    try:
        # Initialize Chroma Client
        client = chromadb.CloudClient(
            api_key=CHROMA_API_KEY,
            tenant=CHROMA_TENANT,
            database=CHROMA_DATABASE
        )
        
        # Get or Create Collection
        collection = client.get_or_create_collection(name="textbook_rag")
        
        # Prepare data for Chroma
        ids = [f"chunk_{i}" for i in range(len(splits))]
        documents = [s.page_content for s in splits]
        metadatas = [s.metadata for s in splits]
        
        # Generate Embeddings manually or let Chroma do it? 
        # Chroma Cloud usually requires embeddings or an embedding function.
        # We will use OpenAI Embeddings via LangChain wrapper to generate them, 
        # OR pass the embedding function to Chroma.
        # Let's generate them to be safe and explicit.
        embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
        embeddings = embeddings_model.embed_documents(documents)
        
        # Add to collection (batching is better for large datasets, but this is small)
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end = min(i + batch_size, len(documents))
            collection.add(
                ids=ids[i:end],
                documents=documents[i:end],
                embeddings=embeddings[i:end],
                metadatas=metadatas[i:end]
            )
        print("ChromaDB ingestion complete.")
        
    except Exception as e:
        print(f"ChromaDB ingestion failed: {e}")
        return

    # 2. Knowledge Graph Ingestion (Neo4j)
    print("Ingesting into Neo4j...")
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    parser = JsonOutputParser(pydantic_object=GraphExtraction)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert at extracting knowledge graphs. Extract key entities and relationships."),
        ("user", "Extract knowledge graph from this text:\n{text}\n\n{format_instructions}")
    ])
    graph_chain = prompt | llm | parser

    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        
        with driver.session() as session:
            for i, split in enumerate(splits):
                # Process every 5th chunk for demo speed/cost
                if i % 5 == 0:
                    try:
                        print(f"Extracting graph from chunk {i}...")
                        content = split.page_content
                        graph_data = graph_chain.invoke({"text": content, "format_instructions": parser.get_format_instructions()})
                        
                        # Cypher query to merge nodes and relationships
                        cypher_query = """
                        UNWIND $nodes AS node
                        MERGE (n:Entity {name: node.name})
                        SET n.type = node.type
                        
                        WITH 1 as dummy
                        UNWIND $edges AS edge
                        MERGE (a:Entity {name: edge.source})
                        MERGE (b:Entity {name: edge.target})
                        MERGE (a)-[r:RELATED {type: edge.relationship}]->(b)
                        """
                        
                        session.run(cypher_query, 
                                    nodes=graph_data.get('nodes', []),
                                    edges=graph_data.get('edges', [])
                        )
                    except Exception as e:
                        print(f"Error processing chunk {i} for graph: {e}")
                        
        driver.close()
        print("Neo4j ingestion complete.")
        
    except Exception as e:
        print(f"Neo4j connection failed: {e}")

if __name__ == "__main__":
    ingest_data()
