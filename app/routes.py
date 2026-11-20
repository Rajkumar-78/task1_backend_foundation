import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.auth import require_api_key
from app.database import get_db
from app.models import ChatSession, Message
from app.schemas import SessionCreated, MessageOut

router = APIRouter(dependencies=[Depends(require_api_key)])

@router.post("/sessions", response_model=SessionCreated, status_code=status.HTTP_201_CREATED)
def create_session(db: Session = Depends(get_db)):
    session = ChatSession(id=str(uuid.uuid4()))
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/sessions/{session_id}/messages", response_model=list[MessageOut])
def get_messages(session_id: str, db: Session = Depends(get_db)):
    session = db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return list(db.scalars(select(Message).where(
        Message.session_id == session_id
    ).order_by(Message.created_at, Message.id)).all())

@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    session = db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"detail": "Session deleted"}
