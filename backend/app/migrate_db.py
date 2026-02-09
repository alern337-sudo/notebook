
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:12345678@localhost/memo_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

def migrate():
    with engine.connect() as conn:
        try:
            # Check if column exists
            conn.execute(text("SELECT current_mileage FROM consumables LIMIT 1"))
            print("Column 'current_mileage' already exists.")
        except OperationalError:
            # Add column if not exists
            print("Adding column 'current_mileage'...")
            conn.execute(text("ALTER TABLE consumables ADD COLUMN current_mileage INTEGER DEFAULT 0"))
            print("Column added.")
            
            # Initialize current_mileage with mileage (assuming mileage was current/last known)
            conn.execute(text("UPDATE consumables SET current_mileage = mileage WHERE mileage IS NOT NULL"))
            print("Initialized current_mileage.")

if __name__ == "__main__":
    migrate()
