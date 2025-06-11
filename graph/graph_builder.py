import os
from langchain.chat_models import AzureChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph
from llama_index import VectorStoreIndex, Document
from tools.linkedin_search import search_linkedin
from tools.profile_scraper import scrape_profile_text

llm = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    openai_api_version="2024-03-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    temperature=0.3,
    model="llama3-8b"
)

### Shared state
def start_node(state):  # state = {'name': ...}
    return {"name": state["name"]}

def search_node(state):
    profile_url = search_linkedin(state["name"])
    return {"profile_url": profile_url}

def scrape_node(state):
    profile_text = scrape_profile_text(state["profile_url"])
    return {"profile_text": profile_text}

def rag_node(state):
    document = Document(text=state["profile_text"])
    index = VectorStoreIndex.from_documents([document])
    query_engine = index.as_query_engine()
    context = query_engine.query("What are relevant conversation topics with this person?")
    return {"rag_context": str(context)}

def generate_node(state):
    prompt = (
        f"""You are an expert conversation assistant. Based on this context:
        ---
        {state['rag_context']}
        ---
        Generate 3 professional and 2 casual conversation starters tailored to meeting '{state['name']}'."""
    )
    response = llm([HumanMessage(content=prompt)])
    return {"output": response.content}

### Graph Assembly
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
