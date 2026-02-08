from sqlalchemy import create_engine, text
from app.database import SQLALCHEMY_DATABASE_URL

def add_order_column():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as conn:
        try:
            # Using backticks for MySQL reserved word `order`
            conn.execute(text("ALTER TABLE subtasks ADD COLUMN `order` INTEGER DEFAULT 0"))
            print("Successfully added 'order' column to subtasks table")
        except Exception as e:
            print(f"Error adding column: {e}")

if __name__ == "__main__":
    add_order_column()
