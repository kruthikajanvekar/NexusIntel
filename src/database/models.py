
from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import json

Base = declarative_base()
# Using SQLite for local persistence as it's lightweight and internal
engine = create_engine('sqlite:///nexus_intel.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class IntelRecord(Base):
    __tablename__ = "intelligence_records"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    website = Column(String)
    summary = Column(Text)
    emails = Column(Text)         # Stored as JSON Array
    phone_numbers = Column(Text)  # Stored as JSON Array
    socials = Column(Text)        # Stored as JSON Array of Objects
    addresses = Column(Text)      # Stored as JSON Array
    notes = Column(Text)          # Added field
    sources = Column(Text)        # Stored as JSON Array
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class UserLog(Base):
    __tablename__ = "user_logs"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    password = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

def save_intel(data):
    db = SessionLocal()
    try:
        record = IntelRecord(
            company_name=data.get('company_name'),
            website=data.get('website'),
            summary=data.get('summary'),
            emails=json.dumps(data.get('emails', [])),
            phone_numbers=json.dumps(data.get('phone_numbers', [])),
            socials=json.dumps(data.get('socials', [])),
            addresses=json.dumps(data.get('addresses', [])),
            notes=data.get('notes', ''),
            sources=json.dumps(data.get('sources', []))
        )
        db.add(record)
        db.commit()
    finally:
        db.close()

def get_history():
    db = SessionLocal()
    try:
        return db.query(IntelRecord).order_by(IntelRecord.timestamp.desc()).all()
    finally:
        db.close()

def delete_history_item(item_id: int):
    db = SessionLocal()
    try:
        db.query(IntelRecord).filter(IntelRecord.id == item_id).delete()
        db.commit()
    finally:
        db.close()
