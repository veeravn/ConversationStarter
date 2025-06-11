import os
from dotenv import load_dotenv
from graph.graph_builder import build_convo_graph

load_dotenv()
graph = build_convo_graph()

def main():
    name = input("Enter a person's or company's name: ")
    final_state = graph.invoke({"name": name})
    print("\n📌 Conversation Starters:\n")
    print(final_state["output"])

if __name__ == "__main__":
    main()
