from sqlalchemy import create_engine, text
import datetime

engine = create_engine('mysql+pymysql://root:12345678@127.0.0.1/memo_db')
with engine.connect() as conn:
    result = conn.execute(text('SELECT id, created_at, updated_at, completed_at FROM memos')).fetchall()
    for row in result:
        print(f'ID: {row[0]}')
        print(f'  Created: {row[1]} (Type: {type(row[1])})')
        print(f'  Updated: {row[2]} (Type: {type(row[2])})')
        print(f'  Completed: {row[3]} (Type: {type(row[3])})')
