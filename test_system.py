#!/usr/bin/env python3

import sys
import os
from datetime import datetime

def test_imports():
    """Test that all modules can be imported successfully"""
    print("Testing imports...")
    
    try:
        from database import PatientDatabase
        print("✓ Database module imported successfully")
    except Exception as e:
        print(f"✗ Database import failed: {e}")
        return False
    
    try:
        from patient_intake import PatientIntake
        print("✓ Patient intake module imported successfully")
    except Exception as e:
        print(f"✗ Patient intake import failed: {e}")
        return False
    
    try:
        from insurance_collection import InsuranceCollector
        print("✓ Insurance collection module imported successfully")
    except Exception as e:
        print(f"✗ Insurance collection import failed: {e}")
        return False
    
    try:
        from scheduling import SmartScheduler
        print("✓ Scheduling module imported successfully")
    except Exception as e:
        print(f"✗ Scheduling import failed: {e}")
        return False
    
    try:
        from messaging import MessagingService
        print("✓ Messaging module imported successfully")
    except Exception as e:
        print(f"✗ Messaging import failed: {e}")
        return False
    
    try:
        from reminder_system import ReminderSystem
        print("✓ Reminder system module imported successfully")
    except Exception as e:
        print(f"✗ Reminder system import failed: {e}")
        return False
    
    try:
        from ai_agent import ClinicSchedulingAgent
        print("✓ AI agent module imported successfully")
    except Exception as e:
        print(f"✗ AI agent import failed: {e}")
        return False
    
    return True

def test_database():
    """Test database functionality"""
    print("\nTesting database...")
    
    try:
        from database import PatientDatabase
        db = PatientDatabase()
        
        # Test patient lookup
        patients = db.patients_df
        print(f"✓ Loaded {len(patients)} patients")
        
        # Test doctor lookup
        doctors = db.get_doctors()
        print(f"✓ Loaded {len(doctors)} doctors")
        
        # Test schedule lookup
        schedule = db.schedule_df
        print(f"✓ Loaded {len(schedule)} schedule entries")
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_patient_intake():
    """Test patient intake functionality"""
    print("\nTesting patient intake...")
    
    try:
        from database import PatientDatabase
        from patient_intake import PatientIntake
        
        db = PatientDatabase()
        intake = PatientIntake(db)
        
        # Test name validation
        valid, msg = intake.validate_name("John Doe")
        if valid:
            print("✓ Name validation works")
        else:
            print(f"✗ Name validation failed: {msg}")
            return False
        
        # Test date validation
        valid, msg = intake.validate_date_of_birth("1990-01-01")
        if valid:
            print("✓ Date validation works")
        else:
            print(f"✗ Date validation failed: {msg}")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Patient intake test failed: {e}")
        return False

def test_insurance_collection():
    """Test insurance collection functionality"""
    print("\nTesting insurance collection...")
    
    try:
        from insurance_collection import InsuranceCollector
        
        collector = InsuranceCollector()
        
        # Test carrier validation
        valid, msg = collector.validate_insurance_carrier("Blue Cross Blue Shield")
        if valid:
            print("✓ Insurance carrier validation works")
        else:
            print(f"✗ Insurance carrier validation failed: {msg}")
            return False
        
        # Test member ID validation
        valid, msg = collector.validate_member_id("ABC123456")
        if valid:
            print("✓ Member ID validation works")
        else:
            print(f"✗ Member ID validation failed: {msg}")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Insurance collection test failed: {e}")
        return False

def test_scheduling():
    """Test scheduling functionality"""
    print("\nTesting scheduling...")
    
    try:
        from database import PatientDatabase
        from scheduling import SmartScheduler
        
        db = PatientDatabase()
        scheduler = SmartScheduler(db)
        
        # Test available slots
        doctors = db.get_doctors()
        if doctors:
            doctor_name = doctors[0]['name']
            slots = scheduler.get_available_slots(doctor_name)
            print(f"✓ Found {len(slots)} available slots for {doctor_name}")
        
        return True
    except Exception as e:
        print(f"✗ Scheduling test failed: {e}")
        return False

def test_ai_agent():
    """Test AI agent functionality"""
    print("\nTesting AI agent...")
    
    try:
        from ai_agent import ClinicSchedulingAgent
        
        agent = ClinicSchedulingAgent()
        
        # Test initial greeting
        response = agent.process_message("Hello")
        if response and len(response) > 10:
            print("✓ AI agent responds to greetings")
        else:
            print("✗ AI agent greeting failed")
            return False
        
        return True
    except Exception as e:
        print(f"✗ AI agent test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏥 AI Healthcare Scheduling Agent - System Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_database,
        test_patient_intake,
        test_insurance_collection,
        test_scheduling,
        test_ai_agent
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("Test failed, stopping...")
            break
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nTo start the application, run:")
        print("streamlit run app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
