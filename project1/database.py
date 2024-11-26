from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
db_config = {
    'user': 'root',
    'password': '12345678',
    'host': 'localhost',
    'database': 'hospital_management'
}

engine = create_engine(db_config)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(255))
    appointment_date = Column(Date)
    time_slot = Column(String(50))
    service = Column(String(50))
    doctor_name = Column(String(50))