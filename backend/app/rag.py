from typing import Any, Dict, Optional


def get_rag_answer(text: str, image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
    """
    占位函数：这里未来接入 RAG + 多模态模型。

    当前 Demo：仅回显问题，并提示尚未接入真实大模型。
    """
    answer = f"【Demo 回答】收到你的问题：{text}。当前还未接入真实大模型和知识库。"
    return {
        "answer": answer,
        "meta": {
            "sources": [],
        },
    }

