import os
from langchain.chat_models import AzureChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain.tools import tool
from tools.linkedin_search import search_linkedin
from tools.profile_scraper import scrape_profile_text

@tool
def linkedin_search_tool(name: str) -> str:
    """Search LinkedIn profile for a person or business."""
    return search_linkedin(name)

@tool
def profile_summary_tool(url: str) -> str:
    """Scrape a summary of a LinkedIn profile."""
    return scrape_profile_text(url)

def get_llama_agent():
    llm = AzureChatOpenAI(
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        openai_api_version="2024-03-01-preview",
        model="llama3-8b",
        temperature=0.3,
    )

    tools = [linkedin_search_tool, profile_summary_tool]
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    return agent

