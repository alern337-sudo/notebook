from sqlalchemy import create_engine, text
from app.database import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def add_columns():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE subtasks ADD COLUMN created_at DATETIME"))
            print("Added created_at")
        except Exception as e:
            print(f"Error adding created_at: {e}")
            
        try:
            conn.execute(text("ALTER TABLE subtasks ADD COLUMN completed_at DATETIME"))
            print("Added completed_at")
        except Exception as e:
            print(f"Error adding completed_at: {e}")

if __name__ == "__main__":
    add_columns()
