from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from services.llm import llm_qwen
from services.milvus_connect import milvus_client
from services.embedding import embedding_dashscope


def rag_chat(question: str):
    # 1. 问题向量化
    embeddings = embedding_dashscope()
    query_vector = embeddings.embed_query(question)
    # 2. Milvus检索
    results = milvus_client(query_vector, 3)
    # 3. 拼接检索结果
    context = "\n\n".join(
        hit["entity"]["text"]
        for hit in results[0]
    )
    # 4. Prompt
    prompt = ChatPromptTemplate.from_template("""
        你是一个企业知识库问答助手。

        请严格根据下面资料回答。
        如果资料中没有答案，请回答“知识库中没有相关信息”。

        知识库资料：
        {context}

        用户问题：
        {question}

        回答：
        """)
    # 5. LLM
    llm = llm_qwen(0.1)
    chain = prompt | llm | StrOutputParser()

    return chain.invoke({
        "context": context,
        "question": question
    })