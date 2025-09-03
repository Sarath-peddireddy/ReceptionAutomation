import pandas as pd
import random
from datetime import datetime, timedelta
import csv

def generate_synthetic_patients():
    first_names = [
        "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Jessica",
        "William", "Ashley", "James", "Amanda", "Christopher", "Jennifer", "Daniel",
        "Lisa", "Matthew", "Nancy", "Anthony", "Karen", "Mark", "Betty", "Donald",
        "Helen", "Steven", "Sandra", "Paul", "Donna", "Andrew", "Carol", "Joshua",
        "Ruth", "Kenneth", "Sharon", "Kevin", "Michelle", "Brian", "Laura", "George",
        "Sarah", "Edward", "Kimberly", "Ronald", "Deborah", "Timothy", "Dorothy",
        "Jason", "Amy", "Jeffrey", "Angela"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
        "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
        "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell",
        "Mitchell", "Carter", "Roberts"
    ]
    
    doctors = [
        {"name": "Dr. Sarah Johnson", "specialty": "Allergist", "location": "Downtown Clinic"},
        {"name": "Dr. Amit Patel", "specialty": "Pulmonologist", "location": "Midtown Clinic"},
        {"name": "Dr. Emily Carter", "specialty": "ENT Specialist", "location": "Uptown Clinic"}
    ]
    
    insurance_carriers = [
        "Blue Cross Blue Shield", "Aetna", "Cigna", "UnitedHealthcare", "Humana",
        "Kaiser Permanente", "Medicare", "Medicaid", "Anthem", "Molina Healthcare"
    ]
    
    patients = []
    
    for i in range(50):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        dob = datetime.now() - timedelta(days=random.randint(18*365, 80*365))
        
        patient = {
            "patient_id": f"P{1000 + i:04d}",
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": dob.strftime("%Y-%m-%d"),
            "phone": f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "email": f"{first_name.lower()}.{last_name.lower()}@email.com",
            "preferred_doctor": random.choice(doctors)["name"],
            "insurance_carrier": random.choice(insurance_carriers),
            "insurance_member_id": f"INS{random.randint(100000, 999999)}",
            "insurance_group_number": f"GRP{random.randint(1000, 9999)}",
            "last_visit": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d") if random.random() > 0.3 else None,
            "is_new_patient": random.random() > 0.7
        }
        patients.append(patient)
    
    return patients, doctors

def create_patient_database():
    patients, doctors = generate_synthetic_patients()
    
    df_patients = pd.DataFrame(patients)
    df_patients.to_csv("data/patients.csv", index=False)
    
    df_doctors = pd.DataFrame(doctors)
    df_doctors.to_csv("data/doctors.csv", index=False)
    
    print(f"Generated {len(patients)} patients and {len(doctors)} doctors")
    return patients, doctors

def create_doctor_schedules():
    doctors = [
        {"name": "Dr. Sarah Johnson", "specialty": "Allergist", "location": "Downtown Clinic"},
        {"name": "Dr. Amit Patel", "specialty": "Pulmonologist", "location": "Midtown Clinic"},
        {"name": "Dr. Emily Carter", "specialty": "ENT Specialist", "location": "Uptown Clinic"}
    ]
    
    schedule_data = []
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for doctor in doctors:
        for day_offset in range(30):
            current_date = start_date + timedelta(days=day_offset)
            
            if current_date.weekday() < 5:
                available_slots = [9, 11, 14]
                for hour in available_slots:
                    time_slot = current_date.replace(hour=hour, minute=0)
                    schedule_data.append({
                        "doctor_name": doctor["name"],
                        "date": current_date.strftime("%Y-%m-%d"),
                        "time_slot": time_slot.strftime("%Y-%m-%d %H:%M"),
                        "is_available": True,
                        "patient_id": None,
                        "appointment_type": None,
                        "duration_minutes": None
                    })
    
    df_schedule = pd.DataFrame(schedule_data)
    df_schedule.to_excel("data/doctor_schedules.xlsx", index=False)
    
    print(f"Generated schedule for {len(doctors)} doctors over 30 days")
    return df_schedule

if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    create_patient_database()
    create_doctor_schedules()
