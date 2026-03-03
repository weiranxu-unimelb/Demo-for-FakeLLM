"""
vector_store.py
使用 ChromaDB（专业向量数据库）+ Ollama 嵌入 API 实现 RAG 检索。
架构：
  - ChromaDB：负责向量存储、HNSW 索引、持久化（行业标准工具）
  - Ollama /api/embeddings：生成文本向量（使用 nomic-embed-text 模型）
  - 无需 PyTorch / sentence-transformers 等重型依赖

使用前需确认：
  docker exec -it ollama ollama pull nomic-embed-text
"""

import os
from typing import List

import requests
import chromadb

# -----------------------------------------------------------------------
# 配置
# -----------------------------------------------------------------------
_OLLAMA_HOST = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434/v1").replace("/v1", "")
_EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

_CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb")
_CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
_COLLECTION_NAME = "rag_documents"

_collection = None


def _get_collection():
    """懒加载 ChromaDB collection。"""
    global _collection
    if _collection is None:
        client = chromadb.HttpClient(host=_CHROMA_HOST, port=_CHROMA_PORT)
        _collection = client.get_or_create_collection(
            name=_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        print(f"[VectorStore] ChromaDB collection '{_COLLECTION_NAME}' 已就绪。")
    return _collection


# -----------------------------------------------------------------------
# Ollama 嵌入 API
# -----------------------------------------------------------------------
def _embed(text: str) -> List[float]:
    """调用 Ollama /api/embeddings 生成向量。"""
    resp = requests.post(
        f"{_OLLAMA_HOST}/api/embeddings",
        json={"model": _EMBED_MODEL, "prompt": text},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]


# -----------------------------------------------------------------------
# 文档分块
# -----------------------------------------------------------------------
def _split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start: start + chunk_size])
        start += chunk_size - overlap
    return chunks


# -----------------------------------------------------------------------
# 公共接口
# -----------------------------------------------------------------------

def index_document(doc_id: int, text: str) -> int:
    """分块 → Ollama 向量化 → 存入 ChromaDB。"""
    collection = _get_collection()
    chunks = _split_text(text)
    if not chunks:
        return 0

    print(f"[VectorStore] 向量化文档 doc_id={doc_id}，共 {len(chunks)} 块...")
    embeddings = [_embed(c) for c in chunks]
    ids = [f"doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))]

    delete_document(doc_id)  # 支持重新上传覆盖
    collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
    print(f"[VectorStore] doc_id={doc_id} 入库完成，{len(chunks)} 个向量块。")
    return len(chunks)


def delete_document(doc_id: int) -> None:
    """从 ChromaDB 删除指定文档的所有向量块。"""
    try:
        collection = _get_collection()
        collection.delete(where={"doc_id": doc_id})
        print(f"[VectorStore] doc_id={doc_id} 的向量块已删除。")
    except Exception as e:
        print(f"[VectorStore] 删除时出错（可忽略）: {e}")


def search(query: str, k: int = 3) -> List[str]:
    """语义搜索：返回最相关的 k 条文本片段。"""
    try:
        collection = _get_collection()
        if collection.count() == 0:
            return []
        query_emb = _embed(query)
        results = collection.query(
            query_embeddings=[query_emb],
            n_results=min(k, collection.count()),
            include=["documents"],
        )
        return results.get("documents", [[]])[0]
    except Exception as e:
        print(f"[VectorStore] 检索失败（nomic-embed-text 是否已下载？）: {e}")
        return []
