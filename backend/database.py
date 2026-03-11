from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv
import os

load_dotenv()  # reads your .env file

DATABASE_URL = os.getenv("DATABASE_URL")

# The engine is your app's connection to the database
engine = create_engine(DATABASE_URL, echo=True)  
# echo=True means every SQL query prints to terminal - great for learning

def get_session():
    # This is a "dependency" - FastAPI will call this automatically
    # to give each request its own database session, then close it cleanly
    with Session(engine) as session:
        yield session

def create_db_tables():
    # Creates all tables in the DB if they don't exist yet
    SQLModel.metadata.create_all(engine)