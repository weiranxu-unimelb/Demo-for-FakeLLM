import base64
import os
from typing import Any, Dict, Optional

from openai import OpenAI

from . import vector_store  # 引入真实向量数据库检索模块

# 初始化 OpenAI 客户端，指向本地的 Ollama 代理
# 我们使用服务名称 "ollama" 因为它们在同一个 docker-compose 网络中
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
# 使用多模态模型以支持图片：llama3.2-vision（支持中文+视觉）
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2-vision")

client = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key="ollama",  # 必填项，但实际不会校验
)


def get_rag_answer(text: str, image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
    """
    整合了真实 RAG 检索结果与多模态能力的对话接口。
    流程：
      1. 将用户问题向量化，在 ChromaDB 中检索相关的知识库片段
      2. 将检索结果拼入 System Prompt，强制模型基于知识库回答
      3. 如果有图片上传，同时传给模型进行多模态分析
    """
    # ---------------------------------------------------------------
    # 第 1 步：真实 RAG 检索（从 ChromaDB 语义搜索相关文档片段）
    # ---------------------------------------------------------------
    relevant_chunks = vector_store.search(query=text, k=3)

    if relevant_chunks:
        # 将多个相关段落拼接为参考资料字符串
        rag_context = "\n---\n".join(relevant_chunks)
        system_prompt = (
            "你是一个有用的公司内部 AI 助手。请直接、简明扼要地回答问题。\n"
            "回答时请优先基于以下【参考资料】中提供的信息，不要超出资料范围编造内容：\n"
            f"【参考资料】:\n{rag_context}"
        )
    else:
        # 知识库为空时，直接依赖模型自身知识回答
        rag_context = ""
        system_prompt = (
            "你是一个有用的公司内部 AI 助手。请直接、简明扼要地回答问题。\n"
            "（当前知识库为空，请根据通用知识回答，并提醒管理员上传相关文档。）"
        )

    # ---------------------------------------------------------------
    # 第 2 步：构造请求体（支持图片多模态输入）
    # ---------------------------------------------------------------
    messages = [{"role": "system", "content": system_prompt}]

    # 如果有图片上传，使用 Ollama vision 的多模态数组结构
    if image_bytes:
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        user_content = [
            {"type": "text", "text": text},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"  # 必须转 base64 才能喂给模型
                },
            },
        ]
    else:
        user_content = text

    messages.append({"role": "user", "content": user_content})

    # ---------------------------------------------------------------
    # 第 3 步：调用本地 Ollama 模型
    # ---------------------------------------------------------------
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
            "sources": [{"content": chunk, "source": "ChromaDB 向量检索"} for chunk in relevant_chunks],
            "model_used": MODEL_NAME,
            "has_image": bool(image_bytes),
            "rag_chunks_found": len(relevant_chunks),
        },
    }

