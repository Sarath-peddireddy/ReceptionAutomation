import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import PatientDatabase

class PatientIntake:
    def __init__(self, db: PatientDatabase):
        self.db = db
        self.current_patient_data = {}
        self.required_fields = ['first_name', 'last_name', 'date_of_birth']
        self.optional_fields = ['phone', 'email', 'preferred_doctor']
    
    def validate_name(self, name: str) -> Tuple[bool, str]:
        if not name or len(name.strip()) < 2:
            return False, "Name must be at least 2 characters long"
        
        if not re.match(r'^[a-zA-Z\s\-\']+$', name.strip()):
            return False, "Name can only contain letters, spaces, hyphens, and apostrophes"
        
        return True, ""
    
    def validate_date_of_birth(self, dob: str) -> Tuple[bool, str]:
        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d')
            today = datetime.now()
            
            if dob_date > today:
                return False, "Date of birth cannot be in the future"
            
            age = (today - dob_date).days / 365.25
            if age < 0 or age > 120:
                return False, "Please enter a valid age (0-120 years)"
            
            return True, ""
        except ValueError:
            return False, "Please enter date in YYYY-MM-DD format"
    
    def validate_phone(self, phone: str) -> Tuple[bool, str]:
        if not phone:
            return True, ""
        
        phone_clean = re.sub(r'[^\d]', '', phone)
        if len(phone_clean) == 10:
            return True, ""
        elif len(phone_clean) == 11 and phone_clean.startswith('1'):
            return True, ""
        else:
            return False, "Please enter a valid 10-digit phone number"
    
    def validate_email(self, email: str) -> Tuple[bool, str]:
        if not email:
            return True, ""
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email):
            return True, ""
        else:
            return False, "Please enter a valid email address"
    
    def validate_doctor(self, doctor_name: str) -> Tuple[bool, str]:
        if not doctor_name:
            return True, ""
        
        doctors = self.db.get_doctors()
        doctor_names = [doc['name'] for doc in doctors]
        
        if doctor_name in doctor_names:
            return True, ""
        else:
            return False, f"Doctor not found. Available doctors: {', '.join(doctor_names)}"
    
    def collect_patient_info(self, user_input: str) -> Dict:
        response = {
            'status': 'continue',
            'message': '',
            'missing_fields': [],
            'patient_data': self.current_patient_data.copy()
        }
        
        user_input = user_input.strip().lower()
        
        if 'first name' in user_input or 'firstname' in user_input:
            response['message'] = "Please provide your first name:"
            response['waiting_for'] = 'first_name'
        elif 'last name' in user_input or 'lastname' in user_input:
            response['message'] = "Please provide your last name:"
            response['waiting_for'] = 'last_name'
        elif 'date of birth' in user_input or 'dob' in user_input or 'birthday' in user_input:
            response['message'] = "Please provide your date of birth (YYYY-MM-DD format):"
            response['waiting_for'] = 'date_of_birth'
        elif 'phone' in user_input:
            response['message'] = "Please provide your phone number (optional):"
            response['waiting_for'] = 'phone'
        elif 'email' in user_input:
            response['message'] = "Please provide your email address (optional):"
            response['waiting_for'] = 'email'
        elif 'doctor' in user_input:
            doctors = self.db.get_doctors()
            doctor_list = "\n".join([f"- {doc['name']} ({doc['specialty']}) - {doc['location']}" for doc in doctors])
            response['message'] = f"Please select your preferred doctor (optional):\n{doctor_list}"
            response['waiting_for'] = 'preferred_doctor'
        else:
            response['message'] = "I can help you with:\n- First name\n- Last name\n- Date of birth\n- Phone number\n- Email address\n- Preferred doctor\n\nWhat would you like to provide?"
        
        return response
    
    def process_field_input(self, field: str, value: str) -> Dict:
        response = {
            'status': 'continue',
            'message': '',
            'patient_data': self.current_patient_data.copy()
        }
        
        if field == 'first_name':
            is_valid, error_msg = self.validate_name(value)
            if is_valid:
                self.current_patient_data['first_name'] = value.strip().title()
                response['message'] = f"Thank you, {value.strip().title()}. What's your last name?"
            else:
                response['message'] = f"Invalid first name: {error_msg}. Please try again."
        
        elif field == 'last_name':
            is_valid, error_msg = self.validate_name(value)
            if is_valid:
                self.current_patient_data['last_name'] = value.strip().title()
                response['message'] = "What's your date of birth? (Please use YYYY-MM-DD format)"
            else:
                response['message'] = f"Invalid last name: {error_msg}. Please try again."
        
        elif field == 'date_of_birth':
            is_valid, error_msg = self.validate_date_of_birth(value)
            if is_valid:
                self.current_patient_data['date_of_birth'] = value.strip()
                response['message'] = "Great! Would you like to provide your phone number? (optional)"
            else:
                response['message'] = f"Invalid date of birth: {error_msg}. Please try again."
        
        elif field == 'phone':
            is_valid, error_msg = self.validate_phone(value)
            if is_valid:
                if value.strip():
                    self.current_patient_data['phone'] = value.strip()
                response['message'] = "Would you like to provide your email address? (optional)"
            else:
                response['message'] = f"Invalid phone number: {error_msg}. Please try again."
        
        elif field == 'email':
            is_valid, error_msg = self.validate_email(value)
            if is_valid:
                if value.strip():
                    self.current_patient_data['email'] = value.strip().lower()
                response['message'] = "Would you like to select a preferred doctor? (optional)"
            else:
                response['message'] = f"Invalid email address: {error_msg}. Please try again."
        
        elif field == 'preferred_doctor':
            is_valid, error_msg = self.validate_doctor(value)
            if is_valid:
                if value.strip():
                    self.current_patient_data['preferred_doctor'] = value.strip()
                response['status'] = 'complete'
                response['message'] = "Perfect! I have all the information I need. Let me check if you're a new or returning patient."
            else:
                response['message'] = f"Invalid doctor: {error_msg}. Please try again."
        
        response['patient_data'] = self.current_patient_data.copy()
        return response
    
    def is_intake_complete(self) -> bool:
        return all(field in self.current_patient_data for field in self.required_fields)
    
    def reset_intake(self):
        self.current_patient_data = {}
    
    def get_missing_fields(self) -> List[str]:
        return [field for field in self.required_fields if field not in self.current_patient_data]
