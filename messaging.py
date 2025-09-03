import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from config import Config

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logging.warning("Twilio not available. SMS functionality will be simulated.")

class EmailService:
    def __init__(self):
        self.smtp_server = Config.EMAIL_HOST
        self.smtp_port = Config.EMAIL_PORT
        self.username = Config.EMAIL_USERNAME
        self.password = Config.EMAIL_PASSWORD
        self.timeout_seconds = 20
    
    def send_email(self, to_email: str, subject: str, body: str, attachment_path: str = None) -> Dict:
        try:
            msg = MIMEMultipart()
            # Always read latest creds in case env changed
            username = os.getenv('EMAIL_USERNAME', self.username)
            password = os.getenv('EMAIL_PASSWORD', self.password)
            msg['From'] = username or self.username or ""
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEApplication(attachment.read(), Name=os.path.basename(attachment_path))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                    msg.attach(part)
            
            if username and password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout_seconds)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(username, password)
                server.send_message(msg)
                try:
                    server.quit()
                except Exception:
                    pass
                
                return {'success': True, 'message': 'Email sent successfully'}
            else:
                return {'success': True, 'message': f'Email would be sent to {to_email} (simulated)'}
        
        except Exception as e:
            return {'success': False, 'message': f'Failed to send email: {str(e)}'}
    
    def send_appointment_confirmation(self, patient_data: Dict, appointment_data: Dict) -> Dict:
        subject = f"Appointment Confirmation - {Config.CLINIC_NAME}"
        
        body = f"""
        <html>
        <body>
            <h2>Appointment Confirmation</h2>
            <p>Dear {patient_data['first_name']} {patient_data['last_name']},</p>
            
            <p>Your appointment has been confirmed with the following details:</p>
            
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr>
                    <td><strong>Appointment ID:</strong></td>
                    <td>{appointment_data['appointment_id']}</td>
                </tr>
                <tr>
                    <td><strong>Doctor:</strong></td>
                    <td>{appointment_data['doctor_name']}</td>
                </tr>
                <tr>
                    <td><strong>Date:</strong></td>
                    <td>{appointment_data['appointment_date']}</td>
                </tr>
                <tr>
                    <td><strong>Time:</strong></td>
                    <td>{appointment_data['appointment_time']}</td>
                </tr>
                <tr>
                    <td><strong>Duration:</strong></td>
                    <td>{appointment_data['duration']} minutes</td>
                </tr>
                <tr>
                    <td><strong>Type:</strong></td>
                    <td>{appointment_data.get('appointment_type','')}</td>
                </tr>
            </table>
            
            <p><strong>Clinic Information:</strong></p>
            <p>{Config.CLINIC_NAME}<br>
            {Config.CLINIC_ADDRESS}<br>
            Phone: {Config.CLINIC_PHONE}</p>
            
            <p>Please arrive 15 minutes early for your appointment.</p>
            
            <p>If you need to reschedule or cancel, please contact us at least 24 hours in advance.</p>
            
            <p>Thank you for choosing {Config.CLINIC_NAME}!</p>
        </body>
        </html>
        """
        
        return self.send_email(patient_data['email'], subject, body)
    
    def send_new_patient_form(self, patient_data: Dict, appointment_data: Dict) -> Dict:
        subject = f"New Patient Intake Form - {Config.CLINIC_NAME}"
        
        body = f"""
        <html>
        <body>
            <h2>New Patient Intake Form</h2>
            <p>Dear {patient_data['first_name']} {patient_data['last_name']},</p>
            
            <p>Thank you for scheduling your appointment with {Config.CLINIC_NAME}!</p>
            
            <p>As a new patient, please complete the attached intake form and bring it with you to your appointment on {appointment_data['appointment_date']} at {appointment_data['appointment_time']}.</p>
            
            <p>If you have any questions about the form, please don't hesitate to contact us.</p>
            
            <p>We look forward to seeing you!</p>
            
            <p>Best regards,<br>
            {Config.CLINIC_NAME}</p>
        </body>
        </html>
        """
        
        form_path = "resources/New Patient Intake Form.pdf"
        return self.send_email(patient_data['email'], subject, body, form_path)
    
    def send_reminder(self, patient_data: Dict, appointment_data: Dict, reminder_type: str) -> Dict:
        if reminder_type == "simple":
            subject = f"Appointment Reminder - {Config.CLINIC_NAME}"
            body = f"""
            <html>
            <body>
                <h2>Appointment Reminder</h2>
                <p>Dear {patient_data['first_name']} {patient_data['last_name']},</p>
                
                <p>This is a friendly reminder about your upcoming appointment:</p>
                
                <p><strong>Date:</strong> {appointment_data['appointment_date']}<br>
                <strong>Time:</strong> {appointment_data['appointment_time']}<br>
                <strong>Doctor:</strong> {appointment_data['doctor_name']}</p>
                
                <p>Please arrive 15 minutes early.</p>
                
                <p>If you need to reschedule, please contact us at {Config.CLINIC_PHONE}.</p>
            </body>
            </html>
            """
        
        elif reminder_type == "forms":
            subject = f"Intake Forms Reminder - {Config.CLINIC_NAME}"
            body = f"""
            <html>
            <body>
                <h2>Intake Forms Reminder</h2>
                <p>Dear {patient_data['first_name']} {patient_data['last_name']},</p>
                
                <p>Your appointment is coming up on {appointment_data['appointment_date']} at {appointment_data['appointment_time']}.</p>
                
                <p>Have you completed your intake forms? If not, please do so before your appointment to save time during your visit.</p>
                
                <p>If you need another copy of the forms, please let us know.</p>
            </body>
            </html>
            """
        
        elif reminder_type == "confirmation":
            subject = f"Final Confirmation - {Config.CLINIC_NAME}"
            body = f"""
            <html>
            <body>
                <h2>Final Appointment Confirmation</h2>
                <p>Dear {patient_data['first_name']} {patient_data['last_name']},</p>
                
                <p>Your appointment is tomorrow on {appointment_data['appointment_date']} at {appointment_data['appointment_time']} with {appointment_data['doctor_name']}.</p>
                
                <p>Please confirm that you will be attending or let us know if you need to cancel or reschedule.</p>
                
                <p>Reply to this email or call us at {Config.CLINIC_PHONE}.</p>
            </body>
            </html>
            """
        
        return self.send_email(patient_data['email'], subject, body)

