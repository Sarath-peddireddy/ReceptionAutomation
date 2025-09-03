import re
from typing import Dict, List, Optional, Tuple

class InsuranceCollector:
    def __init__(self):
        self.insurance_carriers = [
            "Blue Cross Blue Shield", "Aetna", "Cigna", "UnitedHealthcare", "Humana",
            "Kaiser Permanente", "Medicare", "Medicaid", "Anthem", "Molina Healthcare",
            "BCBS", "United Health", "Health Net", "Oscar Health", "Ambetter"
        ]
        self.current_insurance_data = {}
    
    def validate_insurance_carrier(self, carrier: str) -> Tuple[bool, str]:
        if not carrier or not carrier.strip():
            return False, "Insurance carrier is required"
        
        carrier_clean = carrier.strip().title()
        
        for valid_carrier in self.insurance_carriers:
            if carrier_clean.lower() in valid_carrier.lower() or valid_carrier.lower() in carrier_clean.lower():
                return True, valid_carrier
        
        return False, f"Insurance carrier not recognized. Common carriers: {', '.join(self.insurance_carriers[:5])}"
    
    def validate_member_id(self, member_id: str) -> Tuple[bool, str]:
        if not member_id or not member_id.strip():
            return False, "Member ID is required"
        
        member_id_clean = member_id.strip().upper()
        
        if len(member_id_clean) < 6:
            return False, "Member ID must be at least 6 characters long"
        
        if not re.match(r'^[A-Z0-9]+$', member_id_clean):
            return False, "Member ID can only contain letters and numbers"
        
        return True, member_id_clean
    
    def validate_group_number(self, group_number: str) -> Tuple[bool, str]:
        if not group_number or not group_number.strip():
            return True, ""
        
        group_clean = group_number.strip().upper()
        
        if len(group_clean) < 3:
            return False, "Group number must be at least 3 characters long"
        
        if not re.match(r'^[A-Z0-9]+$', group_clean):
            return False, "Group number can only contain letters and numbers"
        
        return True, group_clean
    
    def collect_insurance_info(self, user_input: str) -> Dict:
        response = {
            'status': 'continue',
            'message': '',
            'insurance_data': self.current_insurance_data.copy()
        }
        
        user_input = user_input.strip().lower()
        
        if 'carrier' in user_input or 'insurance' in user_input:
            response['message'] = "Please provide your insurance carrier name:"
            response['waiting_for'] = 'insurance_carrier'
        elif 'member id' in user_input or 'memberid' in user_input or 'id' in user_input:
            response['message'] = "Please provide your insurance member ID:"
            response['waiting_for'] = 'insurance_member_id'
        elif 'group number' in user_input or 'groupnumber' in user_input or 'group' in user_input:
            response['message'] = "Please provide your insurance group number (optional):"
            response['waiting_for'] = 'insurance_group_number'
        else:
            response['message'] = "I need to collect your insurance information:\n- Insurance carrier\n- Member ID\n- Group number (optional)\n\nWhat would you like to provide?"
        
        return response
    
    def process_insurance_field(self, field: str, value: str) -> Dict:
        response = {
            'status': 'continue',
            'message': '',
            'insurance_data': self.current_insurance_data.copy()
        }
        
        if field == 'insurance_carrier':
            is_valid, result = self.validate_insurance_carrier(value)
            if is_valid:
                self.current_insurance_data['insurance_carrier'] = result
                response['message'] = "Great! What's your insurance member ID?"
            else:
                response['message'] = f"Invalid insurance carrier: {result}. Please try again."
        
        elif field == 'insurance_member_id':
            is_valid, result = self.validate_member_id(value)
            if is_valid:
                self.current_insurance_data['insurance_member_id'] = result
                response['message'] = "Perfect! Do you have a group number? (optional)"
            else:
                response['message'] = f"Invalid member ID: {result}. Please try again."
        
        elif field == 'insurance_group_number':
            is_valid, result = self.validate_group_number(value)
            if is_valid:
                if value.strip():
                    self.current_insurance_data['insurance_group_number'] = result
                response['status'] = 'complete'
                response['message'] = "Excellent! I have all your insurance information. Let's proceed with scheduling your appointment."
            else:
                response['message'] = f"Invalid group number: {result}. Please try again."
        
        response['insurance_data'] = self.current_insurance_data.copy()
        return response
    
    def is_insurance_complete(self) -> bool:
        required_fields = ['insurance_carrier', 'insurance_member_id']
        return all(field in self.current_insurance_data for field in required_fields)
    
    def get_insurance_summary(self) -> str:
        if not self.current_insurance_data:
            return "No insurance information collected"
        
        summary = f"Insurance: {self.current_insurance_data.get('insurance_carrier', 'N/A')}\n"
        summary += f"Member ID: {self.current_insurance_data.get('insurance_member_id', 'N/A')}\n"
        
        if self.current_insurance_data.get('insurance_group_number'):
            summary += f"Group Number: {self.current_insurance_data['insurance_group_number']}\n"
        
        return summary.strip()
    
    def reset_insurance_collection(self):
        self.current_insurance_data = {}
    
    def get_missing_insurance_fields(self) -> List[str]:
        required_fields = ['insurance_carrier', 'insurance_member_id']
        return [field for field in required_fields if field not in self.current_insurance_data]
