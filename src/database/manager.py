
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, IntelRecord, UserLog

class DatabaseManager:
    """
    Object-Oriented Database Manager for handling Intelligence records and User logs.
    """
    def __init__(self, db_url: str = "sqlite:///nexus_intel.db"):
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def save_record(self, data: dict):
        with self.SessionLocal() as session:
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
            session.add(record)
            session.commit()
            return record.id

    def log_user(self, email: str, password: str):
        with self.SessionLocal() as session:
            log = UserLog(email=email, password=password)
            session.add(log)
            session.commit()
            return log.id

    def get_all_records(self):
        with self.SessionLocal() as session:
            return session.query(IntelRecord).order_by(IntelRecord.timestamp.desc()).all()

    def delete_record(self, record_id: int):
        with self.SessionLocal() as session:
            session.query(IntelRecord).filter(IntelRecord.id == record_id).delete()
            session.commit()
