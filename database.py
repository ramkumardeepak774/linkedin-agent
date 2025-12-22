from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from config import Config

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    platform_job_id = Column(String, unique=True) # LinkedIn Job ID
    title = Column(String)
    company = Column(String)
    location = Column(String)
    description = Column(Text)
    url = Column(String)
    
    # Intelligence
    fit_score = Column(Float) # 0.0 to 1.0
    fit_reason = Column(Text)
    
    # Status
    status = Column(String, default="found") # found, applied, rejected, interviewed, offered
    created_at = Column(DateTime, default=datetime.utcnow)
    
    applications = relationship("Application", back_populates="job")

class Application(Base):
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    
    resume_version = Column(String)
    cover_letter_content = Column(Text)
    
    applied_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="submitted")
    
    job = relationship("Job", back_populates="applications")

class Outreach(Base):
    __tablename__ = 'outreach'
    
    id = Column(Integer, primary_key=True)
    person_name = Column(String)
    person_role = Column(String) # Recruiter, CEO
    company = Column(String)
    
    contact_method = Column(String) # LinkedIn, Email
    contact_info = Column(String) # Email address or Profile URL
    
    message_content = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)
    reply_received = Column(Boolean, default=False)

def init_db():
    engine = create_engine(f"sqlite:///{Config.DB_PATH}")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {Config.DB_PATH}")
