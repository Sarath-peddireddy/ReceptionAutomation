import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///clinic_scheduling.db')
    
    NEW_PATIENT_SLOT_DURATION = 60
    RETURNING_PATIENT_SLOT_DURATION = 30
    
    CLINIC_NAME = "HealthCare Plus Clinic"
    CLINIC_ADDRESS = "123 Medical Drive, Health City, HC 12345"
    CLINIC_PHONE = "(555) 123-4567"

