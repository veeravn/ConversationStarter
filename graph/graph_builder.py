import os
from dotenv import load_dotenv
from langchain.chat_models import AzureChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from llama_index.core import VectorStoreIndex, Document

from tools.linkedin_search import search_linkedin
from tools.profile_scrapper import scrape_profile_text

load_dotenv()

# LangChain LLM setup with Azure OpenAI + LLaMA3
llm = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    openai_api_version="2024-03-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    model="llama3-8b",
    temperature=0.3,
)

# Step 1: Accept input
def start_node(state: dict) -> dict:
    return {"name": state["name"]}

# Step 2: Search LinkedIn profile URL
def search_node(state: dict) -> dict:
    profile_url = search_linkedin(state["name"])
    return {"profile_url": profile_url}

# Step 3: Scrape profile page
def scrape_node(state: dict) -> dict:
    profile_text = scrape_profile_text(state["profile_url"])
    return {"profile_text": profile_text}

# Step 4: Create RAG context from profile
def rag_node(state: dict) -> dict:
    document = Document(text=state["profile_text"])
    index = VectorStoreIndex.from_documents([document])
    query_engine = index.as_query_engine()
    context = query_engine.query("What are relevant conversation topics with this person?")
    return {"rag_context": str(context)}

# Step 5: Generate conversation prompts
def generate_node(state: dict) -> dict:
    prompt = f"""
    You are a professional networking assistant. Based on the following context:
    ---
    {state['rag_context']}
    ---
    Generate 3 professional and 2 casual conversation starters for someone meeting '{state['name']}' for the first time.
    """
    result = llm([HumanMessage(content=prompt)])
    return {"output": result.content}

# LangGraph workflow assembly
def build_convo_graph():
    builder = StateGraph()

    builder.add_node("start", start_node)
    builder.add_node("search", search_node)
    builder.add_node("scrape", scrape_node)
    builder.add_node("rag", rag_node)
    builder.add_node("generate", generate_node)

    builder.set_entry_point("start")
    builder.add_edge("start", "search")
    builder.add_edge("search", "scrape")
    builder.add_edge("scrape", "rag")
    builder.add_edge("rag", "generate")
    builder.add_edge("generate", END)

    return builder.compile()
