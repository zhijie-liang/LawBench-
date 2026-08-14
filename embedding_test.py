import os
import dashscope

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

resp = dashscope.TextEmbedding.call(
    model="text-embedding-v3",
    input="合同违约需要承担什么责任？",
    dimension=512
)

vector = resp.output["embeddings"][0]["embedding"]
print(len(vector))