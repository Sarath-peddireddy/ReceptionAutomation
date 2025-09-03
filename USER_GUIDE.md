# AI Healthcare Scheduling Agent - User Guide

## 🎯 Overview

This guide will walk you through all the features of the AI Healthcare Scheduling Agent with practical examples. The system is designed to automate patient booking, reduce no-shows, and streamline clinic operations.

## 🚀 Getting Started

### Step 1: Launch the Application
```bash
# Activate the virtual environment
clinic_env\Scripts\activate

# Run the application
streamlit run app.py
```

### Step 2: Access the Interface
- Open your browser and go to `http://localhost:8501`
- You'll see the main interface with 4 tabs:
  - 💬 **Chat Interface** - Main patient interaction
  - 📊 **Dashboard** - Clinic statistics and metrics
  - 📅 **Appointments** - Appointment management
  - ⚙️ **Admin** - Administrative functions

---

## 💬 Chat Interface - Main Features

### Feature 1: Patient Greeting & Intake

**What it does:** The AI greets patients and collects their information step-by-step.

**Example Conversation:**

**User Input:** `Hello, I need to schedule an appointment`

**AI Response:**
```
Hello! Welcome to HealthCare Plus Clinic! 

I'm your AI scheduling assistant. I can help you:
- Schedule new appointments
- Reschedule existing appointments
- Collect your information
- Handle insurance details

Are you a new patient or returning patient? Please provide your first and last name to get started.
```

**User Input:** `I am a new patient`

**AI Response:**
```
Great! I'll help you create a new patient record. Please provide your first and last name.
```

**User Input:** `John Smith`

**AI Response:**
```
Thank you, John Smith. Please provide your date of birth (YYYY-MM-DD format).
```

### Feature 2: Patient Information Collection

**What it does:** Collects and validates patient information using NLP.

**Example for New Patient:**

**User Input:** `1990-05-15`

**AI Response:**
```
Great! Would you like to provide your phone number? (optional)
```

**User Input:** `555-123-4567`

**AI Response:**
```
Would you like to provide your email address? (optional)
```

**User Input:** `john.smith@email.com`

**AI Response:**
```
Would you like to select a preferred doctor? (optional)

- Dr. Sarah Johnson (Allergist) - Downtown Clinic
- Dr. Amit Patel (Pulmonologist) - Midtown Clinic
- Dr. Emily Carter (ENT Specialist) - Uptown Clinic
```

**User Input:** `Dr. Sarah Johnson`

**AI Response:**
```
Perfect! I have all the information I need. Let me check if you're a new or returning patient.
```

### Feature 3: Insurance Collection

**What it does:** Collects and validates insurance information.

**Example:**

**User Input:** `I need to provide my insurance`

**AI Response:**
```
I need to collect your insurance information:
- Insurance carrier
- Member ID
- Group number (optional)

What would you like to provide?
```

**User Input:** `Blue Cross Blue Shield`

**AI Response:**
```
Great! What's your insurance member ID?
```

**User Input:** `ABC123456789`

**AI Response:**
```
Perfect! Do you have a group number? (optional)
```

**User Input:** `GRP001`

**AI Response:**
```
Excellent! I have all your insurance information. Let's proceed with scheduling your appointment.
```

### Feature 4: Smart Scheduling

**What it does:** Shows available appointment times based on patient type (new = 60min, returning = 30min).

**Example:**

**AI Response:**
```
Great! I found some available appointment times for you. As a new patient, your appointment will be 60 minutes long. Here are some available options:

1. Dr. Sarah Johnson - 2024-01-15
   - 09:00
   - 11:00

2. Dr. Amit Patel - 2024-01-15
   - 09:00
   - 14:00

3. Dr. Emily Carter - 2024-01-16
   - 09:00
   - 11:00

Please let me know which option you prefer, or if you'd like to see more options.
```

**User Input:** `I'll take option 1 with Dr. Sarah Johnson at 9 AM`

**AI Response:**
```
Would you like to confirm this appointment? Please say 'yes' to confirm or 'no' to cancel.
```

**User Input:** `Yes, confirm`

**AI Response:**
```
Perfect! Your appointment has been booked successfully!

Appointment ID: APT1001
Doctor: Dr. Sarah Johnson
Date: 2024-01-15
Time: 09:00
Duration: 60 minutes

You will receive a confirmation email and SMS shortly.
```

