import os
import chromadb
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from neo4j import GraphDatabase

load_dotenv()

class RAGBot:
    def __init__(self):
        # ChromaDB Config
        self.chroma_client = chromadb.CloudClient(
            api_key=os.getenv("CHROMADB_API_KEY"),
            tenant=os.getenv("CHROMADB_TENANT"),
            database=os.getenv("CHROMADB_DATABASE")
        )
        self.collection = self.chroma_client.get_collection(name="textbook_rag")
        
        # Neo4j Config
        self.neo4j_driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"), 
            auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
        )
        
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.memory = ConversationBufferMemory(return_messages=True)

    def vector_search(self, query, k=3):
        """Retrieves relevant text chunks using ChromaDB."""
        try:
            query_embedding = self.embeddings.embed_query(query)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k
            )
            # Chroma returns list of lists
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            print(f"Vector search failed: {e}")
            return []

    def graph_search(self, query):
        """Retrieves relevant graph triples based on entities in the query."""
        # 1. Extract entities from query
        extraction_prompt = ChatPromptTemplate.from_template(
            "Extract the main entities (nouns, proper nouns) from this query as a comma-separated list: {query}"
        )
        chain = extraction_prompt | self.llm
        entities_str = chain.invoke({"query": query}).content
        entities = [e.strip() for e in entities_str.split(',')]
        
        triples = []
        try:
            with self.neo4j_driver.session() as session:
                for entity in entities:
                    # Cypher query to find related nodes
                    cypher = """
                    MATCH (a:Entity)-[r:RELATED]->(b:Entity)
                    WHERE a.name CONTAINS $entity OR b.name CONTAINS $entity
                    RETURN a.name, r.type, b.name
                    LIMIT 5
                    """
                    result = session.run(cypher, entity=entity)
                    for record in result:
                        triples.append(f"{record['a.name']} --[{record['r.type']}]--> {record['b.name']}")
        except Exception as e:
            print(f"Graph search failed: {e}")
            
        return list(set(triples))

    def generate_response(self, query):
        # 1. Retrieve Context
        vector_docs = self.vector_search(query)
        graph_data = self.graph_search(query)
        
        context_text = "\n\n".join(vector_docs)
        context_graph = "\n".join(graph_data)
        
        full_context = f"### TEXT SOURCES:\n{context_text}\n\n### KNOWLEDGE GRAPH:\n{context_graph}"
        
        # 2. Prepare Prompt
        system_prompt = """You are a helpful educational assistant for Class 6 English.
        Answer the user's question using ONLY the provided context. 
        If the answer is not in the context, say "I cannot find the answer in the textbook."
        
        Combine information from both the text sources and the knowledge graph to provide a complete answer.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("user", "Context:\n{context}\n\nQuestion: {question}")
        ])
        
        # 3. Generate
        history = self.memory.load_memory_variables({})["history"]
        chain = prompt | self.llm
        response = chain.invoke({
            "history": history,
            "context": full_context,
            "question": query
        })
        
        # 4. Update Memory
        self.memory.save_context({"input": query}, {"output": response.content})
        
        return response.content, full_context

if __name__ == "__main__":
    bot = RAGBot()
    print("RAG Bot initialized (Chroma + Neo4j). Type 'exit' to quit.")
    while True:
        q = input("\nYou: ")
        if q.lower() == 'exit':
            break
        ans, ctx = bot.generate_response(q)
        print(f"Bot: {ans}")
