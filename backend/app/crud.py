from sqlalchemy.orm import Session
from . import models, schemas

def get_memo(db: Session, memo_id: int):
    return db.query(models.Memo).filter(models.Memo.id == memo_id).first()

def get_memos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Memo).offset(skip).limit(limit).all()

def create_memo(db: Session, memo: schemas.MemoCreate):
    db_memo = models.Memo(title=memo.title, content=memo.content)
    db.add(db_memo)
    db.commit()
    db.refresh(db_memo)
    return db_memo

def update_memo(db: Session, memo_id: int, memo: schemas.MemoUpdate):
    db_memo = get_memo(db, memo_id)
    if db_memo:
        if memo.title is not None:
            db_memo.title = memo.title
        if memo.content is not None:
            db_memo.content = memo.content
        db.commit()
        db.refresh(db_memo)
    return db_memo

def delete_memo(db: Session, memo_id: int):
    db_memo = get_memo(db, memo_id)
    if db_memo:
        db.delete(db_memo)
        db.commit()
    return db_memo
