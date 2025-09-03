# AI Healthcare Scheduling Agent – In-Depth Explanation

## Overview
An AI-driven receptionist for clinics that greets patients, collects demographics and insurance, finds the right slot, confirms via email/SMS, and sends reminders. It uses a modular Python backend with a Streamlit UI and a LangGraph-powered conversational agent.

---

## Tech Stack
- Programming language: Python 3.10+
- Frontend/UI: Streamlit
- AI Orchestration: LangGraph + LangChain message schema
- Data Layer: CSV (patients, doctors, appointments) + Excel (doctor schedules)
- Messaging: Gmail SMTP (email), Twilio (SMS, simulated if creds missing)
- Configuration: dotenv-based environment variables (`config.py`)
- Visualization: Streamlit charts

Why this stack:
- Rapid development and demo-friendly
- Deterministic behavior with file-backed storage
- Swappable messaging backends (simulated vs. real)
- Clear, testable modules

---

## System Architecture
- `app.py`: Streamlit app with 4 tabs: Chat, Dashboard, Appointments, Admin
- `ai_agent.py`: Conversation engine implemented as nodes (greeting → lookup → intake → insurance → scheduling → confirmation → forms → completion)
- `database.py`: Lightweight data layer for CSV/Excel read/write
- `patient_intake.py`: Validation for name/DOB/phone/email and optional doctor
- `insurance_collection.py`: Validation for carrier/member ID/group number
- `scheduling.py`: Suggests slots and books appointments, prevents conflicts
- `messaging.py`: Email and SMS services; confirmation and reminders
- `reminder_system.py`: Sends reminders and logs outcomes to `data/reminder_log.csv`
- `data_generator.py`: Generates synthetic patients/doctors and 30-day schedules

Data files in `data/`:
- `patients.csv`, `doctors.csv`, `appointments.csv`, `doctor_schedules.xlsx`, `reminder_log.csv`

Resource files:
- `resources/New Patient Intake Form.pdf`

---

## End-to-End Flow
1) User opens Streamlit (`app.py`) and chats with the assistant.
2) `ClinicSchedulingAgent` in `ai_agent.py` manages steps and state.
3) Patient lookup: `database.find_patient` checks `patients.csv` by name.
4) If new: `patient_intake.py` collects/validates DOB → optional phone/email/doctor.
5) Insurance: `insurance_collection.py` collects carrier/member ID/(optional) group.
6) Scheduling: `scheduling.SmartScheduler.suggest_appointment_times` reads Excel schedule and suggests the next business day slots. Patient selects one.
7) Confirmation: `SmartScheduler.book_appointment` → `database.book_appointment` writes to `appointments.csv` and marks slot unavailable in Excel.
8) Messaging: `messaging.MessagingService` sends email/SMS confirmations; new patients get the PDF form by email.
9) Admin: `reminder_system.process_daily_reminders` sends 3-day (forms/simple) and 1-day (confirmation) reminders; logs results.
10) Dashboard/Reports: Streamlit visualizes counts, trends, workload; admin exports CSV.

---

## Module Deep Dive

### app.py
- Caches long-lived services (agent, db, reminders) and renders 4 tabs.
- Chat tab: Maintains `st.session_state` for messages and `conversation_state` across turns.
- Dashboard: KPIs, line and bar charts, recent appointments table.
- Appointments: Search by patient ID, doctor, or date; show type/status breakdown.
- Admin: One-click daily reminders, reminder report, CSV exports, and test email.

### ai_agent.py
- Finite-state conversation modeled with node functions:
  - greeting → patient_lookup → patient_intake → insurance_collection → scheduling → confirmation → form_distribution → completion
- State keys: `current_step`, `patient_data`, `appointment_data`, `waiting_for`, `conversation_history`, `session_id`.
- Selection parsing for options and free-form time/doctor mentions.
- On confirm: creates patient if needed, books appointment, triggers messaging, then sends forms for new patients.

### database.py
- Loads `patients.csv`, `doctors.csv`, `doctor_schedules.xlsx`, `appointments.csv`.
- `find_patient(first,last[,dob])`: returns dict with `is_new_patient` derived from `last_visit`.
- `book_appointment(...)`: assigns `APT####`, writes/updates CSV and Excel, flips schedule availability.
- `get_available_slots(doctor[,date])`: filters Excel where `is_available=True`.
- `update_patient_visit(patient_id)`: sets `last_visit`, marks not new.

### patient_intake.py
- Validations:
  - Name: letters/spaces/hyphen/apostrophe
  - DOB: YYYY-MM-DD, sensible age (0–120)
  - Phone: 10 or 11 digits (US)
  - Email: standard regex
  - Doctor: must exist in `doctors.csv`
- Progressive intake with optional fields.

### insurance_collection.py
- Validations:
  - Carrier: fuzzy match against common carriers list
  - Member ID: alphanumeric, ≥6
  - Group number: optional alphanumeric, ≥3

### scheduling.py (SmartScheduler)
- New patient: 60 mins; Returning: 30 mins.
- Filters to future weekdays, clinic hours, avoids lunch.
- Suggests earliest viable slots across doctors for [1,2,3,7,14] days ahead.
- Books and marks Excel slot unavailable, writes appointment row.
- Conflict check helper scans existing confirmed appointments.