class SMSService:
    def __init__(self):
        self.twilio_available = TWILIO_AVAILABLE
        if self.twilio_available and Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN:
            self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
            self.from_number = Config.TWILIO_PHONE_NUMBER
        else:
            self.client = None
            self.from_number = None
    
    def send_sms(self, to_number: str, message: str) -> Dict:
        try:
            if self.client and self.from_number:
                message_obj = self.client.messages.create(
                    body=message,
                    from_=self.from_number,
                    to=to_number
                )
                return {'success': True, 'message': f'SMS sent successfully. SID: {message_obj.sid}'}
            else:
                return {'success': True, 'message': f'SMS would be sent to {to_number}: {message} (simulated)'}
        
        except Exception as e:
            return {'success': False, 'message': f'Failed to send SMS: {str(e)}'}
    
    def send_appointment_confirmation_sms(self, patient_data: Dict, appointment_data: Dict) -> Dict:
        message = f"Appointment confirmed! {appointment_data['appointment_date']} at {appointment_data['appointment_time']} with {appointment_data['doctor_name']}. ID: {appointment_data['appointment_id']}. {Config.CLINIC_NAME}"
        return self.send_sms(patient_data['phone'], message)
    
    def send_reminder_sms(self, patient_data: Dict, appointment_data: Dict, reminder_type: str) -> Dict:
        if reminder_type == "simple":
            message = f"Reminder: Appointment on {appointment_data['appointment_date']} at {appointment_data['appointment_time']} with {appointment_data['doctor_name']}. {Config.CLINIC_NAME}"
        elif reminder_type == "forms":
            message = f"Don't forget to complete your intake forms before your appointment on {appointment_data['appointment_date']}. {Config.CLINIC_NAME}"
        elif reminder_type == "confirmation":
            message = f"Please confirm your appointment tomorrow at {appointment_data['appointment_time']} with {appointment_data['doctor_name']}. Reply YES to confirm. {Config.CLINIC_NAME}"
        
        return self.send_sms(patient_data['phone'], message)

class MessagingService:
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
    
    def send_appointment_confirmation(self, patient_data: Dict, appointment_data: Dict) -> Dict:
        results = {}
        
        if patient_data.get('email'):
            results['email'] = self.email_service.send_appointment_confirmation(patient_data, appointment_data)
        
        if patient_data.get('phone'):
            results['sms'] = self.sms_service.send_appointment_confirmation_sms(patient_data, appointment_data)
        
        return results
    
    def send_new_patient_form(self, patient_data: Dict, appointment_data: Dict) -> Dict:
        if patient_data.get('email') and patient_data.get('is_new_patient', True):
            return self.email_service.send_new_patient_form(patient_data, appointment_data)
        return {'success': True, 'message': 'No email available or not a new patient'}
    
    def send_reminder(self, patient_data: Dict, appointment_data: Dict, reminder_type: str) -> Dict:
        results = {}
        
        if patient_data.get('email'):
            results['email'] = self.email_service.send_reminder(patient_data, appointment_data, reminder_type)
        
        if patient_data.get('phone'):
            results['sms'] = self.sms_service.send_reminder_sms(patient_data, appointment_data, reminder_type)
        
        return results
