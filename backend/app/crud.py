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

def update_memo(db: Session, memo_id: int, memo: schemas.MemoUpdate):
    db_memo = get_memo(db, memo_id)
    if db_memo:
        update_data = memo.dict(exclude_unset=True)
        
        # Handle subtasks separately
        if "subtasks" in update_data:
            subtasks_data = update_data.pop("subtasks")
            
            # Reconcile subtasks to preserve created_at/completed_at
            existing_subtasks = {st.id: st for st in db_memo.subtasks}
            current_ids = set()
            
            for index, st_data in enumerate(subtasks_data):
                st_id = st_data.get("id")
                # Update order based on list position
                st_data['order'] = index
                
                if st_id and st_id in existing_subtasks:
                    # Update existing
                    existing_st = existing_subtasks[st_id]
                    existing_st.order = index # Explicitly update order
                    if "content" in st_data:
                        existing_st.content = st_data["content"]
                    if "note" in st_data:
                        existing_st.note = st_data["note"]
                    if "is_completed" in st_data:
                        # If status changes, update completed_at only if completed_at is not explicitly provided
                        if st_data["is_completed"] and not existing_st.is_completed and "completed_at" not in st_data:
                            existing_st.completed_at = datetime.now()
                        elif not st_data["is_completed"] and "completed_at" not in st_data:
                            existing_st.completed_at = None
                        existing_st.is_completed = st_data["is_completed"]
                    
                    if "created_at" in st_data:
                        dt = st_data["created_at"]
                        if dt and dt.tzinfo is not None:
                            dt = dt.astimezone(CN_TZ)
                        existing_st.created_at = dt.replace(tzinfo=None) if dt else None

                    if "completed_at" in st_data:
                        dt = st_data["completed_at"]
                        if dt and dt.tzinfo is not None:
                            dt = dt.astimezone(CN_TZ)
                        existing_st.completed_at = dt.replace(tzinfo=None) if dt else None

                    current_ids.add(st_id)
                else:
                    # Create new
                    # Remove id if present but invalid (e.g. None or not in DB)
                    if "id" in st_data:
                        del st_data["id"]
                    
                    # Handle completed_at for new items if they are created as completed
                    if st_data.get("is_completed") and "completed_at" not in st_data:
                        st_data["completed_at"] = datetime.now(CN_TZ).replace(tzinfo=None)
                    
                    # Handle explicitly provided times
                    if "created_at" in st_data:
                         dt = st_data["created_at"]
                         if dt and dt.tzinfo is not None:
                             dt = dt.astimezone(CN_TZ)
                         st_data["created_at"] = dt.replace(tzinfo=None) if dt else None
                    
                    if "completed_at" in st_data:
                         dt = st_data["completed_at"]
                         if dt and dt.tzinfo is not None:
                             dt = dt.astimezone(CN_TZ)
                         st_data["completed_at"] = dt.replace(tzinfo=None) if dt else None

                    db_subtask = models.SubTask(**st_data, memo_id=memo_id)
                    db.add(db_subtask)
            
            # Delete removed subtasks
            for st_id, st in existing_subtasks.items():
                if st_id not in current_ids:
                    db.delete(st)

        for key, value in update_data.items():
            if key == "completed_at" and value is not None:
                 # Handle timezone
                dt = value
                if dt.tzinfo is not None:
                    dt = dt.astimezone(CN_TZ)
                setattr(db_memo, key, dt.replace(tzinfo=None))
            elif key == "completed_at" and value is None:
                 # Explicitly clearing completion time
                 setattr(db_memo, key, None)
            elif key == "created_at" and value is not None:
                 # Handle timezone for created_at
                dt = value
                if dt.tzinfo is not None:
                    dt = dt.astimezone(CN_TZ)
                setattr(db_memo, key, dt.replace(tzinfo=None))
            elif key == "deadline" and value is not None:
                 # Handle timezone for deadline
                dt = value
                if dt.tzinfo is not None:
                    dt = dt.astimezone(CN_TZ)
                setattr(db_memo, key, dt.replace(tzinfo=None))
            else:
                setattr(db_memo, key, value)
        
        # Enforce rule: If subtasks exist, completion status depends on them
        _sync_memo_status(db, db_memo)

        db.commit()
        db.refresh(db_memo)
    return db_memo

def update_subtask_status(db: Session, subtask_id: int, is_completed: bool):
    subtask = db.query(models.SubTask).filter(models.SubTask.id == subtask_id).first()
    if subtask:
        subtask.is_completed = is_completed
        if is_completed:
            subtask.completed_at = datetime.now()
        else:
            subtask.completed_at = None
            
        # Check parent memo
        if subtask.memo:
            _sync_memo_status(db, subtask.memo)
            
        db.commit()
        db.refresh(subtask)
    return subtask

def reorder_subtasks(db: Session, memo_id: int, subtask_ids: list[int]):
    # Verify all subtasks belong to the memo
    subtasks = db.query(models.SubTask).filter(models.SubTask.memo_id == memo_id).all()
    subtask_map = {st.id: st for st in subtasks}
    
    for index, st_id in enumerate(subtask_ids):
        if st_id in subtask_map:
            subtask_map[st_id].order = index
            
    db.commit()
    return True

def delete_memo(db: Session, memo_id: int):
    db_memo = get_memo(db, memo_id)
    if db_memo:
        db.delete(db_memo)
        db.commit()
    return db_memo

def update_memo_status(db: Session, memo_id: int, is_completed: bool):
    db_memo = get_memo(db, memo_id)
    if db_memo:
        if is_completed:
            # Check subtasks
            if db_memo.subtasks and any(not st.is_completed for st in db_memo.subtasks):
                # Cannot complete if subtasks are incomplete
                # We can return a special value or just not update. 
                # Let's return False to indicate failure/blocking?
                # But the return type is usually the object.
                # Let's handle this in main.py by checking before calling? 
                # Or raise exception here?
                # For simplicity, let's just NOT update and return the memo as is (which is incomplete).
                # But the caller needs to know.
                pass
            else:
                 # If no subtasks or all completed, update time.
                 # If subtasks exist, use the latest time.
                 if db_memo.subtasks:
                     latest = None
                     for st in db_memo.subtasks:
                         if st.completed_at:
                             if latest is None or st.completed_at > latest:
                                 latest = st.completed_at
                     db_memo.completed_at = latest or datetime.now()
                 else:
                     db_memo.completed_at = datetime.now()
        else:
            db_memo.completed_at = None
            
        db.commit()
        db.refresh(db_memo)
    return db_memo
