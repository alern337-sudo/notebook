from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Memo(Base):
    __tablename__ = "memos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    category = Column(String(50), default="work") # work, life

    subtasks = relationship("SubTask", back_populates="memo", cascade="all, delete-orphan")

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    content = Column(Text)
    category = Column(String(50), default="work")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    subtasks = relationship("TemplateSubTask", back_populates="template", cascade="all, delete-orphan")

class TemplateSubTask(Base):
    __tablename__ = "template_subtasks"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(255))
    order = Column(Integer, default=0)
    template_id = Column(Integer, ForeignKey("templates.id"))
    
    template = relationship("Template", back_populates="subtasks")

class SubTask(Base):
    __tablename__ = "subtasks"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(255))
    note = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    start_time = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    memo_id = Column(Integer, ForeignKey("memos.id"))

    memo = relationship("Memo", back_populates="subtasks")
    attachments = relationship("SubtaskAttachment", back_populates="subtask", cascade="all, delete-orphan")

class SubtaskAttachment(Base):
    __tablename__ = "subtask_attachments"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    file_path = Column(String(512))
    file_size = Column(Integer)
    content_type = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    subtask_id = Column(Integer, ForeignKey("subtasks.id"))

    subtask = relationship("SubTask", back_populates="attachments")

class Consumable(Base):
    __tablename__ = "consumables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    tag = Column(String(50), default="耗材") # 耗材, 食物
    category = Column(String(50), default="家") # 家, 车, 其他
    model_spec = Column(String(255), nullable=True) # 规格型号
    status = Column(String(50), default="正常") # 正常, 即将到期, 已过期 (can be computed but storing for cache/override)
    last_replaced = Column(DateTime(timezone=True), nullable=True)
    lifespan = Column(Integer, default=30) # days
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    mileage = Column(Integer, nullable=True) # for Car category (Last Replaced Mileage)
    current_mileage = Column(Integer, nullable=True, default=0) # Latest known mileage
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    logs = relationship("ConsumableLog", back_populates="consumable", cascade="all, delete-orphan")

class ConsumableLog(Base):
    __tablename__ = "consumable_logs"

    id = Column(Integer, primary_key=True, index=True)
    consumable_id = Column(Integer, ForeignKey("consumables.id"))
    replaced_at = Column(DateTime(timezone=True), nullable=False)
    mileage = Column(Integer, nullable=True)
    days_since_last = Column(Integer, default=0)
    km_since_last = Column(Integer, default=0)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    consumable = relationship("Consumable", back_populates="logs")