### Feature 5: Form Distribution

**What it does:** Sends New Patient Intake Form to new patients.

**AI Response:**
```
I've also sent you the new patient intake form via email. Please complete it before your appointment.
```

### Feature 6: Appointment Confirmation

**What it does:** Sends confirmation via email and SMS.

**Example Email (simulated):**
```
Subject: Appointment Confirmation - HealthCare Plus Clinic

Dear John Smith,

Your appointment has been confirmed with the following details:

Appointment ID: APT1001
Doctor: Dr. Sarah Johnson
Date: 2024-01-15
Time: 09:00
Duration: 60 minutes
Type: new_patient

Please arrive 15 minutes early for your appointment.
```

---

## 📊 Dashboard - Analytics & Metrics

### What You'll See:

1. **Key Metrics:**
   - Total Patients: 50
   - Total Appointments: [Number of bookings]
   - Confirmed Appointments: [Active bookings]
   - New Patients: [Count of new patients]

2. **Charts:**
   - **Appointment Trends:** Line chart showing appointments over time
   - **Doctor Workload:** Bar chart showing appointments per doctor

3. **Recent Appointments Table:**
   - Shows last 10 appointments with details

### Example Data You'll See:
```
Appointment ID | Patient ID | Doctor Name | Date | Time | Status
APT1001 | P1001 | Dr. Sarah Johnson | 2024-01-15 | 09:00 | confirmed
APT1002 | P1002 | Dr. Amit Patel | 2024-01-15 | 11:00 | confirmed
```

---

## 📅 Appointments - Management Features

### Feature 1: Search Appointments

**Search by Patient ID:**
1. Select "Patient ID" from dropdown
2. Enter: `P1001`
3. View all appointments for that patient

**Search by Doctor:**
1. Select "Doctor" from dropdown
2. Choose: `Dr. Sarah Johnson`
3. View all appointments for that doctor

**Search by Date:**
1. Select "Date" from dropdown
2. Pick a date: `2024-01-15`
3. View all appointments on that date

### Feature 2: Appointment Statistics

**What you'll see:**
- Bar chart of appointment types (new_patient vs returning_patient)
- Status breakdown:
  - confirmed: 15
  - pending: 3
  - cancelled: 1

---

## ⚙️ Admin Panel - Administrative Functions

### Feature 1: Send Reminders

**What it does:** Sends automated reminders to patients.

**How to use:**
1. Click "Send Daily Reminders" button
2. System processes reminders for:
   - Appointments in 3 days (forms reminder for new patients)
   - Appointments in 1 day (confirmation reminder)

**Example Output:**
```
Reminders processed!

Simple Reminders Sent:
- Jane Doe: SMS would be sent to 555-987-6543: Reminder: Appointment on 2024-01-18 at 09:00 with Dr. Sarah Johnson. HealthCare Plus Clinic (simulated)

Forms Reminders Sent:
- John Smith: Email would be sent to john.smith@email.com (simulated)

Confirmation Reminders Sent:
- Bob Johnson: SMS would be sent to 555-456-7890: Please confirm your appointment tomorrow at 14:00 with Dr. Amit Patel. Reply YES to confirm. HealthCare Plus Clinic (simulated)
```

### Feature 2: Generate Reports

**What it does:** Creates reminder effectiveness reports.

**How to use:**
1. Click "Generate Reminder Report" button

**Example Output:**
```
Reminder Statistics:
- Total Reminders Sent: 25
- Email Success Rate: 100.0%
- SMS Success Rate: 100.0%
- Response Rate: 85.0%

Reminder Types:
- simple: 10
- forms: 8
- confirmation: 7
```

### Feature 3: Data Export

**What it does:** Exports data to CSV files.

**Available Exports:**
1. **Export Patients:** Downloads `patients_20240115.csv`
2. **Export Appointments:** Downloads `appointments_20240115.csv`
3. **Export Schedule:** Downloads `schedule_20240115.csv`

---

## 🧪 Testing All Features - Complete Workflow

### Test Scenario 1: New Patient Booking

1. **Start Chat:**
   - Input: `Hello, I need to schedule an appointment`

2. **Indicate New Patient:**
   - Input: `I am a new patient`

3. **Provide Information:**
   - Input: `Sarah Johnson`
   - Input: `1985-03-20`
   - Input: `555-999-8888`
   - Input: `sarah.johnson@email.com`
   - Input: `Dr. Emily Carter`

