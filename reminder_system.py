from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from database import PatientDatabase
from messaging import MessagingService

class ReminderSystem:
    def __init__(self, db: PatientDatabase):
        self.db = db
        self.messaging_service = MessagingService()
        self.reminder_log_file = "data/reminder_log.csv"
        self._initialize_reminder_log()
    
    def _initialize_reminder_log(self):
        if not os.path.exists(self.reminder_log_file):
            reminder_log_df = pd.DataFrame(columns=[
                'appointment_id', 'patient_id', 'reminder_type', 'sent_at', 
                'email_success', 'sms_success', 'response_received'
            ])
            reminder_log_df.to_csv(self.reminder_log_file, index=False)
    
    def get_upcoming_appointments(self, days_ahead: int = 7) -> List[Dict]:
        current_date = datetime.now().date()
        target_date = current_date + timedelta(days=days_ahead)
        
        upcoming_appointments = self.db.appointments_df[
            (self.db.appointments_df['appointment_date'] == target_date.strftime('%Y-%m-%d')) &
            (self.db.appointments_df['status'] == 'confirmed')
        ]
        
        appointments_with_patient_data = []
        for _, appointment in upcoming_appointments.iterrows():
            patient_data = self.db.patients_df[
                self.db.patients_df['patient_id'] == appointment['patient_id']
            ]
            
            if not patient_data.empty:
                patient = patient_data.iloc[0].to_dict()
                appointment_data = appointment.to_dict()
                appointments_with_patient_data.append({
                    'patient': patient,
                    'appointment': appointment_data
                })
        
        return appointments_with_patient_data
    
    def send_simple_reminder(self, patient_data: Dict, appointment_data: Dict) -> Dict:
        results = self.messaging_service.send_reminder(
            patient_data, appointment_data, "simple"
        )
        
        self._log_reminder(
            appointment_data['appointment_id'],
            patient_data['patient_id'],
            'simple',
            results
        )
        
        return results
    
    def send_forms_reminder(self, patient_data: Dict, appointment_data: Dict) -> Dict:
        if not patient_data.get('is_new_patient', True):
            return {'success': True, 'message': 'Not a new patient, skipping forms reminder'}
        
        results = self.messaging_service.send_reminder(
            patient_data, appointment_data, "forms"
        )
        
        self._log_reminder(
            appointment_data['appointment_id'],
            patient_data['patient_id'],
            'forms',
            results
        )
        
        return results
    
    def send_confirmation_reminder(self, patient_data: Dict, appointment_data: Dict) -> Dict:
        results = self.messaging_service.send_reminder(
            patient_data, appointment_data, "confirmation"
        )
        
        self._log_reminder(
            appointment_data['appointment_id'],
            patient_data['patient_id'],
            'confirmation',
            results
        )
        
        return results
    
    def _log_reminder(self, appointment_id: str, patient_id: str, reminder_type: str, results: Dict):
        log_entry = {
            'appointment_id': appointment_id,
            'patient_id': patient_id,
            'reminder_type': reminder_type,
            'sent_at': datetime.now().isoformat(),
            'email_success': results.get('email', {}).get('success', False),
            'sms_success': results.get('sms', {}).get('success', False),
            'response_received': False
        }
        
        reminder_log_df = pd.read_csv(self.reminder_log_file)
        reminder_log_df = pd.concat([reminder_log_df, pd.DataFrame([log_entry])], ignore_index=True)
        reminder_log_df.to_csv(self.reminder_log_file, index=False)
    
    def process_daily_reminders(self) -> Dict:
        results = {
            'simple_reminders': [],
            'forms_reminders': [],
            'confirmation_reminders': [],
            'errors': []
        }
        
        try:
            appointments_3_days = self.get_upcoming_appointments(3)
            appointments_1_day = self.get_upcoming_appointments(1)
            
            for appointment_info in appointments_3_days:
                patient_data = appointment_info['patient']
                appointment_data = appointment_info['appointment']
                
                if patient_data.get('is_new_patient', True):
                    reminder_result = self.send_forms_reminder(patient_data, appointment_data)
                    results['forms_reminders'].append({
                        'appointment_id': appointment_data['appointment_id'],
                        'patient_name': f"{patient_data['first_name']} {patient_data['last_name']}",
                        'result': reminder_result
                    })
                else:
                    reminder_result = self.send_simple_reminder(patient_data, appointment_data)
                    results['simple_reminders'].append({
                        'appointment_id': appointment_data['appointment_id'],
                        'patient_name': f"{patient_data['first_name']} {patient_data['last_name']}",
                        'result': reminder_result
                    })
            
            for appointment_info in appointments_1_day:
                patient_data = appointment_info['patient']
                appointment_data = appointment_info['appointment']
                
                reminder_result = self.send_confirmation_reminder(patient_data, appointment_data)
                results['confirmation_reminders'].append({
                    'appointment_id': appointment_data['appointment_id'],
                    'patient_name': f"{patient_data['first_name']} {patient_data['last_name']}",
                    'result': reminder_result
                })
        
        except Exception as e:
            results['errors'].append(f"Error processing reminders: {str(e)}")
        
        return results
    
    def get_reminder_status(self, appointment_id: str) -> Dict:
        reminder_log_df = pd.read_csv(self.reminder_log_file)
        appointment_reminders = reminder_log_df[
            reminder_log_df['appointment_id'] == appointment_id
        ]
        
        if appointment_reminders.empty:
            return {'status': 'no_reminders_sent'}
        
        reminders = appointment_reminders.to_dict('records')
        
        return {
            'status': 'reminders_sent',
            'reminders': reminders,
            'total_sent': len(reminders)
        }
    
    def mark_response_received(self, appointment_id: str, reminder_type: str, response: str):
        reminder_log_df = pd.read_csv(self.reminder_log_file)
        
        mask = (
            (reminder_log_df['appointment_id'] == appointment_id) &
            (reminder_log_df['reminder_type'] == reminder_type)
        )
        
        if mask.any():
            reminder_log_df.loc[mask, 'response_received'] = True
            reminder_log_df.loc[mask, 'response_text'] = response
            reminder_log_df.to_csv(self.reminder_log_file, index=False)
    
    def generate_reminder_report(self, start_date: str = None, end_date: str = None) -> Dict:
        reminder_log_df = pd.read_csv(self.reminder_log_file)
        
        if start_date:
            reminder_log_df = reminder_log_df[reminder_log_df['sent_at'] >= start_date]
        if end_date:
            reminder_log_df = reminder_log_df[reminder_log_df['sent_at'] <= end_date]
        
        total_reminders = len(reminder_log_df)
        email_success_rate = reminder_log_df['email_success'].mean() * 100 if total_reminders > 0 else 0
        sms_success_rate = reminder_log_df['sms_success'].mean() * 100 if total_reminders > 0 else 0
        response_rate = reminder_log_df['response_received'].mean() * 100 if total_reminders > 0 else 0
        
        reminder_types = reminder_log_df['reminder_type'].value_counts().to_dict()
        
        return {
            'total_reminders': total_reminders,
            'email_success_rate': round(email_success_rate, 2),
            'sms_success_rate': round(sms_success_rate, 2),
            'response_rate': round(response_rate, 2),
            'reminder_types': reminder_types,
            'period': f"{start_date} to {end_date}" if start_date and end_date else "All time"
        }

import os
