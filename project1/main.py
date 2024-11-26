# 
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
import base64
import qrcode
from io import BytesIO
import os
from dotenv import load_dotenv
from datetime import datetime
from fastapi import Request
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import logging
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# CORS Configuration
# origins = [
#     "http://localhost",
#     "http://localhost:5500",  # Example frontend URL
# ]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Model
class Patient(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(255))
    appointment_date = Column(Date)
    time_slot = Column(String(50))
    service = Column(String(50))
    doctor_name = Column(String(50))

# Create the database tables
Base.metadata.create_all(bind=engine)

# Pydantic Model
class PatientCreate(BaseModel):
    name: str
    phone: str
    email: str
    address: str
    dateInput: str
    service: str
    time_slot: str
    doctor_name: str
# class PatientCreate(BaseModel):
#     name: str
#     phone: str
#     email: str
#     address: str
#     # dateInput: str
#     appointment_date: str
#     time_slot: str
#     service: str
#     doctor_name: str

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# QR Code Generator
def generate_qr_code(patient_id: int) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"Patient ID: {patient_id}")
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered)  # Remove the 'format' argument
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     print(f"Request body: {await request.body()}")
#     print(f"Validation error: {exc.errors()}")
#     return JSONResponse(
#         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#         content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
#     )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    logging.error(f"RequestValidationError: body={body}")
    logging.error(f"RequestValidationError: errors={exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.post("/register")
async def register_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    try:
        # Parse the date directly from the frontend format (YYYY-MM-DD)
        appointment_date = datetime.strptime(patient.dateInput, "%Y-%m-%d").date()
        
        new_patient = Patient(
            name=patient.name,
            phone=patient.phone,
            email=patient.email,
            address=patient.address,
            appointment_date=appointment_date,
            time_slot=patient.time_slot,
            service=patient.service,
            doctor_name=patient.doctor_name
        )
        
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        qr_code = generate_qr_code(new_patient.id)
        return {"patient_id": new_patient.id, "qr_code": qr_code}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
# @app.post("/register")
# async def register_patient(patient: PatientCreate, db: Session = Depends(get_db)):
#     try:
#         # Parse the date directly from the frontend format (YYYY-MM-DD)
#         appointment_date = datetime.strptime(patient.dateInput, "%Y-%m-%d").date()
        
#         new_patient = Patient(
#             name=patient.name,
#             phone=patient.phone,
#             email=patient.email,
#             address=patient.address,
#             appointment_date=appointment_date,
#             time_slot=patient.time_slot,
#             service=patient.service,
#             doctor_name=patient.doctor_name
#         )
        
#         db.add(new_patient)
#         db.commit()
#         db.refresh(new_patient)
#         qr_code = generate_qr_code(new_patient.id)
#         return {"patient_id": new_patient.id, "qr_code": qr_code}
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
# @app.post("/register")
# async def register_patient(patient: PatientCreate, db: Session = Depends(get_db)):
#     try:
#         appointment_date = datetime.strptime(patient.appointment_date, "%d-%m-%Y").date()
#     # except ValueError as e:
#     #     raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

#         new_patient = Patient(
#             name=patient.name,
#             phone=patient.phone,
#             email=patient.email,
#             address=patient.address,
#         # appointment_date=patient.dateInput,
#             appointment_date= appointment_date,
#             time_slot=patient.time_slot,
#             service=patient.service,
#             doctor_name=patient.doctor_name
#         )
    
#     # try:
#         db.add(new_patient)
#         db.commit()
#         db.refresh(new_patient)
#         qr_code = generate_qr_code(new_patient.id)
#         return {"patient_id": new_patient.id, "qr_code": qr_code}
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)

