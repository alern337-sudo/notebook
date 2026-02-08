from sqlalchemy import create_engine, text
from app.database import SQLALCHEMY_DATABASE_URL

def add_note_column():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE subtasks ADD COLUMN note TEXT"))
            print("Successfully added 'note' column to subtasks table")
        except Exception as e:
            print(f"Error adding column: {e}")

if __name__ == "__main__":
    add_note_column()
