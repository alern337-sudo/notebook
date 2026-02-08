from fastapi import FastAPI, Depends, HTTPException, Body, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas, crud
from .database import SessionLocal, engine
import redis
import json
import os
import shutil
import uuid
from datetime import datetime, timezone, timedelta

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount static files
if not os.path.exists("backend/uploads"):
    os.makedirs("backend/uploads")
app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")

# 东八区时区
CN_TZ = timezone(timedelta(hours=8))

def to_cn_time(dt):
    """将时间转换为东八区时间字符串"""
    if dt is None:
        return None
    # 如果是 naive 时间（数据库读取），视为本地时间 (东八区)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=CN_TZ)
    else:
        # 如果是 aware 时间，转换到东八区
        dt = dt.astimezone(CN_TZ)
    return dt.isoformat()

def subtask_to_dict(st):
    return {
        "id": st.id, 
        "content": st.content,
        "note": st.note,
        "is_completed": st.is_completed, 
        "order": st.order,
        "memo_id": st.memo_id,
        "created_at": to_cn_time(st.created_at),
        "completed_at": to_cn_time(st.completed_at),
        "attachments": [
            {
                "id": a.id,
                "filename": a.filename,
                "file_path": a.file_path,
                "created_at": to_cn_time(a.created_at)
            } for a in st.attachments
        ]
    }

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
            subtask_to_dict(st)
            for st in sorted(memo.subtasks, key=lambda x: x.order)
        ]
    }

def template_to_dict(template):
    return {
        "id": template.id,
        "title": template.title,
        "content": template.content,
        "category": template.category,
        "created_at": to_cn_time(template.created_at),
        "subtasks": [
            {
                "id": st.id,
                "content": st.content,
                "order": st.order,
                "template_id": st.template_id
            }
            for st in sorted(template.subtasks, key=lambda x: x.order)
        ]
    }

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis 连接
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
except:
    r = None 

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/memos/", response_model=dict)
def create_memo(memo: schemas.MemoCreate, db: Session = Depends(get_db)):
    db_memo = crud.create_memo(db=db, memo=memo)
    # 清除缓存
    if r:
        keys = r.keys("memos_list_*")
        if keys:
            r.delete(*keys)
    return memo_to_dict(db_memo)

@app.get("/memos/", response_model=List[dict])
def read_memos(skip: int = 0, limit: int = 100, category: str = None, db: Session = Depends(get_db)):
    memos = crud.get_memos(db, skip=skip, limit=limit, category=category)
    return [memo_to_dict(memo) for memo in memos]

@app.get("/memos/{memo_id}", response_model=dict)
def read_memo(memo_id: int, db: Session = Depends(get_db)):
    db_memo = crud.get_memo(db, memo_id=memo_id)
    if db_memo is None:
        raise HTTPException(status_code=404, detail="Memo not found")
    return memo_to_dict(db_memo)

@app.put("/memos/{memo_id}", response_model=dict)
def update_memo(memo_id: int, memo: schemas.MemoUpdate, db: Session = Depends(get_db)):
    db_memo = crud.get_memo(db, memo_id)
    if not db_memo:
        raise HTTPException(status_code=404, detail="Memo not found")
    
    # Update fields
    if memo.title is not None:
        db_memo.title = memo.title
    if memo.content is not None:
        db_memo.content = memo.content
    if memo.category is not None:
        db_memo.category = memo.category
    if memo.deadline is not None:
        dt = memo.deadline
        if dt.tzinfo is not None:
            dt = dt.astimezone(CN_TZ)
        db_memo.deadline = dt.replace(tzinfo=None)
    elif memo.deadline is None and "deadline" in memo.dict(exclude_unset=True):
         db_memo.deadline = None

    if memo.completed_at is not None:
        dt = memo.completed_at
        if dt.tzinfo is not None:
            dt = dt.astimezone(CN_TZ)
        db_memo.completed_at = dt.replace(tzinfo=None)
    elif "completed_at" in memo.dict(exclude_unset=True) and memo.completed_at is None:
        db_memo.completed_at = None

    # Handle Subtasks
    if memo.subtasks is not None:
        # Get existing subtask IDs
        existing_ids = {st.id: st for st in db_memo.subtasks}
        incoming_ids = {st.id for st in memo.subtasks if st.id is not None}
        
        # Delete removed subtasks
        for st_id, st in existing_ids.items():
            if st_id not in incoming_ids:
                db.delete(st)
        
        # Update or create
        for index, st_data in enumerate(memo.subtasks):
            if st_data.id and st_data.id in existing_ids:
                # Update
                st = existing_ids[st_data.id]
                st.content = st_data.content
                st.note = st_data.note
                st.order = index
                st.is_completed = st_data.is_completed
                if st_data.created_at:
                     dt = st_data.created_at
                     if dt.tzinfo is not None: dt = dt.astimezone(CN_TZ)
                     st.created_at = dt.replace(tzinfo=None)
                if st_data.completed_at:
                     dt = st_data.completed_at
                     if dt.tzinfo is not None: dt = dt.astimezone(CN_TZ)
                     st.completed_at = dt.replace(tzinfo=None)
                elif st_data.is_completed and not st.completed_at:
                     st.completed_at = datetime.now()
                elif not st_data.is_completed:
                     st.completed_at = None
            else:
                # Create
                new_st_data = st_data.dict(exclude={'id'})
                new_st_data['order'] = index
                if new_st_data.get('created_at'):
                     dt = new_st_data['created_at']
                     if dt.tzinfo is not None: dt = dt.astimezone(CN_TZ)
                     new_st_data['created_at'] = dt.replace(tzinfo=None)
                if new_st_data.get('completed_at'):
                     dt = new_st_data['completed_at']
                     if dt.tzinfo is not None: dt = dt.astimezone(CN_TZ)
                     new_st_data['completed_at'] = dt.replace(tzinfo=None)
                
                new_st = models.SubTask(**new_st_data, memo_id=db_memo.id)
                db.add(new_st)

    db.commit()
    db.refresh(db_memo)
    if r:
        keys = r.keys("memos_list_*")
        if keys:
            r.delete(*keys)
    return memo_to_dict(db_memo)

