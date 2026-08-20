from langchain_community.chat_models import ChatTongyi


def llm_qwen(tt: float):
    llm = ChatTongyi(
        model="qwen3-vl-plus",
        temperature=tt
    )
    return llm