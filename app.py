from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from graph.graph_builder import build_convo_graph
from dotenv import load_dotenv
import re

load_dotenv()

app = FastAPI(title="AI Conversation Starter", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        result = graph.invoke({"name": request.name})
        raw_output = result["output"]

        # Normalize bullets: "1.", "•", "-" etc
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
        raise HTTPException(status_code=500, detail=str(e))
