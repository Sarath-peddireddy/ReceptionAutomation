import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from ai_agent import ClinicSchedulingAgent
from database import PatientDatabase
from reminder_system import ReminderSystem
from messaging import MessagingService

st.set_page_config(
    page_title="AI Healthcare Scheduling Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_agent():
    return ClinicSchedulingAgent()

@st.cache_resource
def load_database():
    return PatientDatabase()

@st.cache_resource
def load_reminder_system():
    db = PatientDatabase()
    return ReminderSystem(db)

def main():
    st.title("🏥 AI Healthcare Scheduling Agent")
    st.markdown("---")
    
    agent = load_agent()
    db = load_database()
    reminder_system = load_reminder_system()
    
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat Interface", "📊 Dashboard", "📅 Appointments", "⚙️ Admin"])
    
    with tab1:
        st.header("Patient Scheduling Chat")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "agent_session" not in st.session_state:
            st.session_state.agent_session = agent
            st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize conversation state if not exists
        if "conversation_state" not in st.session_state:
            st.session_state.conversation_state = {
                'current_step': 'greeting',
                'patient_data': {},
                'insurance_data': {},
                'appointment_data': {},
                'conversation_history': [],
                'waiting_for': None,
                'session_id': st.session_state.session_id,
                'greeting_shown': False
            }
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Always show the input box
        if prompt := st.chat_input("Type your message here..."):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process with AI agent
            with st.chat_message("assistant"):
                with st.spinner("Processing..."):
                    # Update the agent's conversation state with our persistent state
                    st.session_state.agent_session.conversation_state = st.session_state.conversation_state
                    
                    # Process the message
                    response = st.session_state.agent_session.process_message(
                        prompt, 
                        st.session_state.session_id
                    )
                    
                    # Update our persistent state with the agent's updated state
                    st.session_state.conversation_state = st.session_state.agent_session.conversation_state
                    
                st.markdown(response)
            
            # Add AI response to chat
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Force rerun to update the UI
            st.rerun()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset Conversation"):
                st.session_state.agent_session.reset_conversation()
                st.session_state.messages = []
                # Reset the persistent conversation state
                st.session_state.conversation_state = {
                    'current_step': 'greeting',
                    'patient_data': {},
                    'insurance_data': {},
                    'appointment_data': {},
                    'conversation_history': [],
                    'waiting_for': None,
                    'session_id': st.session_state.session_id,
                    'greeting_shown': False
                }
                st.rerun()
        
        with col2:
            if st.button("📋 Export Chat"):
                chat_data = {
                    'timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * len(st.session_state.messages),
                    'role': [msg['role'] for msg in st.session_state.messages],
                    'content': [msg['content'] for msg in st.session_state.messages]
                }
                df = pd.DataFrame(chat_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Chat History",
                    data=csv,
                    file_name=f"chat_history_{st.session_state.session_id}.csv",
                    mime="text/csv"
                )
        
        # Debug information (remove this in production)
        with st.expander("🔧 Debug Information"):
            st.write("**Current Step:**", st.session_state.conversation_state.get('current_step', 'unknown'))
            st.write("**Waiting For:**", st.session_state.conversation_state.get('waiting_for', 'none'))
            st.write("**Patient Data:**", st.session_state.conversation_state.get('patient_data', {}))
            st.write("**Session ID:**", st.session_state.session_id)
    
    with tab2:
        st.header("📊 Clinic Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_patients = len(db.patients_df)
            st.metric("Total Patients", total_patients)
        
        with col2:
            total_appointments = len(db.appointments_df)
            st.metric("Total Appointments", total_appointments)
        
        with col3:
            confirmed_appointments = len(db.appointments_df[db.appointments_df['status'] == 'confirmed'])
            st.metric("Confirmed Appointments", confirmed_appointments)
        
        with col4:
            new_patients = len(db.patients_df[db.patients_df['is_new_patient'] == True])
            st.metric("New Patients", new_patients)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Appointment Trends")
            if not db.appointments_df.empty:
                appointments_by_date = db.appointments_df.groupby('appointment_date').size().reset_index(name='count')
                appointments_by_date['appointment_date'] = pd.to_datetime(appointments_by_date['appointment_date'])
                st.line_chart(appointments_by_date.set_index('appointment_date'))
            else:
                st.info("No appointment data available")
        
        with col2:
            st.subheader("👨‍⚕️ Doctor Workload")
            if not db.appointments_df.empty:
                doctor_appointments = db.appointments_df['doctor_name'].value_counts()
                st.bar_chart(doctor_appointments)
            else:
                st.info("No appointment data available")
        
        st.markdown("---")
        
        st.subheader("📋 Recent Appointments")
        if not db.appointments_df.empty:
            recent_appointments = db.appointments_df.tail(10)[
                ['appointment_id', 'patient_id', 'doctor_name', 'appointment_date', 'appointment_time', 'status']
            ]
            st.dataframe(recent_appointments, width='stretch')
        else:
            st.info("No appointments scheduled yet")
    
    with tab3:
        st.header("📅 Appointment Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔍 Search Appointments")
            search_option = st.selectbox("Search by:", ["Patient ID", "Doctor", "Date"])
            
            if search_option == "Patient ID":
                patient_id = st.text_input("Enter Patient ID:")
                if patient_id:
                    appointments = db.get_patient_appointments(patient_id)
                    if appointments:
                        st.dataframe(pd.DataFrame(appointments), use_container_width=True)
                    else:
                        st.warning("No appointments found for this patient")
            
            elif search_option == "Doctor":
                doctors = db.get_doctors()
                doctor_names = [doc['name'] for doc in doctors]
                selected_doctor = st.selectbox("Select Doctor:", doctor_names)
                if selected_doctor:
                    doctor_appointments = db.appointments_df[
                        db.appointments_df['doctor_name'] == selected_doctor
                    ]
                    if not doctor_appointments.empty:
                        st.dataframe(doctor_appointments, width='stretch')
                    else:
                        st.warning("No appointments found for this doctor")
            
            elif search_option == "Date":
                selected_date = st.date_input("Select Date:")
                if selected_date:
                    date_appointments = db.appointments_df[
                        db.appointments_df['appointment_date'] == selected_date.strftime('%Y-%m-%d')
                    ]
                    if not date_appointments.empty:
                        st.dataframe(date_appointments, width='stretch')
                    else:
                        st.warning("No appointments found for this date")
        
        with col2:
            st.subheader("📊 Appointment Statistics")
            
            if not db.appointments_df.empty:
                appointment_types = db.appointments_df['appointment_type'].value_counts()
                st.bar_chart(appointment_types)
                
                st.markdown("**Appointment Status:**")
                status_counts = db.appointments_df['status'].value_counts()
                for status, count in status_counts.items():
                    st.write(f"- {status}: {count}")
            else:
                st.info("No appointment data available")
    
    with tab4:
        st.header("⚙️ Admin Panel")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📧 Send Reminders")
            
            if st.button("Send Daily Reminders"):
                with st.spinner("Processing reminders..."):
                    results = reminder_system.process_daily_reminders()
                
                st.success("Reminders processed!")
                
                if results['simple_reminders']:
                    st.write("**Simple Reminders Sent:**")
                    for reminder in results['simple_reminders']:
                        res = reminder.get('result')
                        # result may be a dict of channel results or a single dict
                        if isinstance(res, dict) and 'message' in res:
                            st.write(f"- {reminder['patient_name']}: {res['message']}")
                        elif isinstance(res, dict):
                            email_res = res.get('email', {})
                            sms_res = res.get('sms', {})
                            parts = []
                            if isinstance(email_res, dict) and 'message' in email_res:
                                parts.append(f"Email: {email_res['message']}")
                            if isinstance(sms_res, dict) and 'message' in sms_res:
                                parts.append(f"SMS: {sms_res['message']}")
                            st.write(f"- {reminder['patient_name']}: {' | '.join(parts) if parts else 'sent'}")
                        else:
                            st.write(f"- {reminder['patient_name']}: sent")
                
                if results['forms_reminders']:
                    st.write("**Forms Reminders Sent:**")
                    for reminder in results['forms_reminders']:
                        res = reminder.get('result')
                        if isinstance(res, dict) and 'message' in res:
                            st.write(f"- {reminder['patient_name']}: {res['message']}")
                        elif isinstance(res, dict):
                            email_res = res.get('email', {})
                            sms_res = res.get('sms', {})
                            parts = []
                            if isinstance(email_res, dict) and 'message' in email_res:
                                parts.append(f"Email: {email_res['message']}")
                            if isinstance(sms_res, dict) and 'message' in sms_res:
                                parts.append(f"SMS: {sms_res['message']}")
                            st.write(f"- {reminder['patient_name']}: {' | '.join(parts) if parts else 'sent'}")
                        else:
                            st.write(f"- {reminder['patient_name']}: sent")
                
                if results['confirmation_reminders']:
                    st.write("**Confirmation Reminders Sent:**")
                    for reminder in results['confirmation_reminders']:
                        res = reminder.get('result')
                        if isinstance(res, dict) and 'message' in res:
                            st.write(f"- {reminder['patient_name']}: {res['message']}")
                        elif isinstance(res, dict):
                            email_res = res.get('email', {})
                            sms_res = res.get('sms', {})
                            parts = []
                            if isinstance(email_res, dict) and 'message' in email_res:
                                parts.append(f"Email: {email_res['message']}")
                            if isinstance(sms_res, dict) and 'message' in sms_res:
                                parts.append(f"SMS: {sms_res['message']}")
                            st.write(f"- {reminder['patient_name']}: {' | '.join(parts) if parts else 'sent'}")
                        else:
                            st.write(f"- {reminder['patient_name']}: sent")
                
                if results['errors']:
                    st.error("**Errors:**")
                    for error in results['errors']:
                        st.write(f"- {error}")
        
        with col2:
            st.subheader("📊 Reminder Reports")
            
            if st.button("Generate Reminder Report"):
                report = reminder_system.generate_reminder_report()
                
                st.write("**Reminder Statistics:**")
                st.write(f"- Total Reminders Sent: {report['total_reminders']}")
                st.write(f"- Email Success Rate: {report['email_success_rate']}%")
                st.write(f"- SMS Success Rate: {report['sms_success_rate']}%")
                st.write(f"- Response Rate: {report['response_rate']}%")
                
                st.write("**Reminder Types:**")
                for reminder_type, count in report['reminder_types'].items():
                    st.write(f"- {reminder_type}: {count}")
        
        st.markdown("---")
        
        st.subheader("📁 Data Export")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Export Patients"):
                csv = db.patients_df.to_csv(index=False)
                st.download_button(
                    label="Download Patients CSV",
                    data=csv,
                    file_name=f"patients_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Export Appointments"):
                csv = db.appointments_df.to_csv(index=False)
                st.download_button(
                    label="Download Appointments CSV",
                    data=csv,
                    file_name=f"appointments_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("Export Schedule"):
                csv = db.schedule_df.to_csv(index=False)
                st.download_button(
                    label="Download Schedule CSV",
                    data=csv,
                    file_name=f"schedule_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

        st.markdown("---")
        st.subheader("✉️ Email Diagnostics")
        test_email = st.text_input("Send a test email to:", value=os.getenv('EMAIL_USERNAME',''))
        if st.button("Send Test Email"):
            ms = MessagingService()
            res = ms.email_service.send_email(
                to_email=test_email,
                subject="Clinic App Test",
                body="<b>This is a test email from the clinic app.</b>"
            )
            if res.get('success'):
                st.success(res.get('message','Email sent'))
            else:
                st.error(res.get('message','Failed to send'))

if __name__ == "__main__":
    main()
