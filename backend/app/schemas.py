from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List

class SubTaskBase(BaseModel):
    content: str
    note: Optional[str] = None
    is_completed: bool = False
    order: int = 0

class SubtaskAttachmentBase(BaseModel):
    filename: str
    file_size: int
    content_type: str

class SubtaskAttachmentCreate(SubtaskAttachmentBase):
    file_path: str

class SubtaskAttachment(SubtaskAttachmentBase):
    id: int
    created_at: datetime
    subtask_id: int

    class Config:
        from_attributes = True

class SubtaskAttachmentUpdate(BaseModel):
    filename: str

class SubTaskCreate(SubTaskBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    start_time: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    pass

class SubTaskUpdate(BaseModel):
    content: Optional[str] = None
    is_completed: Optional[bool] = None
    start_time: Optional[datetime] = None


class SubTask(SubTaskBase):
    id: int
    memo_id: int
    created_at: Optional[datetime] = None
    start_time: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    attachments: List[SubtaskAttachment] = []

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

# Consumables
class ConsumableLogBase(BaseModel):
    replaced_at: datetime
    mileage: Optional[int] = None
    days_since_last: int = 0
    km_since_last: int = 0
    note: Optional[str] = None

class ConsumableLogCreate(ConsumableLogBase):
    pass

class ConsumableLog(ConsumableLogBase):
    id: int
    consumable_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ConsumableBase(BaseModel):
    name: str
    tag: str = "耗材"
    category: str = "家"
    model_spec: Optional[str] = None
    status: str = "正常"
    last_replaced: Optional[datetime] = None
    lifespan: int = 30
    expiry_date: Optional[datetime] = None
    mileage: Optional[int] = None
    current_mileage: Optional[int] = None

class ConsumableCreate(ConsumableBase):
    pass

class ConsumableUpdate(ConsumableBase):
    pass

class Consumable(ConsumableBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    logs: List[ConsumableLog] = []

    class Config:
        from_attributes = True
