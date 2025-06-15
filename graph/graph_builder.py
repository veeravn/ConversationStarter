import os
from dotenv import load_dotenv
from typing import TypedDict

from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langgraph.graph import StateGraph, END

from llama_index.core import Settings, VectorStoreIndex, Document
from tools.linkedin_search import search_linkedin
from tools.profile_scrapper import scrape_profile_text

# Load environment variables
load_dotenv()

# ✅ Set up Embedding Model
Settings.embed_model = AzureOpenAIEmbeddings(
    deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),  # e.g. "veeravn-ai-text-embedding"
    model="text-embedding-3-small",  # must match your Azure deployment config
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    chunk_size=1000  # prevent KeyError
)

# ✅ Set up LLM for query and generation
from llama_index.llms.langchain import LangChainLLM
from langchain_openai import AzureChatOpenAI

chat_llm = AzureChatOpenAI(
    deployment_name="gpt-4.1",
    model="gpt-4",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# 👇 Wrap with LangChainLLM
Settings.llm = LangChainLLM(llm=chat_llm)

# ✅ Define the conversation state
class ConversationState(TypedDict, total=False):
    name: str
    profile_url: str
    profile_text: str
    rag_context: str
    output: str

# 🔹 Step 1: Start node
def start_node(state: ConversationState) -> ConversationState:
    return {"name": state["name"]}

# 🔹 Step 2: Search LinkedIn
def search_node(state: ConversationState) -> ConversationState:
    profile_url = search_linkedin(state["name"])
    print(f"🔍 Found LinkedIn profile URL: {profile_url}")
    if profile_url != "No profile found":
        return {"profile_url": profile_url}
    else:
        raise ValueError("No LinkedIn profile found for the given name.")

# 🔹 Step 3: Scrape LinkedIn profile
def scrape_node(state: ConversationState) -> ConversationState:
    profile_text = scrape_profile_text(state["profile_url"])
    return {"profile_text": profile_text}

# 🔹 Step 4: Generate RAG context from profile
def rag_node(state: ConversationState) -> ConversationState:
    document = Document(text=state["profile_text"])
    index = VectorStoreIndex.from_documents([document])
    query_engine = index.as_query_engine()
    context = query_engine.query("What are relevant conversation topics with this person?")
    return {"rag_context": str(context)}

# 🔹 Step 5: Generate conversation starters using LLM
def generate_node(state: ConversationState) -> ConversationState:
    prompt = f"""You are a professional networking assistant. Based on the following context:
        ---
        {state['rag_context']}
        ---
        Generate 3 professional and 2 casual conversation starters for someone meeting '{state['name']}' for the first time.
        Return only a list like this:
        Professional:
        1. ...
        2. ...
        3. ...
        Casual:
        1. ...
        2. ...
        """
    result = Settings.llm.complete(prompt)
    return {"output": result.text}

# 🔗 Build and compile the LangGraph
def build_convo_graph():
    builder = StateGraph(ConversationState)

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
