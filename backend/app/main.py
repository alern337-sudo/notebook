from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, crud
from .database import SessionLocal, engine
import redis
import json

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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
    r.delete("memos_list")
    return db_memo

@app.get("/memos/", response_model=List[schemas.Memo])
def read_memos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # 尝试从 Redis 获取
    cache_key = f"memos_list_{skip}_{limit}"
    cached_memos = r.get(cache_key)
    if cached_memos:
        return json.loads(cached_memos)
    
    memos = crud.get_memos(db, skip=skip, limit=limit)
    # 存入 Redis，过期时间 60 秒
    # 注意：这里简单序列化，实际上 Pydantic 模型需要 dict()
    # 重新构造为 list of dict 以便 json 序列化
    memos_json = [
        {
            "id": m.id,
            "title": m.title,
            "content": m.content,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "updated_at": m.updated_at.isoformat() if m.updated_at else None
        }
        for m in memos
    ]
    r.setex(cache_key, 60, json.dumps(memos_json))
    return memos

@app.get("/memos/{memo_id}", response_model=schemas.Memo)
def read_memo(memo_id: int, db: Session = Depends(get_db)):
    db_memo = crud.get_memo(db, memo_id=memo_id)
    if db_memo is None:
        raise HTTPException(status_code=404, detail="Memo not found")
    return db_memo

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
    return db_memo

@app.delete("/memos/{memo_id}", response_model=schemas.Memo)
def delete_memo(memo_id: int, db: Session = Depends(get_db)):
    db_memo = crud.delete_memo(db, memo_id)
    if db_memo is None:
        raise HTTPException(status_code=404, detail="Memo not found")
    # 清除列表缓存
    keys = r.keys("memos_list_*")
    if keys:
        r.delete(*keys)
    return db_memo
