from typing import Dict, List, Optional, Any
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage, AIMessage
from database import PatientDatabase
from patient_intake import PatientIntake
from insurance_collection import InsuranceCollector
from scheduling import SmartScheduler
from messaging import MessagingService
from reminder_system import ReminderSystem

class ClinicSchedulingAgent:
    def __init__(self):
        self.db = PatientDatabase()
        self.patient_intake = PatientIntake(self.db)
        self.insurance_collector = InsuranceCollector()
        self.scheduler = SmartScheduler(self.db)
        self.messaging_service = MessagingService()
        self.reminder_system = ReminderSystem(self.db)
        
        self.conversation_state = {
            'current_step': 'greeting',
            'patient_data': {},
            'insurance_data': {},
            'appointment_data': {},
            'conversation_history': [],
            'waiting_for': None,
            'session_id': None
        }
        
        self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(dict)
        
        workflow.add_node("greeting", self._greeting_node)
        workflow.add_node("patient_lookup", self._patient_lookup_node)
        workflow.add_node("patient_intake", self._patient_intake_node)
        workflow.add_node("insurance_collection", self._insurance_collection_node)
        workflow.add_node("scheduling", self._scheduling_node)
        workflow.add_node("confirmation", self._confirmation_node)
        workflow.add_node("form_distribution", self._form_distribution_node)
        workflow.add_node("completion", self._completion_node)
        
        workflow.set_entry_point("greeting")
        
        workflow.add_conditional_edges(
            "greeting",
            self._route_after_greeting,
            {
                "patient_lookup": "patient_lookup",
                "patient_intake": "patient_intake",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "patient_lookup",
            self._route_after_lookup,
            {
                "insurance_collection": "insurance_collection",
                "patient_intake": "patient_intake",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "patient_intake",
            self._route_after_intake,
            {
                "insurance_collection": "insurance_collection",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "insurance_collection",
            self._route_after_insurance,
            {
                "scheduling": "scheduling",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "scheduling",
            self._route_after_scheduling,
            {
                "confirmation": "confirmation",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "confirmation",
            self._route_after_confirmation,
            {
                "form_distribution": "form_distribution",
                "completion": "completion",
                "end": END
            }
        )
        
        workflow.add_edge("form_distribution", "completion")
        workflow.add_edge("completion", END)
        
        self.graph = workflow.compile()
    
    def _greeting_node(self, state: Dict) -> Dict:
        # Only show greeting if we haven't shown it yet
        if not state.get('greeting_shown', False):
            greeting_message = f"""Hello! Welcome to {self.db.CLINIC_NAME if hasattr(self.db, 'CLINIC_NAME') else 'HealthCare Plus Clinic'}! 

I'm your AI scheduling assistant. I can help you:
- Schedule new appointments
- Reschedule existing appointments
- Collect your information
- Handle insurance details

Are you a new patient or returning patient? Please provide your first and last name to get started."""
            
            state['conversation_history'].append(AIMessage(content=greeting_message))
            state['greeting_shown'] = True
        
        state['current_step'] = 'patient_lookup'
        return state
    
    def _patient_lookup_node(self, state: Dict) -> Dict:
        user_input = state.get('user_input', '').strip().lower()
        
        if not user_input:
            response = "Please provide your first and last name so I can look you up in our system."
            state['conversation_history'].append(AIMessage(content=response))
            return state
        
        # Check if user is indicating they are a new patient
        if 'new patient' in user_input or 'new' in user_input:
            response = "Great! I'll help you create a new patient record. Please provide your first and last name."
            state['conversation_history'].append(AIMessage(content=response))
            state['waiting_for'] = 'patient_name'
            return state
        
        # Check if we're waiting for patient name after new patient indication
        if state.get('waiting_for') == 'patient_name':
            name_parts = user_input.split()
            if len(name_parts) < 2:
                response = "Please provide both your first and last name."
                state['conversation_history'].append(AIMessage(content=response))
                return state
            
            first_name = name_parts[0].title()
            last_name = ' '.join(name_parts[1:]).title()
            response = f"Thank you, {first_name} {last_name}. Please provide your date of birth (YYYY-MM-DD format)."
            state['conversation_history'].append(AIMessage(content=response))
            state['patient_data'] = {'first_name': first_name, 'last_name': last_name, 'is_new_patient': True}
            state['current_step'] = 'patient_intake'
            state['waiting_for'] = None
            return state
        
        # Regular patient lookup
        name_parts = user_input.split()
        if len(name_parts) < 2:
            response = "Please provide both your first and last name."
            state['conversation_history'].append(AIMessage(content=response))
            return state
        
        first_name = name_parts[0].title()
        last_name = ' '.join(name_parts[1:]).title()
        
        patient = self.db.find_patient(first_name, last_name)
        
        if patient:
            state['patient_data'] = patient
            response = f"Hello {patient['first_name']}! I found you in our system. "
            
            if patient.get('is_new_patient', True):
                response += "I see you're a new patient. Let me collect some additional information and help you schedule your first appointment."
            else:
                response += "Welcome back! I can help you schedule your next appointment."
            
            state['conversation_history'].append(AIMessage(content=response))
            state['current_step'] = 'insurance_collection'
        else:
            response = f"I couldn't find a patient named {first_name} {last_name} in our system. Let me help you create a new patient record. Please provide your date of birth (YYYY-MM-DD format)."
            state['conversation_history'].append(AIMessage(content=response))
            state['patient_data'] = {'first_name': first_name, 'last_name': last_name, 'is_new_patient': True}
            state['current_step'] = 'patient_intake'
        
        return state
    
    def _patient_intake_node(self, state: Dict) -> Dict:
        user_input = state.get('user_input', '').strip()
        patient_data = state.get('patient_data', {})
        
        # Check if we need to collect date of birth
        if 'date_of_birth' not in patient_data:
            # Validate date of birth
            is_valid, error_msg = self.patient_intake.validate_date_of_birth(user_input)
            if is_valid:
                patient_data['date_of_birth'] = user_input
                state['patient_data'] = patient_data
                response = "Great! Would you like to provide your phone number? (optional)"
                state['conversation_history'].append(AIMessage(content=response))
                state['waiting_for'] = 'phone'
            else:
                response = f"Invalid date of birth: {error_msg}. Please try again."
                state['conversation_history'].append(AIMessage(content=response))
            return state
        
        # Check if we need to collect phone
        elif state.get('waiting_for') == 'phone':
            if user_input.lower() in ['no', 'skip', 'n/a', '']:
                response = "Would you like to provide your email address? (optional)"
                state['conversation_history'].append(AIMessage(content=response))
                state['waiting_for'] = 'email'
            else:
                is_valid, error_msg = self.patient_intake.validate_phone(user_input)
                if is_valid:
                    if user_input.strip():
                        patient_data['phone'] = user_input.strip()
                    response = "Would you like to provide your email address? (optional)"
                    state['conversation_history'].append(AIMessage(content=response))
                    state['waiting_for'] = 'email'
                else:
                    response = f"Invalid phone number: {error_msg}. Please try again."
                    state['conversation_history'].append(AIMessage(content=response))
            state['patient_data'] = patient_data
            return state
        
        # Check if we need to collect email
        elif state.get('waiting_for') == 'email':
            if user_input.lower() in ['no', 'skip', 'n/a', '']:
                response = "Would you like to select a preferred doctor? (optional)\n\n- Dr. Sarah Johnson (Allergist) - Downtown Clinic\n- Dr. Amit Patel (Pulmonologist) - Midtown Clinic\n- Dr. Emily Carter (ENT Specialist) - Uptown Clinic"
                state['conversation_history'].append(AIMessage(content=response))
                state['waiting_for'] = 'doctor'
            else:
                is_valid, error_msg = self.patient_intake.validate_email(user_input)
                if is_valid:
                    if user_input.strip():
                        patient_data['email'] = user_input.strip().lower()
                    response = "Would you like to select a preferred doctor? (optional)\n\n- Dr. Sarah Johnson (Allergist) - Downtown Clinic\n- Dr. Amit Patel (Pulmonologist) - Midtown Clinic\n- Dr. Emily Carter (ENT Specialist) - Uptown Clinic"
                    state['conversation_history'].append(AIMessage(content=response))
                    state['waiting_for'] = 'doctor'
                else:
                    response = f"Invalid email address: {error_msg}. Please try again."
                    state['conversation_history'].append(AIMessage(content=response))
            state['patient_data'] = patient_data
            return state
        
        # Check if we need to collect doctor preference
        elif state.get('waiting_for') == 'doctor':
            if user_input.lower() in ['no', 'skip', 'n/a', '']:
                response = "Perfect! I have all the information I need. Let me collect your insurance information."
                state['conversation_history'].append(AIMessage(content=response))
                state['current_step'] = 'insurance_collection'
                state['waiting_for'] = None
            else:
                is_valid, error_msg = self.patient_intake.validate_doctor(user_input)
                if is_valid:
                    if user_input.strip():
                        patient_data['preferred_doctor'] = user_input.strip()
                    response = "Perfect! I have all the information I need. Let me collect your insurance information."
                    state['conversation_history'].append(AIMessage(content=response))
                    state['current_step'] = 'insurance_collection'
                    state['waiting_for'] = None
                else:
                    response = f"Invalid doctor: {error_msg}. Please try again."
                    state['conversation_history'].append(AIMessage(content=response))
            state['patient_data'] = patient_data
            return state
        
        # If we get here, move to insurance collection
        state['current_step'] = 'insurance_collection'
        return state
    
    def _insurance_collection_node(self, state: Dict) -> Dict:
        user_input = state.get('user_input', '').strip()
        patient_data = state.get('patient_data', {})
        
        # Simplified insurance collection - just collect basic info and move to scheduling
        if 'insurance_carrier' not in patient_data:
            if not state.get('waiting_for'):
                response = "I need to collect your insurance information. What's your insurance carrier name?"
                state['conversation_history'].append(AIMessage(content=response))
                state['waiting_for'] = 'insurance_carrier'
                return state
            elif state.get('waiting_for') == 'insurance_carrier':
                # Accept any input as insurance carrier for now
                patient_data['insurance_carrier'] = user_input
                response = "Great! What's your insurance member ID?"
                state['conversation_history'].append(AIMessage(content=response))
                state['waiting_for'] = 'insurance_member_id'
                state['patient_data'] = patient_data
                return state
        
        elif state.get('waiting_for') == 'insurance_member_id':
            # Accept any input as member ID for now
            patient_data['insurance_member_id'] = user_input
            response = "Perfect! Do you have a group number? (optional)"
            state['conversation_history'].append(AIMessage(content=response))
            state['waiting_for'] = 'insurance_group_number'
            state['patient_data'] = patient_data
            return state
        
        elif state.get('waiting_for') == 'insurance_group_number':
            if user_input.lower() in ['no', 'skip', 'n/a', '']:
                response = "Excellent! I have all your insurance information. Let's proceed with scheduling your appointment."
                state['conversation_history'].append(AIMessage(content=response))
                state['current_step'] = 'scheduling'
                state['waiting_for'] = None
            else:
                patient_data['insurance_group_number'] = user_input
                response = "Excellent! I have all your insurance information. Let's proceed with scheduling your appointment."
                state['conversation_history'].append(AIMessage(content=response))
                state['current_step'] = 'scheduling'
                state['waiting_for'] = None
            state['patient_data'] = patient_data
            return state
        
        # If we get here, move to scheduling
        state['current_step'] = 'scheduling'
        return state
    
    def _scheduling_node(self, state: Dict) -> Dict:
        user_input = state.get('user_input', '').strip()
        patient_data = state.get('patient_data', {})
        
        # Check if we need to show appointment options
        if not state.get('suggestions'):
            suggestions = self.scheduler.suggest_appointment_times(patient_data)
            
            if suggestions['suggestions']:
                response = f"Great! I found some available appointment times for you. "
                
                if suggestions['is_new_patient']:
                    response += f"As a new patient, your appointment will be {suggestions['duration']} minutes long. "
                else:
                    response += f"As a returning patient, your appointment will be {suggestions['duration']} minutes long. "
                
                response += "Here are some available options:\n\n"
                
                for i, suggestion in enumerate(suggestions['suggestions'][:3], 1):
                    response += f"{i}. {suggestion['doctor_name']} - {suggestion['date']}\n"
                    for time_slot in suggestion['available_times'][:2]:
                        response += f"   - {time_slot.split()[1]}\n"
                    response += "\n"
                
                response += "Please let me know which option you prefer, or if you'd like to see more options."
                
                state['conversation_history'].append(AIMessage(content=response))
                state['suggestions'] = suggestions['suggestions']
                state['waiting_for'] = 'appointment_selection'
            else:
                response = "I'm sorry, but I don't see any available appointments in the next few weeks. Please contact our office directly for assistance."
                state['conversation_history'].append(AIMessage(content=response))
                state['current_step'] = 'completion'
        
        # Handle appointment selection
        elif state.get('waiting_for') == 'appointment_selection':
            # Parse user selection
            selected_appointment = self._parse_appointment_selection(user_input, state.get('suggestions', []))
            
            if selected_appointment:
                state['appointment_data'] = selected_appointment
                response = f"Great! I've selected:\n\n"
                response += f"Doctor: {selected_appointment['doctor_name']}\n"
                response += f"Date: {selected_appointment['appointment_date']}\n"
                response += f"Time: {selected_appointment['appointment_time']}\n"
                response += f"Duration: {selected_appointment['duration']} minutes\n\n"
                response += "Would you like to confirm this appointment? Please say 'yes' to confirm or 'no' to cancel."
                
                state['conversation_history'].append(AIMessage(content=response))
                state['current_step'] = 'confirmation'
                state['waiting_for'] = None
            else:
                response = "I didn't understand your selection. Please choose from the available options (1, 2, or 3) or specify the doctor and time clearly."
                state['conversation_history'].append(AIMessage(content=response))
        
        return state
    
    def _parse_appointment_selection(self, user_input: str, suggestions: List[Dict]) -> Optional[Dict]:
        """Parse user input to select an appointment from suggestions"""
        user_input = user_input.lower().strip()
        
        # Check for option numbers (1, 2, 3)
        if user_input in ['1', 'option 1', 'first']:
            if len(suggestions) > 0:
                suggestion = suggestions[0]
                return {
                    'doctor_name': suggestion['doctor_name'],
                    'appointment_date': suggestion['date'],
                    'appointment_time': suggestion['available_times'][0].split()[1],
                    'duration': 60 if suggestion.get('is_new_patient', True) else 30
                }
        elif user_input in ['2', 'option 2', 'second']:
            if len(suggestions) > 1:
                suggestion = suggestions[1]
                return {
                    'doctor_name': suggestion['doctor_name'],
                    'appointment_date': suggestion['date'],
                    'appointment_time': suggestion['available_times'][0].split()[1],
                    'duration': 60 if suggestion.get('is_new_patient', True) else 30
                }
        elif user_input in ['3', 'option 3', 'third']:
            if len(suggestions) > 2:
                suggestion = suggestions[2]
                return {
                    'doctor_name': suggestion['doctor_name'],
                    'appointment_date': suggestion['date'],
                    'appointment_time': suggestion['available_times'][0].split()[1],
                    'duration': 60 if suggestion.get('is_new_patient', True) else 30
                }
        
        # Check for doctor names and times
        for suggestion in suggestions:
            doctor_name = suggestion['doctor_name'].lower()
            if any(name_part in user_input for name_part in doctor_name.split()):
                # Check for time mentions
                for time_slot in suggestion['available_times']:
                    time_part = time_slot.split()[1].lower()
                    if time_part in user_input or any(t in user_input for t in ['9', '11', '2', 'am', 'pm']):
                        return {
                            'doctor_name': suggestion['doctor_name'],
                            'appointment_date': suggestion['date'],
                            'appointment_time': time_slot.split()[1],
                            'duration': 60 if suggestion.get('is_new_patient', True) else 30
                        }
        
        return None
    
    def _confirmation_node(self, state: Dict) -> Dict:
        user_input = state.get('user_input', '').strip().lower()
        patient_data = state.get('patient_data', {})
        appointment_data = state.get('appointment_data', {})
        
        if 'yes' in user_input or 'confirm' in user_input or 'book' in user_input:
            # First, save the patient to the database if they don't have a patient_id
            if 'patient_id' not in patient_data:
                # Save patient to database
                saved_patient = self.db.add_patient(patient_data)
                if saved_patient:
                    patient_data['patient_id'] = saved_patient['patient_id']
                    state['patient_data'] = patient_data
            
            # Now book the appointment
            booking_result = self.scheduler.book_appointment(patient_data, appointment_data)
            
            if booking_result['success']:
                appointment_data['appointment_id'] = booking_result['appointment_id']
                # Ensure appointment_type is present for email templates
                if 'appointment_type' not in appointment_data:
                    appointment_data['appointment_type'] = 'new_patient' if patient_data.get('is_new_patient', True) else 'returning_patient'
                state['appointment_data'] = appointment_data
                
                # Send confirmation email/SMS immediately
                delivery_notes: List[str] = []
                try:
                    delivery_results = self.messaging_service.send_appointment_confirmation(patient_data, appointment_data)
                    if isinstance(delivery_results, dict):
                        email_res = delivery_results.get('email')
                        if isinstance(email_res, dict):
                            delivery_notes.append(f"Email: {'sent' if email_res.get('success') else 'failed'}")
                        sms_res = delivery_results.get('sms')
                        if isinstance(sms_res, dict):
                            # In simulation mode this is success with a message
                            delivery_notes.append(f"SMS: {'sent' if sms_res.get('success') else 'failed'}")
                except Exception as _:
                    delivery_notes.append("Email/SMS dispatch encountered an error")

                response = f"Perfect! Your appointment has been booked successfully!\n\n"
                response += f"Appointment ID: {appointment_data['appointment_id']}\n"
                response += f"Patient ID: {patient_data['patient_id']}\n"
                response += f"Doctor: {appointment_data['doctor_name']}\n"
                response += f"Date: {appointment_data['appointment_date']}\n"
                response += f"Time: {appointment_data['appointment_time']}\n"
                response += f"Duration: {appointment_data['duration']} minutes\n\n"
                if delivery_notes:
                    response += "Delivery Status: " + ", ".join(delivery_notes) + "\n\n"
                response += "You will receive a confirmation email and SMS shortly."
                
                state['conversation_history'].append(AIMessage(content=response))
                state['current_step'] = 'form_distribution'
            else:
                response = f"I'm sorry, there was an issue booking your appointment: {booking_result['message']}"
                state['conversation_history'].append(AIMessage(content=response))
                state['current_step'] = 'completion'
        else:
            response = "Would you like to confirm this appointment? Please say 'yes' to confirm or 'no' to cancel."
            state['conversation_history'].append(AIMessage(content=response))
        
        return state
    
    def _form_distribution_node(self, state: Dict) -> Dict:
        patient_data = state.get('patient_data', {})
        appointment_data = state.get('appointment_data', {})
        
        if patient_data.get('is_new_patient', True) and patient_data.get('email'):
            form_result = self.messaging_service.send_new_patient_form(patient_data, appointment_data)
            
            if form_result['success']:
                response = "I've also sent you the new patient intake form via email. Please complete it before your appointment."
            else:
                response = "I tried to send you the intake form, but there was an issue. Please contact our office for a copy."
            
            state['conversation_history'].append(AIMessage(content=response))
        
        state['current_step'] = 'completion'
        return state
    
    def _completion_node(self, state: Dict) -> Dict:
        response = "Thank you for using our scheduling system! If you have any questions or need to make changes, please don't hesitate to contact us. Have a great day!"
        state['conversation_history'].append(AIMessage(content=response))
        state['current_step'] = 'completed'
        return state
    
    def _route_after_greeting(self, state: Dict) -> str:
        return "patient_lookup"
    
    def _route_after_lookup(self, state: Dict) -> str:
        if state.get('patient_data') and not state['patient_data'].get('patient_id'):
            return "patient_intake"
        else:
            return "insurance_collection"
    
    def _route_after_intake(self, state: Dict) -> str:
        return "insurance_collection"
    
    def _route_after_insurance(self, state: Dict) -> str:
        return "scheduling"
    
    def _route_after_scheduling(self, state: Dict) -> str:
        return "confirmation"
    
    def _route_after_confirmation(self, state: Dict) -> str:
        if state.get('appointment_data', {}).get('appointment_id'):
            return "form_distribution"
        else:
            return "completion"
    
    def process_message(self, user_input: str, session_id: str = None) -> str:
        if session_id:
            self.conversation_state['session_id'] = session_id
        
        self.conversation_state['user_input'] = user_input
        self.conversation_state['conversation_history'].append(HumanMessage(content=user_input))
        
        try:
            # Handle the conversation flow manually for better control
            current_step = self.conversation_state.get('current_step', 'greeting')
            
            if current_step == 'greeting':
                result = self._greeting_node(self.conversation_state)
            elif current_step == 'patient_lookup':
                result = self._patient_lookup_node(self.conversation_state)
            elif current_step == 'patient_intake':
                result = self._patient_intake_node(self.conversation_state)
            elif current_step == 'insurance_collection':
                result = self._insurance_collection_node(self.conversation_state)
            elif current_step == 'scheduling':
                result = self._scheduling_node(self.conversation_state)
            elif current_step == 'confirmation':
                result = self._confirmation_node(self.conversation_state)
            elif current_step == 'form_distribution':
                result = self._form_distribution_node(self.conversation_state)
            elif current_step == 'completion':
                result = self._completion_node(self.conversation_state)
            else:
                result = self._greeting_node(self.conversation_state)
            
            self.conversation_state = result
            last_message = result['conversation_history'][-1].content
            return last_message
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again or contact our office for assistance."
    
    def reset_conversation(self):
        self.conversation_state = {
            'current_step': 'greeting',
            'patient_data': {},
            'insurance_data': {},
            'appointment_data': {},
            'conversation_history': [],
            'waiting_for': None,
            'session_id': None,
            'greeting_shown': False
        }
        self.patient_intake.reset_intake()
        self.insurance_collector.reset_insurance_collection()
