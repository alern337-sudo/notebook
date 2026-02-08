from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from . import models, schemas

CN_TZ = timezone(timedelta(hours=8))

def _sync_memo_status(db: Session, memo: models.Memo):
    """
    Updates memo completion status based on subtasks.
    If subtasks exist:
    - All completed -> Memo completed (time = max subtask completion time)
    - Any incomplete -> Memo active (completed_at = None)
    """
    # Flush to ensure subtask changes are in DB (but not committed yet)
    db.flush()
    
    # Query subtasks directly to get the latest state
    subtasks = db.query(models.SubTask).filter(models.SubTask.memo_id == memo.id).all()
    
    if not subtasks:
        return

    all_done = all(st.is_completed for st in subtasks)
    
    if all_done:
        # Find the latest completion time
        latest = None
        for st in subtasks:
            if st.completed_at:
                # Ensure we are comparing aware/naive consistently if needed, 
                # but DB returns consistent types usually.
                if latest is None or st.completed_at > latest:
                    latest = st.completed_at
        
        # If strictly all are completed but some lack timestamp, use now
        memo.completed_at = latest or datetime.now()
    else:
        memo.completed_at = None

def get_memo(db: Session, memo_id: int):
    return db.query(models.Memo).filter(models.Memo.id == memo_id).first()

def get_memos(db: Session, skip: int = 0, limit: int = 100, category: str = None):
    query = db.query(models.Memo)
    if category and category != 'all':
        query = query.filter(models.Memo.category == category)
    
    # Sort by deadline: non-nulls first (asc), then nulls
    query = query.order_by(models.Memo.deadline.is_(None), models.Memo.deadline.asc())
    
    return query.offset(skip).limit(limit).all()

def create_memo(db: Session, memo: schemas.MemoCreate):
    db_memo = models.Memo(
        title=memo.title, 
        content=memo.content,
        category=memo.category
    )
    if memo.deadline:
        dt = memo.deadline
        if dt.tzinfo is not None:
            dt = dt.astimezone(CN_TZ)
        db_memo.deadline = dt.replace(tzinfo=None)
        
    db.add(db_memo)
    db.flush() # Flush to get the ID
    
    for index, subtask in enumerate(memo.subtasks):
        subtask_data = subtask.dict()
        subtask_data['order'] = index
        db_subtask = models.SubTask(**subtask_data, memo_id=db_memo.id)
        db.add(db_subtask)
        
    db.commit()
    db.refresh(db_memo)
    return db_memo

def create_template(db: Session, template: schemas.TemplateCreate):
    db_template = models.Template(
        title=template.title,
        content=template.content,
        category=template.category
    )
    db.add(db_template)
    db.flush()
    
    for index, subtask in enumerate(template.subtasks):
        db_subtask = models.TemplateSubTask(
            content=subtask.content,
            order=index,
            template_id=db_template.id
        )
        db.add(db_subtask)
        
    db.commit()
    db.refresh(db_template)
    return db_template

def get_templates(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Template).offset(skip).limit(limit).all()

def delete_template(db: Session, template_id: int):
    db_template = db.query(models.Template).filter(models.Template.id == template_id).first()
    if db_template:
        db.delete(db_template)
        db.commit()
    return db_template

def create_subtask_attachment(db: Session, attachment_data: dict):
    db_attachment = models.SubtaskAttachment(**attachment_data)
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    return db_attachment

def get_subtask_attachment(db: Session, attachment_id: int):
    return db.query(models.SubtaskAttachment).filter(models.SubtaskAttachment.id == attachment_id).first()

def delete_subtask_attachment(db: Session, attachment_id: int):
    db_attachment = get_subtask_attachment(db, attachment_id)
    if db_attachment:
        db.delete(db_attachment)
        db.commit()
    return db_attachment

def update_subtask_attachment(db: Session, attachment_id: int, attachment_update: schemas.SubtaskAttachmentUpdate):
    db_attachment = get_subtask_attachment(db, attachment_id)
    if db_attachment:
        if attachment_update.filename:
            db_attachment.filename = attachment_update.filename
        db.commit()
        db.refresh(db_attachment)
    return db_attachment
