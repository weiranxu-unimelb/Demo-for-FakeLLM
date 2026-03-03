from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from . import schemas
from .database import SessionLocal
from .deps import get_current_employee
from .models import Question
from .rag import get_rag_answer

router = APIRouter(prefix="/chat", tags=["chat"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/query", response_model=schemas.QuestionOut)
async def query(
    text: str = Form(...),
    image: Optional[UploadFile] = File(default=None),
    current_user=Depends(get_current_employee),
    db: Session = Depends(get_db),
):
    image_bytes = await image.read() if image is not None else None
    rag_result = get_rag_answer(text, image_bytes=image_bytes)
    answer_text = rag_result["answer"]

    q = Question(
        user_id=current_user.id,
        question_text=text,
        answer_text=answer_text,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q