### messaging.py
- Email via SMTP; if no credentials, simulates with success messages.
- SMS via Twilio; simulated if Twilio not configured.
- Templates for confirmation, intake forms, and three reminder types.

### reminder_system.py
- For 3 days ahead: new patients receive forms reminder; returning receive simple reminder.
- For 1 day ahead: all receive confirmation reminder.
- Logs to `data/reminder_log.csv` with success flags.
- Generates success rates and counts for the Admin report.

### data_generator.py
- Creates 50 patients, 3 doctors, and a 30-day weekday schedule at 09:00, 11:00, 14:00.
- Outputs `patients.csv`, `doctors.csv`, `doctor_schedules.xlsx`.

---

## Data Model (conceptual)
- Patient: patient_id, first_name, last_name, date_of_birth, phone, email, preferred_doctor, insurance_*, last_visit, is_new_patient
- Doctor: name, specialty, location
- Schedule row: doctor_name, date, time_slot, is_available, patient_id, appointment_type, duration_minutes
- Appointment: appointment_id, patient_id, doctor_name, appointment_date, appointment_time, duration_minutes, appointment_type, status, created_at, insurance_*, phone, email
- Reminder log: appointment_id, patient_id, reminder_type, sent_at, email_success, sms_success, response_received

---

## Configuration and Secrets
- `.env` variables loaded in `config.py`:
  - EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD
  - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
  - OPENAI_API_KEY (future LLM use)
  - DATABASE_URL (not required for CSV/Excel mode)
- If email/SMS creds missing, system simulates sending and continues.

---

## Operational Notes
- Persistence: CSV/Excel ensures state survives restarts.
- Caching: `@st.cache_resource` reduces reload time of services in Streamlit.
- Error handling: User-friendly messages and safe fallbacks.
- Extensibility: Replace file storage with a real DB; plug in EHR/EMR.

---

## Video Walkthrough Script (Ready to Record)

Intro (10–15s)
- "Welcome! This is the AI Healthcare Scheduling Agent that automates patient intake, scheduling, confirmations, and reminders."

Section 1: Launch and UI Tour (30–45s)
- Show terminal: `streamlit run app.py`.
- Browser shows four tabs: Chat, Dashboard, Appointments, Admin.
- "We’ll start in the Chat tab, then review analytics and admin tools."

Section 2: New Patient Booking (90–120s)
- In Chat: type "Hello, I need to schedule an appointment".
- Show greeting and prompt for name; enter a new name (e.g., "John Smith").
- Provide DOB; optionally phone and email; optionally select a preferred doctor.
- Insurance collection: carrier → member ID → optional group.
- Assistant proposes slots; choose option 1.
- Confirm booking; show success with Appointment ID.
- Point out email/SMS confirmation (simulated if no creds) and intake form email for new patients.

Section 3: Dashboard Insights (30–45s)
- Switch to Dashboard tab; show KPIs updating.
- Show Appointment Trends line chart and Doctor Workload bar chart.
- View Recent Appointments table including the newly booked appointment.

Section 4: Appointments Search (20–30s)
- Go to Appointments tab; search by Patient ID from the confirmation.
- Show appointment type/status breakdown.

Section 5: Admin Reminders and Reports (45–60s)
- Open Admin tab.
- Click "Send Daily Reminders"; narrate three-day forms/simple and one-day confirmation reminders.
- Show results list and any simulated messages.
- Click "Generate Reminder Report"; explain success rates and counts.
- Demonstrate CSV exports for patients/appointments/schedule.

Section 6: Tech and Architecture Recap (30–45s)
- "Built with Python, Streamlit UI, LangGraph conversation flow, CSV/Excel data, SMTP/Twilio messaging with safe simulation fallbacks. Modular services make it easy to extend and integrate with real EMR systems."

Outro (10–15s)
- "That’s the end-to-end demo. The repository includes docs and tests. Thanks for watching!"

---

## FAQ Talking Points (for the video Q&A)
- What happens without email/SMS creds? Simulated success; no runtime failures.
- How are no-shows reduced? Multi-stage reminders and forms completion nudges.
- How to scale? Swap CSV/Excel for a DB; deploy Streamlit behind a reverse proxy; run reminders as a scheduled job.
- How to integrate EMR? Replace data access in `database.py` and messaging hooks; maintain the same service APIs.

---

## Files Reference – What each file does
- `app.py`: Streamlit UI and user flows
- `ai_agent.py`: Conversational state machine and logic
- `database.py`: File-backed CRUD and schedule persistence
- `patient_intake.py`: Input validation for demographics
- `insurance_collection.py`: Input validation for insurance
- `scheduling.py`: Slot suggestion, conflict check, booking
- `messaging.py`: Email and SMS services and templates
- `reminder_system.py`: Reminder orchestration and logging
- `data_generator.py`: Synthetic data and schedules
- `README.md`: Quick start and features
- `PROJECT_SUMMARY.md`: Delivery status and outcomes
- `USER_GUIDE.md`: Step-by-step user instructions