@app.patch("/memos/{memo_id}/status")
def update_memo_status(memo_id: int, status: dict = Body(...), db: Session = Depends(get_db)):
    db_memo = crud.get_memo(db, memo_id)
    if not db_memo:
        raise HTTPException(status_code=404, detail="Memo not found")
    
    is_completed = status.get("is_completed")
    if is_completed:
        db_memo.completed_at = datetime.now()
    else:
        db_memo.completed_at = None
        
    db.commit()
    db.refresh(db_memo)
    if r:
        keys = r.keys("memos_list_*")
        if keys:
            r.delete(*keys)
    return memo_to_dict(db_memo)

@app.patch("/subtasks/{subtask_id}/status")
def update_subtask_status(subtask_id: int, status: dict = Body(...), db: Session = Depends(get_db)):
    subtask = db.query(models.SubTask).filter(models.SubTask.id == subtask_id).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")
        
    is_completed = status.get("is_completed")
    subtask.is_completed = is_completed
    if is_completed:
        subtask.completed_at = datetime.now()
    else:
        subtask.completed_at = None
        
    # Sync memo status
    crud._sync_memo_status(db, subtask.memo)
    
    db.commit()
    
    # Return parent memo
    db.refresh(subtask.memo)
    if r:
        keys = r.keys("memos_list_*")
        if keys:
            r.delete(*keys)
    return memo_to_dict(subtask.memo)

@app.delete("/memos/{memo_id}")
def delete_memo(memo_id: int, db: Session = Depends(get_db)):
    db_memo = crud.get_memo(db, memo_id)
    if not db_memo:
        raise HTTPException(status_code=404, detail="Memo not found")
    
    db.delete(db_memo)
    db.commit()
    
    if r:
        keys = r.keys("memos_list_*")
        if keys:
            r.delete(*keys)
    return {"status": "success"}

@app.get("/templates/", response_model=List[dict])
def read_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    templates = crud.get_templates(db, skip=skip, limit=limit)
    return [template_to_dict(t) for t in templates]

@app.post("/templates/", response_model=dict)
def create_template(template: schemas.TemplateCreate, db: Session = Depends(get_db)):
    db_template = crud.create_template(db, template)
    return template_to_dict(db_template)

@app.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    crud.delete_template(db, template_id)
    return {"status": "success"}

@app.get("/memos/{memo_id}/stats")
def get_memo_stats(memo_id: int, db: Session = Depends(get_db)):
    db_memo = crud.get_memo(db, memo_id)
    if not db_memo:
        raise HTTPException(status_code=404, detail="Memo not found")
    
    if not db_memo.subtasks:
        return []
    
    completed_subtasks = [st for st in db_memo.subtasks if st.is_completed and st.completed_at]
    completed_subtasks.sort(key=lambda x: x.completed_at)
    
    stats = []
    
    for st in completed_subtasks:
        start = st.created_at
        end = st.completed_at
        
        if not start:
            start = db_memo.created_at
        
        # Ensure timezones match
        if start.tzinfo is None and end.tzinfo is not None:
            start = start.replace(tzinfo=end.tzinfo)
        elif start.tzinfo is not None and end.tzinfo is None:
            end = end.replace(tzinfo=start.tzinfo)
        
        duration = (end - start).total_seconds() / 3600 # hours
        if duration < 0:
            duration = 0 
        
        stats.append({
            "name": st.content,
            "value": round(duration, 2)
        })
    
    return stats

@app.post("/subtasks/{subtask_id}/attachments", response_model=schemas.SubtaskAttachment)
async def upload_attachment(subtask_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Verify subtask exists
    subtask = db.query(models.SubTask).filter(models.SubTask.id == subtask_id).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join("backend/uploads", unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Create DB entry
    attachment_data = {
        "filename": file.filename,
        "file_path": unique_filename,
        "file_size": os.path.getsize(file_path),
        "content_type": file.content_type,
        "subtask_id": subtask_id
    }
    
    return crud.create_subtask_attachment(db, attachment_data)

@app.put("/attachments/{attachment_id}", response_model=schemas.SubtaskAttachment)
def update_attachment(attachment_id: int, attachment: schemas.SubtaskAttachmentUpdate, db: Session = Depends(get_db)):
    db_attachment = crud.get_subtask_attachment(db, attachment_id)
    if not db_attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    return crud.update_subtask_attachment(db, attachment_id, attachment)

@app.delete("/attachments/{attachment_id}")
def delete_attachment(attachment_id: int, db: Session = Depends(get_db)):
    attachment = crud.get_subtask_attachment(db, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
        
    # Delete file from disk
    full_path = os.path.join("backend/uploads", attachment.file_path)
    if os.path.exists(full_path):
        os.remove(full_path)
        
    # Delete from DB
    crud.delete_subtask_attachment(db, attachment_id)
    return {"status": "success"}
