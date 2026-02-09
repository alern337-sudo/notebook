from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta, date
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
    if memo.created_at:
        db_memo.created_at = memo.created_at
    if memo.completed_at:
        db_memo.completed_at = memo.completed_at
        
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

def update_memo(db: Session, memo_id: int, memo: schemas.MemoUpdate):
    db_memo = get_memo(db, memo_id)
    if not db_memo:
        return None
    
    if memo.title is not None:
        db_memo.title = memo.title
    if memo.content is not None:
        db_memo.content = memo.content
    if memo.created_at is not None:
        db_memo.created_at = memo.created_at
    if memo.completed_at is not None:
        db_memo.completed_at = memo.completed_at
    if memo.deadline is not None:
        dt = memo.deadline
        if dt.tzinfo is not None:
            dt = dt.astimezone(CN_TZ)
        db_memo.deadline = dt.replace(tzinfo=None)
        
    # Handle subtasks update if provided
    if memo.subtasks is not None:
        # Map existing subtasks by ID
        existing_subtasks = {st.id: st for st in db_memo.subtasks}
        new_subtasks_list = []
        
        for index, st_data in enumerate(memo.subtasks):
            # If ID exists and is in current subtasks, update it
            if st_data.id and st_data.id in existing_subtasks:
                st = existing_subtasks[st_data.id]
                st.content = st_data.content
                st.is_completed = st_data.is_completed
                st.order = index
                if st_data.created_at: st.created_at = st_data.created_at
                st.start_time = st_data.start_time
                st.completed_at = st_data.completed_at
                if st_data.note is not None: st.note = st_data.note
                new_subtasks_list.append(st)
            else:
                # Create new subtask
                # Exclude id from dict to let DB assign it (though SubTaskCreate has id=None default)
                st_dict = st_data.dict(exclude={'id'})
                st_dict['order'] = index
                new_st = models.SubTask(**st_dict, memo_id=db_memo.id)
                new_subtasks_list.append(new_st)
        
        # Assigning the list will trigger SQLAlchemy to delete orphans (those not in new_subtasks_list)
        # because cascade="all, delete-orphan" is set on the relationship.
        db_memo.subtasks = new_subtasks_list

    db.commit()
    db.refresh(db_memo)
    return db_memo

def delete_memo(db: Session, memo_id: int):
    db_memo = get_memo(db, memo_id)
    if db_memo:
        db.delete(db_memo)
        db.commit()
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

# Consumables CRUD
def get_consumables(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Consumable).order_by(models.Consumable.status == '已过期', models.Consumable.status == '即将到期', models.Consumable.status == '正常').offset(skip).limit(limit).all()

def get_consumable(db: Session, consumable_id: int):
    return db.query(models.Consumable).filter(models.Consumable.id == consumable_id).first()

def create_consumable(db: Session, consumable: schemas.ConsumableCreate):
    db_consumable = models.Consumable(**consumable.dict())
    if db_consumable.mileage is not None and db_consumable.current_mileage is None:
        db_consumable.current_mileage = db_consumable.mileage
    db.add(db_consumable)
    db.commit()
    db.refresh(db_consumable)
    return db_consumable

def update_subtask_status(db: Session, subtask_id: int, is_completed: bool):
    subtask = db.query(models.SubTask).filter(models.SubTask.id == subtask_id).first()
    if not subtask:
        return None
    
    subtask.is_completed = is_completed
    if is_completed:
        subtask.completed_at = datetime.now()
    else:
        subtask.completed_at = None
        
    db.commit()
    db.refresh(subtask)
    
    # Update parent memo completion status
    memo = db.query(models.Memo).filter(models.Memo.id == subtask.memo_id).first()
    if memo:
        _sync_memo_status(db, memo)
        db.commit()
        
    return subtask

def update_subtask(db: Session, subtask_id: int, subtask_update: schemas.SubTaskUpdate):
    db_subtask = db.query(models.SubTask).filter(models.SubTask.id == subtask_id).first()
    if not db_subtask:
        return None
    
    update_data = subtask_update.dict(exclude_unset=True)
    
    # Handle timezones if present
    if 'start_time' in update_data and update_data['start_time']:
         dt = update_data['start_time']
         if dt.tzinfo is not None:
             dt = dt.astimezone(CN_TZ)
         update_data['start_time'] = dt.replace(tzinfo=None)
         
    if 'completed_at' in update_data and update_data['completed_at']:
         dt = update_data['completed_at']
         if dt.tzinfo is not None:
             dt = dt.astimezone(CN_TZ)
         update_data['completed_at'] = dt.replace(tzinfo=None)

    for key, value in update_data.items():
        setattr(db_subtask, key, value)
        
    db.commit()
    db.refresh(db_subtask)
    
    # Update parent memo completion status if completion status or time changed
    memo = db.query(models.Memo).filter(models.Memo.id == db_subtask.memo_id).first()
    if memo:
        _sync_memo_status(db, memo)
        db.commit()
        
    return db_subtask

def create_subtask_attachment(db: Session, attachment: schemas.SubtaskAttachmentCreate, subtask_id: int):
    db_attachment = models.SubtaskAttachment(**attachment.dict(), subtask_id=subtask_id)
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

def update_subtask_attachment(db: Session, attachment_id: int, attachment: schemas.SubtaskAttachmentUpdate):
    db_attachment = get_subtask_attachment(db, attachment_id)
    if not db_attachment:
        return None
    
    if attachment.filename:
        db_attachment.filename = attachment.filename
        
    db.commit()
    db.refresh(db_attachment)
    return db_attachment

def update_consumable(db: Session, consumable_id: int, consumable: schemas.ConsumableUpdate):
    db_consumable = get_consumable(db, consumable_id)
    if not db_consumable:
        return None
    
    for key, value in consumable.dict(exclude_unset=True).items():
        setattr(db_consumable, key, value)
        
    db.commit()
    db.refresh(db_consumable)
    return db_consumable

def delete_consumable(db: Session, consumable_id: int):
    db_consumable = get_consumable(db, consumable_id)
    if db_consumable:
        db.delete(db_consumable)
        db.commit()
    return db_consumable

def replace_consumable(db: Session, consumable_id: int, replaced_at: datetime.date, mileage: int = None, note: str = None):
    db_consumable = get_consumable(db, consumable_id)
    if not db_consumable:
        return None
    
    # Calculate diffs
    days_since = 0
    if db_consumable.last_replaced:
        days_since = (replaced_at - db_consumable.last_replaced).days
        
    km_since = 0
    if mileage is not None and db_consumable.mileage is not None:
        km_since = mileage - db_consumable.mileage
        if km_since < 0: km_since = 0 # Should not happen if input validated
        
    # Create Log
    log = models.ConsumableLog(
        consumable_id=consumable_id,
        replaced_at=replaced_at,
        mileage=mileage,
        days_since_last=days_since,
        km_since_last=km_since,
        note=note
    )
    db.add(log)
    
    # Update Consumable
    db_consumable.last_replaced = replaced_at
    if mileage is not None:
        db_consumable.mileage = mileage
        db_consumable.current_mileage = mileage
    
    # Reset status to normal? Or let user/logic handle it. Usually replacing makes it 'Normal'
    db_consumable.status = '正常'
    
    db.commit()
    db.refresh(db_consumable)
    return db_consumable
