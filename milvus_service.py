# 导入Milvus连接和工具
from pymilvus import connections
# 导入集合字段和结构定义工具
from pymilvus import FieldSchema, CollectionSchema, DataType, Collection

_collection = None
def get_collection():
    global _collection

    if _collection is None:
        # 连接本地Milvus
        connections.connect("default", host="localhost", port="19530")

        print("Milvus连接成功")

        fields = [
            FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema("document_id", DataType.INT64),
            FieldSchema("chunk_index", DataType.INT64),
            FieldSchema("text", DataType.VARCHAR, max_length=2000),
            FieldSchema("vector", DataType.FLOAT_VECTOR, dim=512)
        ]
        schema = CollectionSchema(fields)
        document_chunks = "document_chunks_v1"
        _collection = Collection(document_chunks, schema)
        print(f"{document_chunks}集合创建成功")

    return _collection









# question = "合同违约如何处理？"
# resp = dashscope.TextEmbedding.call(
#     model="text-embedding-v3",
#     input=question,
#     dimension=512
# )
# query_vector = resp.output["embeddings"][0]["embedding"]
#
# collection2.create_index(
#     "vector",
#     {"index_type": "FLAT", "metric_type": "L2", "params": {}}
# )
# collection2.load()
#
# result = collection2.search(
#     [query_vector], "vector",
#     {"metric_type": "L2", "params": {}},
#     limit=3,
#     output_fields=["document_id", "chunk_index", "text"]
# )
# print(result)