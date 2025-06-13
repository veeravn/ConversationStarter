from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
import os

class CustomAzureEmbedding(AzureOpenAIEmbedding):
    def __init__(self):
        super().__init__(
            deployment_name=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            model="text-embedding-3-small",  # matches model behind your deployment
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version="2024-02-15"
        )
