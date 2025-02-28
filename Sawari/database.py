from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import time

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine=create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base=declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


#while True:
#   try:
#     onn=psycopg2.connect(host="localhost",database='Sawari',user='postgres',password='siddiqui123',cursor_factory=RealDictCursor)
#     cursor=conn.cursor()
#     print("Connected to database successfully")
#     break    
#   except Exception as Error:
#     print("Connection to database failed")
#     print("Error:",Error)
#     time.sleep(2)

