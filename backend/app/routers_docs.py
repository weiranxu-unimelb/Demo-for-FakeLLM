from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from . import schemas
from .database import SessionLocal
from .deps import get_current_admin
from .models import Document

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
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
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
    doc = Document(filename=file.filename, content=content)
    db.add(doc)
    db.commit()
    db.refresh(doc)
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
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在",
        )
    db.delete(doc)
    db.commit()
    return None