3. **Provide Insurance:**
   - Input: `Aetna`
   - Input: `AET789456123`
   - Input: `GRP002`

4. **Book Appointment:**
   - Select from available options
   - Input: `Yes, confirm`

5. **Check Results:**
   - Go to Dashboard tab to see new appointment
   - Go to Appointments tab to search for your booking

### Test Scenario 2: Returning Patient Booking

1. **Start Chat:**
   - Input: `Hello, I need an appointment`

2. **Provide Name:**
   - Input: `Michael Brown` (existing patient in database)

3. **Provide Insurance:**
   - Input: `UnitedHealthcare`
   - Input: `UHC456789123`

4. **Book Appointment:**
   - Select from available options (30-minute slot)
   - Input: `Yes, confirm`

### Test Scenario 3: Admin Functions

1. **Send Reminders:**
   - Go to Admin tab
   - Click "Send Daily Reminders"
   - Observe the results

2. **Generate Reports:**
   - Click "Generate Reminder Report"
   - Review the statistics

3. **Export Data:**
   - Click "Export Patients"
   - Download and open the CSV file

---

## 🔍 Where to See Results

### 1. Chat Interface Results:
- **Conversation History:** All interactions are saved in the chat
- **Appointment Confirmation:** Shows appointment ID and details
- **Email/SMS Status:** Shows if confirmations were sent

### 2. Dashboard Results:
- **Metrics:** Updated in real-time
- **Charts:** Visual representation of data
- **Recent Appointments:** Latest bookings

### 3. Appointments Tab Results:
- **Search Results:** Filtered appointment data
- **Statistics:** Appointment type and status breakdowns

### 4. Admin Tab Results:
- **Reminder Status:** Shows which reminders were sent
- **Report Data:** Success rates and statistics
- **Export Files:** Downloaded CSV files

---

## 🎯 Key Features to Test

### ✅ Must-Test Features:

1. **New Patient Flow:**
   - Complete patient intake
   - Insurance collection
   - 60-minute appointment booking
   - Form distribution

2. **Returning Patient Flow:**
   - Patient lookup
   - Insurance update
   - 30-minute appointment booking

3. **Admin Functions:**
   - Send reminders
   - Generate reports
   - Export data

4. **Data Validation:**
   - Try invalid dates: `2025-13-45`
   - Try invalid phone: `123`
   - Try invalid email: `not-an-email`

### ✅ Expected Behaviors:

- **Error Handling:** System provides helpful error messages
- **Data Persistence:** All data is saved and retrievable
- **Real-time Updates:** Dashboard updates immediately after bookings
- **Professional Communication:** All messages are professional and clear

---

## 🚨 Troubleshooting

### Common Issues:

1. **"Streamlit not recognized":**
   - Make sure virtual environment is activated
   - Run: `clinic_env\Scripts\activate`

2. **Import Errors:**
   - Ensure all dependencies are installed
   - Run: `pip install -r requirements.txt`

3. **No Data Showing:**
   - Regenerate data: `python data_generator.py`

4. **Email/SMS Not Working:**
   - Check `.env` file configuration
   - System will simulate if credentials not provided

---

## 📱 Sample Data for Testing

### Existing Patients in Database:
- **Michael Brown** - Returning patient
- **Jennifer Davis** - Returning patient
- **Robert Wilson** - New patient

### Available Doctors:
- **Dr. Sarah Johnson** - Allergist - Downtown Clinic
- **Dr. Amit Patel** - Pulmonologist - Midtown Clinic
- **Dr. Emily Carter** - ENT Specialist - Uptown Clinic

### Available Time Slots:
- **9:00 AM** - All doctors
- **11:00 AM** - All doctors
- **2:00 PM** - All doctors

---

## 🎉 Success Indicators

You'll know the system is working correctly when:

1. ✅ **Chat flows naturally** from greeting to confirmation
2. ✅ **Data validation works** (rejects invalid inputs)
3. ✅ **Appointments are booked** with correct durations
4. ✅ **Dashboard updates** in real-time
5. ✅ **Admin functions work** (reminders, reports, exports)
6. ✅ **All tabs are functional** and show relevant data

---

**Happy Testing! 🏥✨**

This system is designed to make healthcare scheduling efficient and user-friendly. Each feature has been carefully crafted to provide a seamless experience for both patients and clinic staff.
