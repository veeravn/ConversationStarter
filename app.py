from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from graph.graph_builder import build_convo_graph
from dotenv import load_dotenv
import re, traceback, os

load_dotenv()
print("🔍 LLM Deployment:", os.getenv("AZURE_OPENAI_DEPLOYMENT"))
print("🔍 Embed Deployment Name:", os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"))
print("🔍 Embed Model ID:", os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"))
app = FastAPI(title="AI Conversation Starter", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Or "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_convo_graph()

class ConversationRequest(BaseModel):
    name: str

class ConversationResponse(BaseModel):
    name: str
    professional: list[str]
    casual: list[str]

@app.post("/generate", response_model=ConversationResponse)
def generate_conversation(request: ConversationRequest):
    try:
        print(f"\n🔍 Invoking LangGraph with name: {request.name}")
        result = graph.invoke({"name": request.name})

        raw_output = result.get("output", "")
        print(f"\n📄 Raw LLM Output:\n{raw_output}\n")

        # Split into bullet points
        bullets = re.split(r'\n+|\d+\.\s*|[-•]\s*', raw_output)
        cleaned = [b.strip() for b in bullets if len(b.strip()) > 10]

        if len(cleaned) < 5:
            raise ValueError("Expected at least 5 conversation starters from LLM.")

        return {
            "name": request.name,
            "professional": cleaned[:3],
            "casual": cleaned[3:5]
        }

    except Exception as e:
        print("\n❌ Internal Server Error:\n")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
