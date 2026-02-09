
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:12345678@localhost/memo_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

def migrate():
    with engine.connect() as conn:
        try:
            # Check if column exists
            conn.execute(text("SELECT start_time FROM subtasks LIMIT 1"))
            print("Column 'start_time' already exists.")
        except OperationalError:
            # Add column if not exists
            print("Adding column 'start_time'...")
            conn.execute(text("ALTER TABLE subtasks ADD COLUMN start_time DATETIME DEFAULT NULL"))
            print("Column added.")
            
            # Optional: Initialize start_time with created_at?
            # print("Initializing start_time with created_at...")
            # conn.execute(text("UPDATE subtasks SET start_time = created_at WHERE start_time IS NULL"))
            # print("Initialized start_time.")

if __name__ == "__main__":
    migrate()
