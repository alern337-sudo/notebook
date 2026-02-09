from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone, timedelta
import shutil
import os
import uuid
from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Create uploads directory if not exists
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

CN_TZ = timezone(timedelta(hours=8))

def to_cn_time(dt):
    if not dt:
        return None
    if dt.tzinfo is None:
        return dt.strftime("%Y-%m-%d %H:%M")
    return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M")

# Memos
def memo_to_dict(memo):
    return {
        "id": memo.id,
        "title": memo.title,
        "content": memo.content,
        "category": memo.category,
        "created_at": to_cn_time(memo.created_at),
        "updated_at": to_cn_time(memo.updated_at),
        "completed_at": to_cn_time(memo.completed_at),
        "deadline": to_cn_time(memo.deadline),
        "subtasks": [
            {
                "id": st.id,
                "content": st.content,
                "is_completed": st.is_completed,
                "order": st.order,
                "created_at": to_cn_time(st.created_at),
                "start_time": to_cn_time(st.start_time),
                "completed_at": to_cn_time(st.completed_at),
                "note": st.note,
                "attachments": [
                    {
                        "id": att.id,
                        "filename": att.filename,
                        "file_path": att.file_path,
                        "file_size": att.file_size,
                        "content_type": att.content_type,
                        "created_at": to_cn_time(att.created_at)
                    } for att in st.attachments
                ]
            } for st in sorted(memo.subtasks, key=lambda x: x.order)
        ]
    }

@app.post("/memos/", response_model=dict)
def create_memo(memo: schemas.MemoCreate, db: Session = Depends(get_db)):
    db_memo = crud.create_memo(db, memo)
    return memo_to_dict(db_memo)

@app.get("/memos/", response_model=List[dict])
def read_memos(skip: int = 0, limit: int = 100, category: str = None, db: Session = Depends(get_db)):
    memos = crud.get_memos(db, skip=skip, limit=limit, category=category)
    return [memo_to_dict(memo) for memo in memos]

@app.get("/memos/{memo_id}", response_model=dict)
def read_memo(memo_id: int, db: Session = Depends(get_db)):
    db_memo = crud.get_memo(db, memo_id)
    if db_memo is None:
        raise HTTPException(status_code=404, detail="Memo not found")
    return memo_to_dict(db_memo)

@app.put("/memos/{memo_id}", response_model=dict)
def update_memo(memo_id: int, memo: schemas.MemoUpdate, db: Session = Depends(get_db)):
    db_memo = crud.update_memo(db, memo_id, memo)
    if db_memo is None:
        raise HTTPException(status_code=404, detail="Memo not found")
    return memo_to_dict(db_memo)

@app.delete("/memos/{memo_id}", response_model=dict)
def delete_memo(memo_id: int, db: Session = Depends(get_db)):
    db_memo = crud.delete_memo(db, memo_id)
    if db_memo is None:
        raise HTTPException(status_code=404, detail="Memo not found")
    return memo_to_dict(db_memo)

@app.patch("/subtasks/{subtask_id}/status", response_model=dict)
def update_subtask_status(subtask_id: int, status: schemas.SubTaskUpdate, db: Session = Depends(get_db)):
    if status.is_completed is None:
        raise HTTPException(status_code=400, detail="is_completed field is required")
        
    db_subtask = crud.update_subtask_status(db, subtask_id, status.is_completed)
    if db_subtask is None:
        raise HTTPException(status_code=404, detail="Subtask not found")
        
    return {
        "id": db_subtask.id,
        "is_completed": db_subtask.is_completed,
        "completed_at": to_cn_time(db_subtask.completed_at)
    }

