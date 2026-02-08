from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
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
    
    # Store subtasks as a JSON string or simplified relationship?
    # For simplicity, let's use a relationship similar to Memo, but TemplateSubTask
    # OR simpler: just store content in Text field if simple, but we need subtasks.
    # Let's use a separate table for TemplateSubTasks to keep structure clean
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
