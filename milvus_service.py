# 导入Milvus连接和工具
from pymilvus import connections, utility

# 连接本地Milvus
connections.connect("default", host="localhost", port="19530")
print("Milvus连接成功")

# 导入集合字段和结构定义工具
from pymilvus import FieldSchema, CollectionSchema, DataType, Collection

# 定义集合字段
fields = [
    # 自动生成主键
    FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
    # 保存原始文本
    FieldSchema("text", DataType.VARCHAR, max_length=2000),
    # 保存4维向量
    FieldSchema("vector", DataType.FLOAT_VECTOR, dim=4)
]
# 创建集合结构
schema = CollectionSchema(fields)
# 创建documents集合
collection = Collection("documents", schema)
print("documents集合创建成功")


fields = [
    FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema("text", DataType.VARCHAR, max_length=2000),
    FieldSchema("vector", DataType.FLOAT_VECTOR, dim=512)
]
schema = CollectionSchema(fields)
collection = Collection("document_chunks_v1", schema)
print("document_chunks_v1集合创建成功")





from document_service import load_documents

documents = load_documents()

from text_processor import clean_text, split_text

for document in documents:
    content = document[2]  # 第3项是正文
    cleaned = clean_text(content)
    print(cleaned)


for document in documents:
    content = clean_text(document[2])
    chunks = split_text(content)
    print("切块数量：", len(chunks))
    print(chunks[0])