import sqlalchemy
from sqlalchemy import create_engine, text

DATABASE_URL = "mysql+pymysql://root:12345678@localhost/memo_db"
engine = create_engine(DATABASE_URL)

def run_migrations():
    with engine.connect() as conn:
        # Add category column to memos
        try:
            conn.execute(text("ALTER TABLE memos ADD COLUMN category VARCHAR(50) DEFAULT 'work'"))
            print("Added category column to memos")
        except Exception as e:
            print(f"Error adding category to memos (might exist): {e}")

        # Create templates table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS templates (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255),
                    content TEXT,
                    category VARCHAR(50) DEFAULT 'work',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX (id)
                )
            """))
            print("Created templates table")
        except Exception as e:
             print(f"Error creating templates table: {e}")

        # Create template_subtasks table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS template_subtasks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    content VARCHAR(255),
                    `order` INT DEFAULT 0,
                    template_id INT,
                    FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE,
                    INDEX (id)
                )
            """))
            print("Created template_subtasks table")
        except Exception as e:
             print(f"Error creating template_subtasks table: {e}")

if __name__ == "__main__":
    run_migrations()
