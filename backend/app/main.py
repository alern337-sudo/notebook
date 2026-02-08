from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, crud
from .database import SessionLocal, engine
import redis
import json
from datetime import datetime, timezone, timedelta

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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
        "completed_at": to_cn_time(st.completed_at)
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
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/memos/", response_model=schemas.Memo)
def create_memo(memo: schemas.MemoCreate, db: Session = Depends(get_db)):
    db_memo = crud.create_memo(db=db, memo=memo)
    # 清除缓存
    keys = r.keys("memos_list_*")
    if keys:
        r.delete(*keys)
    return memo_to_dict(db_memo)

@app.patch("/subtasks/{subtask_id}/status", response_model=schemas.SubTask)
def update_subtask_status(subtask_id: int, is_completed: bool = Body(..., embed=True), db: Session = Depends(get_db)):
    subtask = crud.update_subtask_status(db, subtask_id, is_completed)
    if subtask is None:
        raise HTTPException(status_code=404, detail="SubTask not found")
    
    # 清除缓存
    keys = r.keys("memos_list_*")
    if keys:
        r.delete(*keys)
        
    return subtask_to_dict(subtask)

@app.put("/memos/{memo_id}/subtasks/reorder")
def reorder_subtasks(memo_id: int, subtask_ids: List[int] = Body(...), db: Session = Depends(get_db)):
    result = crud.reorder_subtasks(db, memo_id, subtask_ids)
    if not result:
        raise HTTPException(status_code=404, detail="Memo not found or subtasks mismatch")
    
    # 清除缓存
    keys = r.keys("memos_list_*")
    if keys:
        r.delete(*keys)
        
    return {"status": "success"}

@app.get("/memos/", response_model=List[schemas.Memo])
def read_memos(skip: int = 0, limit: int = 100, category: str = None, db: Session = Depends(get_db)):
    # 尝试从缓存获取
    cache_key = f"memos_list_{skip}_{limit}_{category}"
    cached_data = r.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    memos = crud.get_memos(db, skip=skip, limit=limit, category=category)
    result = [memo_to_dict(memo) for memo in memos]
    
    # 存入缓存，过期时间 60 秒
    r.setex(cache_key, 60, json.dumps(result))
    
    return result

@app.post("/templates/", response_model=schemas.Template)
def create_template(template: schemas.TemplateCreate, db: Session = Depends(get_db)):
    db_template = crud.create_template(db=db, template=template)
    return template_to_dict(db_template)

@app.get("/templates/", response_model=List[schemas.Template])
def read_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    templates = crud.get_templates(db, skip=skip, limit=limit)
    return [template_to_dict(t) for t in templates]

@app.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    crud.delete_template(db, template_id)
    return {"ok": True}

@app.get("/memos/{memo_id}", response_model=schemas.Memo)
def read_memo(memo_id: int, db: Session = Depends(get_db)):
    db_memo = crud.get_memo(db, memo_id=memo_id)
    if db_memo is None:
        raise HTTPException(status_code=404, detail="Memo not found")
    return memo_to_dict(db_memo)

@app.put("/memos/{memo_id}", response_model=schemas.Memo)
def update_memo(memo_id: int, memo: schemas.MemoUpdate, db: Session = Depends(get_db)):
    db_memo = crud.update_memo(db, memo_id, memo)
    if db_memo is None:
        raise HTTPException(status_code=404, detail="Memo not found")
    # 清除列表缓存
    # 这里应该清除所有相关缓存，简单起见我们使用模式匹配删除或简单处理
    keys = r.keys("memos_list_*")
    if keys:
        r.delete(*keys)
    return memo_to_dict(db_memo)

@app.patch("/memos/{memo_id}/status", response_model=schemas.Memo)
def update_memo_status(memo_id: int, is_completed: bool = Body(..., embed=True), db: Session = Depends(get_db)):
    db_memo = crud.update_memo_status(db, memo_id, is_completed)
    if db_memo is None:
        raise HTTPException(status_code=404, detail="Memo not found")
    
    # Check if the update was blocked (user requested complete but it's still incomplete)
    if is_completed and db_memo.completed_at is None:
         raise HTTPException(status_code=400, detail="Cannot complete memo with incomplete subtasks")

    # 清除缓存
    keys = r.keys("memos_list_*")
    if keys:
        r.delete(*keys)
        
    return memo_to_dict(db_memo)

@app.get("/memos/{memo_id}/stats")
def get_memo_stats(memo_id: int, db: Session = Depends(get_db)):
    db_memo = crud.get_memo(db, memo_id)
    if not db_memo:
        raise HTTPException(status_code=404, detail="Memo not found")
    
    if not db_memo.subtasks:
        return []
        
    # Filter completed subtasks and sort by completion time
    completed_subtasks = [st for st in db_memo.subtasks if st.is_completed and st.completed_at]
    completed_subtasks.sort(key=lambda x: x.completed_at)
    
    stats = []
    
    for st in completed_subtasks:
        # Ensure timezone consistency
        # Use subtask's created_at as start time if available, otherwise use memo's created_at or some fallback
        # Ideally, we should use st.created_at because user can edit "start time" which maps to created_at
        start = st.created_at
        end = st.completed_at
        
        # If start is missing (shouldn't happen for new ones), fallback to memo creation
        if not start:
            start = db_memo.created_at

        # If one is aware and other is naive, make both aware (or naive)
        if start.tzinfo is None and end.tzinfo is not None:
            start = start.replace(tzinfo=end.tzinfo) # Assume same TZ if naive
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

@app.delete("/memos/{memo_id}", response_model=schemas.Memo)
def delete_memo(memo_id: int, db: Session = Depends(get_db)):
    db_memo = crud.delete_memo(db, memo_id)
    if db_memo is None:
        raise HTTPException(status_code=404, detail="Memo not found")
    # 清除列表缓存
    keys = r.keys("memos_list_*")
    if keys:
        r.delete(*keys)
    return memo_to_dict(db_memo)
