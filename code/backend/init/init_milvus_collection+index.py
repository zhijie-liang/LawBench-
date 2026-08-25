from pymilvus import MilvusClient, DataType
client = None

"""获取 Milvus 客户端（单例）。"""
if client is None:
    client = MilvusClient(uri="http://47.99.120.222:19530")
    print("Milvus连接成功")

COLLECTION = "document_chunks_v1"

if not client.has_collection(COLLECTION):
    schema = MilvusClient.create_schema(
        auto_id=True,
        enable_dynamic_field=False
    )
    schema.add_field("id", DataType.INT64, is_primary=True, auto_id=True)
    schema.add_field("document_id", DataType.INT64)
    schema.add_field("chunk_index", DataType.INT64)
    schema.add_field("text", DataType.VARCHAR, max_length=2000)
    schema.add_field("vector", DataType.FLOAT_VECTOR, dim=1024)
    client.create_collection(
        collection_name=COLLECTION,
        schema=schema
    )
    print("集合创建成功")

indexes = client.list_indexes(COLLECTION)
if "vector" not in indexes:
    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        index_type="FLAT",
        metric_type="L2",
        params={}
    )
    client.create_index(
        collection_name=COLLECTION,
        index_params=index_params
    )
    print("向量索引创建成功")

client.load_collection(COLLECTION)
print(client)
