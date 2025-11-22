import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def setup_database():
    if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
        print("Error: Neo4j credentials missing in .env")
        return

    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        
        with driver.session() as session:
            print("Connected to Neo4j. Setting up constraints...")
            
            # Create uniqueness constraint for Entity nodes
            # Note: Syntax might vary slightly by Neo4j version, this is standard for 4.x/5.x
            try:
                session.run("CREATE CONSTRAINT FOR (n:Entity) REQUIRE n.name IS UNIQUE")
                print("Created constraint: Entity.name must be unique.")
            except Exception as e:
                print(f"Constraint creation note (might already exist): {e}")

            # Optional: Create index for faster lookup if constraint fails or for other labels
            try:
                session.run("CREATE INDEX FOR (n:Entity) ON (n.name)")
                print("Created index on Entity.name")
            except Exception as e:
                print(f"Index creation note: {e}")

        driver.close()
        print("Database setup complete.")

    except Exception as e:
        print(f"Database setup failed: {e}")

if __name__ == "__main__":
    setup_database()