@app.post("/subtasks/{subtask_id}/attachments", response_model=dict)
async def upload_subtask_attachment(subtask_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Verify subtask exists
    subtask = db.query(models.SubTask).filter(models.SubTask.id == subtask_id).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")

    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create DB record
    attachment_data = schemas.SubtaskAttachmentCreate(
        filename=file.filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        content_type=file.content_type or "application/octet-stream"
    )
    
    db_attachment = crud.create_subtask_attachment(db, attachment_data, subtask_id)

    return {
        "id": db_attachment.id,
        "filename": db_attachment.filename,
        "file_path": db_attachment.file_path,
        "file_size": db_attachment.file_size,
        "content_type": db_attachment.content_type,
        "created_at": to_cn_time(db_attachment.created_at)
    }

@app.delete("/attachments/{attachment_id}", response_model=dict)
def delete_attachment(attachment_id: int, db: Session = Depends(get_db)):
    # Get attachment to find file path
    db_attachment = crud.get_subtask_attachment(db, attachment_id)
    if not db_attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    # Delete file from disk
    if db_attachment.file_path and os.path.exists(db_attachment.file_path):
        try:
            os.remove(db_attachment.file_path)
        except Exception as e:
            print(f"Error deleting file {db_attachment.file_path}: {e}")
            # Continue to delete DB record even if file deletion fails
            
    # Delete DB record
    deleted_attachment = crud.delete_subtask_attachment(db, attachment_id)
    
    return {
        "id": deleted_attachment.id,
        "filename": deleted_attachment.filename
    }

@app.put("/attachments/{attachment_id}", response_model=dict)
def update_attachment(attachment_id: int, attachment: schemas.SubtaskAttachmentUpdate, db: Session = Depends(get_db)):
    db_attachment = crud.update_subtask_attachment(db, attachment_id, attachment)
    if not db_attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    return {
        "id": db_attachment.id,
        "filename": db_attachment.filename,
        "file_path": db_attachment.file_path,
        "file_size": db_attachment.file_size,
        "content_type": db_attachment.content_type,
        "created_at": to_cn_time(db_attachment.created_at)
    }

# Templates
@app.post("/templates/", response_model=schemas.Template)
def create_template(template: schemas.TemplateCreate, db: Session = Depends(get_db)):
    return crud.create_template(db, template)

@app.get("/templates/", response_model=List[schemas.Template])
def read_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_templates(db, skip=skip, limit=limit)

# Consumables
def consumable_to_dict(c):
    return {
        "id": c.id,
        "name": c.name,
        "tag": c.tag,
        "category": c.category,
        "model_spec": c.model_spec,
        "status": c.status,
        "last_replaced": c.last_replaced.isoformat() if c.last_replaced else None,
        "lifespan": c.lifespan,
        "expiry_date": c.expiry_date.isoformat() if c.expiry_date else None,
        "mileage": c.mileage,
        "current_mileage": c.current_mileage,
        "created_at": to_cn_time(c.created_at),
        "updated_at": to_cn_time(c.updated_at),
        "logs": [
            {
                "id": l.id,
                "replaced_at": l.replaced_at.isoformat(),
                "mileage": l.mileage,
                "days_since_last": l.days_since_last,
                "km_since_last": l.km_since_last,
                "note": l.note,
                "created_at": to_cn_time(l.created_at)
            } for l in sorted(c.logs, key=lambda x: x.replaced_at, reverse=True)
        ]
    }

@app.get("/consumables/", response_model=List[dict])
def read_consumables(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    consumables = crud.get_consumables(db, skip=skip, limit=limit)
    return [consumable_to_dict(c) for c in consumables]

@app.post("/consumables/", response_model=dict)
def create_consumable(consumable: schemas.ConsumableCreate, db: Session = Depends(get_db)):
    db_consumable = crud.create_consumable(db, consumable)
    return consumable_to_dict(db_consumable)

@app.put("/consumables/{consumable_id}", response_model=dict)
def update_consumable(consumable_id: int, consumable: schemas.ConsumableUpdate, db: Session = Depends(get_db)):
    db_consumable = crud.update_consumable(db, consumable_id, consumable)
    if not db_consumable:
        raise HTTPException(status_code=404, detail="Consumable not found")
    return consumable_to_dict(db_consumable)

@app.delete("/consumables/{consumable_id}", response_model=dict)
def delete_consumable(consumable_id: int, db: Session = Depends(get_db)):
    db_consumable = crud.delete_consumable(db, consumable_id)
    if not db_consumable:
        raise HTTPException(status_code=404, detail="Consumable not found")
    return consumable_to_dict(db_consumable)

@app.post("/consumables/{consumable_id}/replace", response_model=dict)
def replace_consumable(consumable_id: int, log: schemas.ConsumableLogCreate, db: Session = Depends(get_db)):
    db_consumable = crud.replace_consumable(db, consumable_id, log.replaced_at, log.mileage, log.note)
    if not db_consumable:
        raise HTTPException(status_code=404, detail="Consumable not found")
    return consumable_to_dict(db_consumable)
