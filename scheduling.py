from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import PatientDatabase

class SmartScheduler:
    def __init__(self, db: PatientDatabase):
        self.db = db
        self.new_patient_duration = 60
        self.returning_patient_duration = 30
    
    def get_available_slots(self, doctor_name: str, date: str = None, duration: int = 30) -> List[Dict]:
        if date:
            available_slots = self.db.get_available_slots(doctor_name, date)
        else:
            available_slots = self.db.get_available_slots(doctor_name)
        
        suitable_slots = []
        for slot in available_slots:
            slot_datetime = datetime.strptime(slot['time_slot'], '%Y-%m-%d %H:%M')
            
            if self._is_slot_suitable(slot_datetime, duration):
                suitable_slots.append({
                    'time_slot': slot['time_slot'],
                    'date': slot['date'],
                    'doctor_name': slot['doctor_name'],
                    'duration': duration
                })
        
        return suitable_slots
    
    def _is_slot_suitable(self, slot_datetime: datetime, duration: int) -> bool:
        current_time = datetime.now()
        
        if slot_datetime <= current_time:
            return False
        
        if slot_datetime.weekday() >= 5:
            return False
        
        if slot_datetime.hour < 9 or slot_datetime.hour >= 17:
            return False
        
        if slot_datetime.hour == 12:
            return False
        
        return True
    
    def suggest_appointment_times(self, patient_data: Dict, doctor_name: str = None) -> Dict:
        is_new_patient = patient_data.get('is_new_patient', True)
        duration = self.new_patient_duration if is_new_patient else self.returning_patient_duration
        
        if doctor_name:
            doctors = [{'name': doctor_name}]
        else:
            doctors = self.db.get_doctors()
        
        suggestions = []
        
        for doctor in doctors:
            doctor_name = doctor['name']
            
            for days_ahead in [1, 2, 3, 7, 14]:
                target_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
                available_slots = self.get_available_slots(doctor_name, target_date, duration)
                
                if available_slots:
                    suggestions.append({
                        'doctor_name': doctor_name,
                        'date': target_date,
                        'available_times': [slot['time_slot'] for slot in available_slots[:3]],
                        'duration': duration
                    })
                    break
        
        return {
            'suggestions': suggestions,
            'is_new_patient': is_new_patient,
            'duration': duration
        }
    
    def book_appointment(self, patient_data: Dict, appointment_details: Dict) -> Dict:
        try:
            appointment_data = {
                'patient_id': patient_data['patient_id'],
                'doctor_name': appointment_details['doctor_name'],
                'appointment_date': appointment_details['appointment_date'],
                'appointment_time': appointment_details['appointment_time'],
                'duration_minutes': appointment_details['duration'],
                'appointment_type': 'new_patient' if patient_data.get('is_new_patient', True) else 'returning_patient',
                'insurance_carrier': patient_data.get('insurance_carrier', ''),
                'insurance_member_id': patient_data.get('insurance_member_id', ''),
                'insurance_group_number': patient_data.get('insurance_group_number', ''),
                'phone': patient_data.get('phone', ''),
                'email': patient_data.get('email', '')
            }
            
            appointment_id = self.db.book_appointment(appointment_data)
            
            return {
                'success': True,
                'appointment_id': appointment_id,
                'message': f"Appointment booked successfully! Your appointment ID is {appointment_id}."
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to book appointment: {str(e)}"
            }
    
    def check_conflicts(self, doctor_name: str, appointment_time: str, duration: int) -> bool:
        appointment_datetime = datetime.strptime(appointment_time, '%Y-%m-%d %H:%M')
        end_time = appointment_datetime + timedelta(minutes=duration)
        
        existing_appointments = self.db.appointments_df[
            (self.db.appointments_df['doctor_name'] == doctor_name) &
            (self.db.appointments_df['status'] == 'confirmed')
        ]
        
        for _, appointment in existing_appointments.iterrows():
            existing_start = datetime.strptime(
                f"{appointment['appointment_date']} {appointment['appointment_time']}", 
                '%Y-%m-%d %H:%M'
            )
            existing_end = existing_start + timedelta(minutes=appointment['duration_minutes'])
            
            if (appointment_datetime < existing_end and end_time > existing_start):
                return True
        
        return False
    
    def get_next_available_slot(self, doctor_name: str, preferred_date: str = None) -> Optional[Dict]:
        if preferred_date:
            available_slots = self.get_available_slots(doctor_name, preferred_date)
            if available_slots:
                return available_slots[0]
        
        for days_ahead in range(1, 31):
            target_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            available_slots = self.get_available_slots(doctor_name, target_date)
            if available_slots:
                return available_slots[0]
        
        return None
