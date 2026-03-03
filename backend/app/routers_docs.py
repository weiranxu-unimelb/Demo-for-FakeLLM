from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from . import schemas
from .database import SessionLocal
from .deps import get_current_admin
from .models import Document
from . import vector_store  # 引入向量数据库模块

router = APIRouter(prefix="/admin/docs", tags=["admin-docs"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "",
    response_model=schemas.DocumentOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    上传 TXT 知识库文件：
    1. 保存到 SQLite（便于前端展示和管理）
    2. 在后台异步向量化并存入 ChromaDB（不阻塞 HTTP 响应）
    """
    if not file.filename.lower().endswith(".txt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="目前仅支持上传 .txt 文本文件作为知识库",
        )
    raw = await file.read()
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文本文件必须为 UTF-8 编码",
        )
    # 存入关系数据库
    doc = Document(filename=file.filename, content=content)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 在后台异步向量化，不阻塞 HTTP 响应（大文件时不会超时）
    background_tasks.add_task(vector_store.index_document, doc.id, content)

    return doc


@router.get("", response_model=List[schemas.DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return db.query(Document).order_by(Document.created_at.desc()).all()


@router.get("/{doc_id}", response_model=schemas.DocumentDetail)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在",
        )
    return doc


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    删除文档：同时从 SQLite 和 ChromaDB 向量库中清除。
    """
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在",
        )
    # 从向量库删除
    vector_store.delete_document(doc_id)
    # 从关系数据库删除
    db.delete(doc)
    db.commit()
    return None


