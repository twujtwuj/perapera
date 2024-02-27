from sqlalchemy import create_engine  # database type, path, and name
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine("sqlite:///perapera.db")  # databse engine; sits within the application

Base = declarative_base()  # class to access database

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
