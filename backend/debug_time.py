from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, text

CN_TZ = timezone(timedelta(hours=8))

def to_cn_time(dt):
    """将时间转换为东八区时间字符串"""
    if dt is None:
        return None
    # 如果是 naive 时间（数据库读取），默认视为 UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    # 转换为东八区
    return dt.astimezone(CN_TZ).isoformat()

engine = create_engine('mysql+pymysql://root:12345678@127.0.0.1/memo_db')
with engine.connect() as conn:
    result = conn.execute(text('SELECT created_at, completed_at FROM memos WHERE id=4')).fetchone()
    if result:
        created_at, completed_at = result
        print(f"DB Created: {created_at} (type: {type(created_at)})")
        print(f"Converted Created: {to_cn_time(created_at)}")
        
        print(f"DB Completed: {completed_at} (type: {type(completed_at)})")
        print(f"Converted Completed: {to_cn_time(completed_at)}")
