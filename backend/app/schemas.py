from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class SubTaskBase(BaseModel):
    content: str
    note: Optional[str] = None
    is_completed: bool = False
    order: int = 0

class SubTaskCreate(SubTaskBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    pass

class SubTask(SubTaskBase):
    id: int
    memo_id: int
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MemoBase(BaseModel):
    title: str
    content: str
    category: str = "work"
    deadline: Optional[datetime] = None

class MemoCreate(MemoBase):
    subtasks: List[SubTaskCreate] = []

class MemoUpdate(MemoBase):
    title: Optional[str] = None
    content: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    subtasks: Optional[List[SubTaskCreate]] = None

class Memo(MemoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    subtasks: List[SubTask] = []
    category: str

    class Config:
        from_attributes = True

class TemplateSubTaskBase(BaseModel):
    content: str
    order: int = 0

class TemplateSubTaskCreate(TemplateSubTaskBase):
    pass

class TemplateSubTask(TemplateSubTaskBase):
    id: int
    template_id: int

    class Config:
        from_attributes = True

class TemplateBase(BaseModel):
    title: str
    content: str
    category: str = "work"

class TemplateCreate(TemplateBase):
    subtasks: List[TemplateSubTaskCreate] = []

class Template(TemplateBase):
    id: int
    created_at: datetime
    subtasks: List[TemplateSubTask] = []

    class Config:
        from_attributes = True
