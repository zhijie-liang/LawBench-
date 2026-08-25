from langchain_community.embeddings.dashscope import DashScopeEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")


def embedding_dashscope():
    embedding_ds = DashScopeEmbeddings(
        model="text-embedding-v4",
        dashscope_api_key=api_key
    )
    return embedding_ds
