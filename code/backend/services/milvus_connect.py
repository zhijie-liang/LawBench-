from pymilvus import MilvusClient


def milvus_insert(data: list):
    client = MilvusClient(uri="http://47.99.120.222:19530")
    print("Milvus连接成功")
    client.insert(
        collection_name="document_chunks_v1",
        data=data
    )
    print(f"Milvus入库完成，共{len(data)}条")
    return f"Milvus入库完成，共{len(data)}条"


def milvus_client(query_vector: str,limit: int):
    client = MilvusClient(
                uri="http://47.99.120.222:19530"
            )
    print("Milvus连接成功")
    results = client.search(
        collection_name="document_chunks_v1",
        data=[query_vector],
        anns_field="vector",
        limit=limit,
        output_fields=[
            "text",
            "document_id",
            "chunk_index"
        ]
    )
    return results