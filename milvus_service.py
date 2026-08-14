# 导入Milvus连接和工具
import os
import dashscope
from pymilvus import connections, utility
from document_service import load_documents
from text_processor import clean_text, split_text

# 连接本地Milvus
connections.connect("default", host="localhost", port="19530")
print("Milvus连接成功")

# 导入集合字段和结构定义工具
from pymilvus import FieldSchema, CollectionSchema, DataType, Collection

fields = [
    FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema("document_id", DataType.INT64),
    FieldSchema("chunk_index", DataType.INT64),
    FieldSchema("text", DataType.VARCHAR, max_length=2000),
    FieldSchema("vector", DataType.FLOAT_VECTOR, dim=512)
]
schema = CollectionSchema(fields)
collection2 = Collection("document_chunks_v2", schema)
print("document_chunks_v2集合创建成功")


documents = load_documents()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

for document in documents:
    document_id = document[0]
    content = clean_text(document[2])
    if content == "暂只支持TXT文件":
        continue

    for index, chunk in enumerate(split_text(content)):
        resp = dashscope.TextEmbedding.call(
            model="text-embedding-v3",
            input=chunk,
            dimension=512
        )
        vector = resp.output["embeddings"][0]["embedding"]
        collection2.insert([[document_id], [index], [chunk], [vector]])

collection2.flush()
print("全部切块写入成功")


question = "合同违约如何处理？"
resp = dashscope.TextEmbedding.call(
    model="text-embedding-v3",
    input=question,
    dimension=512
)
query_vector = resp.output["embeddings"][0]["embedding"]

collection2.create_index(
    "vector",
    {"index_type": "FLAT", "metric_type": "L2", "params": {}}
)
collection2.load()

result = collection2.search(
    [query_vector], "vector",
    {"metric_type": "L2", "params": {}},
    limit=3,
    output_fields=["document_id", "chunk_index", "text"]
)
print(result)