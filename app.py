import os
from dotenv import load_dotenv
from chains.conversation_agent import get_llama_agent

load_dotenv()

def main():
    agent = get_llama_agent()
    name = input("Enter person or company name: ")
    question = f"""Find the LinkedIn profile of {name}, extract summary details,
and generate 3 professional and 2 casual conversation starters."""
    
    response = agent.run(question)
    print("\n📌 Conversation Starters:\n")
    print(response)

if __name__ == "__main__":
    main()

