import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

class PatientDatabase:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.patients_file = os.path.join(data_dir, "patients.csv")
        self.doctors_file = os.path.join(data_dir, "doctors.csv")
        self.schedule_file = os.path.join(data_dir, "doctor_schedules.xlsx")
        self.appointments_file = os.path.join(data_dir, "appointments.csv")
        
        self._load_data()
    
    def _load_data(self):
        self.patients_df = pd.read_csv(self.patients_file)
        self.doctors_df = pd.read_csv(self.doctors_file)
        self.schedule_df = pd.read_excel(self.schedule_file)
        
        if os.path.exists(self.appointments_file):
            self.appointments_df = pd.read_csv(self.appointments_file)
        else:
            self.appointments_df = pd.DataFrame(columns=[
                'appointment_id', 'patient_id', 'doctor_name', 'appointment_date',
                'appointment_time', 'duration_minutes', 'appointment_type',
                'status', 'created_at', 'insurance_carrier', 'insurance_member_id',
                'insurance_group_number', 'phone', 'email'
            ])
    
    def save_appointments(self):
        self.appointments_df.to_csv(self.appointments_file, index=False)
    
    def find_patient(self, first_name: str, last_name: str, dob: str = None) -> Optional[Dict]:
        first_name = first_name.lower().strip()
        last_name = last_name.lower().strip()
        
        mask = (
            (self.patients_df['first_name'].str.lower() == first_name) &
            (self.patients_df['last_name'].str.lower() == last_name)
        )
        
        if dob:
            mask = mask & (self.patients_df['date_of_birth'] == dob)
        
        matches = self.patients_df[mask]
        
        if len(matches) > 0:
            patient = matches.iloc[0].to_dict()
            patient['is_new_patient'] = patient.get('last_visit') is None or pd.isna(patient.get('last_visit'))
            return patient
        
        return None
    
    def create_new_patient(self, patient_data: Dict) -> str:
        patient_id = f"P{len(self.patients_df) + 1001:04d}"
        
        new_patient = {
            'patient_id': patient_id,
            'first_name': patient_data['first_name'],
            'last_name': patient_data['last_name'],
            'date_of_birth': patient_data['date_of_birth'],
            'phone': patient_data.get('phone', ''),
            'email': patient_data.get('email', ''),
            'preferred_doctor': patient_data.get('preferred_doctor', ''),
            'insurance_carrier': patient_data.get('insurance_carrier', ''),
            'insurance_member_id': patient_data.get('insurance_member_id', ''),
            'insurance_group_number': patient_data.get('insurance_group_number', ''),
            'last_visit': None,
            'is_new_patient': True
        }
        
        self.patients_df = pd.concat([self.patients_df, pd.DataFrame([new_patient])], ignore_index=True)
        self.patients_df.to_csv(self.patients_file, index=False)
        
        return patient_id
    
    def add_patient(self, patient_data: Dict) -> Optional[Dict]:
        """Add a new patient and return the patient data with patient_id"""
        try:
            patient_id = self.create_new_patient(patient_data)
            
            # Return the patient data with the new patient_id
            patient_data['patient_id'] = patient_id
            return patient_data
        except Exception as e:
            print(f"Error adding patient: {e}")
            return None
    
    def get_available_slots(self, doctor_name: str, date: str = None) -> List[Dict]:
        if date:
            mask = (
                (self.schedule_df['doctor_name'] == doctor_name) &
                (self.schedule_df['date'] == date) &
                (self.schedule_df['is_available'] == True)
            )
        else:
            mask = (
                (self.schedule_df['doctor_name'] == doctor_name) &
                (self.schedule_df['is_available'] == True)
            )
        
        available_slots = self.schedule_df[mask].copy()
        
        slots = []
        for _, slot in available_slots.iterrows():
            slots.append({
                'time_slot': slot['time_slot'],
                'date': slot['date'],
                'doctor_name': slot['doctor_name']
            })
        
        return slots
    
    def book_appointment(self, appointment_data: Dict) -> str:
        appointment_id = f"APT{len(self.appointments_df) + 1001:04d}"
        
        new_appointment = {
            'appointment_id': appointment_id,
            'patient_id': appointment_data['patient_id'],
            'doctor_name': appointment_data['doctor_name'],
            'appointment_date': appointment_data['appointment_date'],
            'appointment_time': appointment_data['appointment_time'],
            'duration_minutes': appointment_data['duration_minutes'],
            'appointment_type': appointment_data['appointment_type'],
            'status': 'confirmed',
            'created_at': datetime.now().isoformat(),
            'insurance_carrier': appointment_data.get('insurance_carrier', ''),
            'insurance_member_id': appointment_data.get('insurance_member_id', ''),
            'insurance_group_number': appointment_data.get('insurance_group_number', ''),
            'phone': appointment_data.get('phone', ''),
            'email': appointment_data.get('email', '')
        }
        
        self.appointments_df = pd.concat([self.appointments_df, pd.DataFrame([new_appointment])], ignore_index=True)
        
        time_slot = f"{appointment_data['appointment_date']} {appointment_data['appointment_time']}"
        slot_mask = (
            (self.schedule_df['doctor_name'] == appointment_data['doctor_name']) &
            (self.schedule_df['time_slot'] == time_slot)
        )
        
        if slot_mask.any():
            self.schedule_df.loc[slot_mask, 'is_available'] = False
            self.schedule_df.loc[slot_mask, 'patient_id'] = appointment_data['patient_id']
            self.schedule_df.loc[slot_mask, 'appointment_type'] = appointment_data['appointment_type']
            self.schedule_df.loc[slot_mask, 'duration_minutes'] = appointment_data['duration_minutes']
        
        self.save_appointments()
        self.schedule_df.to_excel(self.schedule_file, index=False)
        
        return appointment_id
    
    def get_doctors(self) -> List[Dict]:
        return self.doctors_df.to_dict('records')
    
    def get_patient_appointments(self, patient_id: str) -> List[Dict]:
        mask = self.appointments_df['patient_id'] == patient_id
        appointments = self.appointments_df[mask]
        return appointments.to_dict('records')
    
    def update_patient_visit(self, patient_id: str):
        mask = self.patients_df['patient_id'] == patient_id
        if mask.any():
            self.patients_df.loc[mask, 'last_visit'] = datetime.now().strftime('%Y-%m-%d')
            self.patients_df.loc[mask, 'is_new_patient'] = False
            self.patients_df.to_csv(self.patients_file, index=False)
