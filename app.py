from dotenv import load_dotenv
from graph.graph_builder import build_convo_graph

load_dotenv()
graph = build_convo_graph()

def main():
    print("🔍 AI Conversation Starter")
    name = input("Enter a person or business name: ").strip()
    
    print(f"\nSearching and generating personalized conversation prompts for '{name}'...\n")
    final_state = graph.invoke({"name": name})
    
    print("\n Conversation Starters:\n")
    print(final_state["output"])

if __name__ == "__main__":
    main()
