import sys
import os
from rag_bot import RAGBot

def test_rag_system():
    print("Initializing RAG Bot (Chroma + Neo4j)...")
    try:
        bot = RAGBot()
    except Exception as e:
        print(f"Failed to initialize bot: {e}")
        print("Please ensure .env is set up correctly.")
        return

    test_questions = [
        "Who are the main characters in the stories?",
        "What is the moral of the story about the turtle?", 
        "Tell me about a specific vocabulary word defined in the text.",
        "What is the capital of France?" # Hallucination test
    ]

    print("\n--- Starting Verification Tests ---")

    for q in test_questions:
        print(f"\nTest Question: {q}")
        try:
            answer, context = bot.generate_response(q)
            print(f"Answer: {answer}")
            
            if "cannot find" in answer.lower() and "France" in q:
                print("✅ Hallucination Check Passed")
            elif "cannot find" not in answer.lower() and "France" not in q:
                print("✅ Answer Generated")
            else:
                print("⚠️ Check Answer Quality")
                
        except Exception as e:
            print(f"❌ Test Failed: {e}")

if __name__ == "__main__":
    test_rag_system()
