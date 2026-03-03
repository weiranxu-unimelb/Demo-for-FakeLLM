import os
from typing import Any, Dict, Optional
from openai import OpenAI

# 初始化 OpenAI 客户端，指向本地的 Ollama 代理
# 我们使用服务名称 "ollama" 因为它们在同一个 docker-compose 网络中
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
# 使用多模态模型以支持图片，例如 qwen2.5-vl 或者 llava 相关模型。
# 注意：Ollama 里跑多模态需要对应的模型（比如 llava/qwen2.5-vl 等）。假设模型名为 qwen2.5:7b (需支持视觉) 或 llava。
MODEL_NAME = os.getenv("MODEL_NAME", "llava")

client = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key="ollama", # 必填项，但实际不会校验
)

import base64

def simulate_rag_retrieval(query: str) -> str:
    """
    这里是一个占位函数，用来模拟真实的 RAG 检索过程。
    实际使用中，你需要在这里连接到如 FAISS, ChromaDB 或者 Milvus 等向量数据库，
    进行 query embeddings 计算并召回相关文档片段。
    """
    # 假设这里是检索到的内部知识库短语
    retrieved_context = "【公司内部规范规定：货架底层只允许摆放重量大于20kg或体积超大的重物；高层适合摆放轻量物品。】"
    return retrieved_context

def get_rag_answer(text: str, image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
    """
    整合了 RAG 检索结果与多模态能力的对话接口。
    """
    # 1. 第一步：检索相关知识库内容 (RAG Context)
    rag_context = simulate_rag_retrieval(text)

    # 2. 第二步：拼接系统提示词，强制模型基于检索结果回答
    system_prompt = (
        "你是一个有用的公司内部 AI 助手。请直接、简明扼要地回答问题。\n"
        "回答时请优先基于以下【参考资料】中提供的信息：\n"
        f"【参考资料】: {rag_context}"
    )

    # 3. 构造请求体 (包括可能的图片多模态输入)
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # 如果有图片上传，则使用 GPT-4-vision / Ollama-vision 支持的多模态数组结构
    if image_bytes:
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        user_content = [
            {"type": "text", "text": text},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}" # 必须转换为 base64 喂给模型
                }
            }
        ]
    else:
        user_content = text

    messages.append({"role": "user", "content": user_content})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"与本地 LLM 通信时出错。ollama 容器是否成功启动？详细信息: {e}"

    return {
        "answer": answer,
        "meta": {
            "sources": [{"content": rag_context, "source": "模拟检索来源"}],
            "model_used": MODEL_NAME,
            "has_image": bool(image_bytes)
        },
    }

