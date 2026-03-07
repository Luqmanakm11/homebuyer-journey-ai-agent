import json
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker

# Use default Faker to avoid locale crash
fake = Faker()

# Custom list to maintain the realistic Malaysian vibe for your demo
LOCAL_FIRST_NAMES = ["Ahmad", "Muhammad", "Sarah", "Nurul", "Wei Jie", "Siti", "Amir", "Chong", "Tan", "Fatima", "Karthik", "Priya", "Arif", "Mei Ling", "Muthu", "Aisyah", "Jason", "Michelle"]
LOCAL_LAST_NAMES = ["Bin Abdullah", "Binti Razak", "Wong", "Lee", "Goh", "Lim", "Subramaniam", "Nair", "Bin Osman", "Binti Kassim", "Yeoh"]

# The exact journey stages we mapped out
JOURNEY_STAGES = [
    "1_LOAN_APPROVED",
    "2_SPA_PENDING_SIGNATURE",
    "3_PENDING_ESTAMP",
    "4_CONSTRUCTION_ACTIVE",
    "5_PROGRESSIVE_BILLING_ISSUED",
    "6_READY_FOR_VP",
    "7_COMPLETED"
]

PROJECTS = [
    "Chin Hin Sky Residences", 
    "Solaris Parq", 
    "Avant Space"
]

def generate_mock_data(num_records=1000):
    properties = []
    transactions = []

    print(f"Generating {num_records} homebuyer records...")

    for i in range(num_records):
        # 1. Generate Property Unit Data
        project_name = random.choice(PROJECTS)
        unit_id = f"{project_name[:3].upper()}-{random.randint(10, 99)}-{random.randint(100, 999)}"
        purchase_price = round(random.uniform(400000.0, 1200000.0), 2)
        
        # Pick a random journey stage
        stage_index = random.randint(0, len(JOURNEY_STAGES) - 1)
        current_stage = JOURNEY_STAGES[stage_index]

        # Logic to determine construction percentage based on stage
        if stage_index < 3:
            construction_pct = 0
        elif stage_index == 3:
            construction_pct = random.randint(10, 80)
        elif stage_index == 4:
            construction_pct = random.randint(20, 90)
        else:
            construction_pct = 100

        property_data = {
            "unit_id": unit_id,
            "project_name": project_name,
            "purchase_price": purchase_price,
            "construction_percentage": construction_pct,
            "latest_architect_cert_url": f"https://mockstorage.blob.core.windows.net/certs/{unit_id}_cert.pdf" if construction_pct > 0 else None
        }
        properties.append(property_data)

        # 2. Generate Homebuyer Transaction Data
        transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        
        # Generate a local name
        buyer_name = f"{random.choice(LOCAL_FIRST_NAMES)} {random.choice(LOCAL_LAST_NAMES)}"
        
        # Logic to fill milestones realistically based on their current stage
        milestones = {
            "loan_approved_date": (datetime.now() - timedelta(days=random.randint(100, 300))).strftime("%Y-%m-%d"),
            "lawyer_appointed": stage_index >= 1,
            "spa_generated_url": f"https://mockstorage.blob.core.windows.net/spas/{transaction_id}_spa.pdf" if stage_index >= 1 else None,
            "is_spa_signed": stage_index >= 2,
            "idsaya_transaction_id": f"IDS-{uuid.uuid4().hex[:6].upper()}" if stage_index >= 2 else None,
            "is_spa_stamped": stage_index >= 3,
            "lhdn_certificate_no": f"LHDN-{random.randint(10000, 99999)}" if stage_index >= 3 else None,
            "outstanding_billing_amount": round(purchase_price * 0.10, 2) if current_stage == "5_PROGRESSIVE_BILLING_ISSUED" else 0.00,
            "bank_payment_released": stage_index >= 6
        }

        # Use faker for realistic looking phone numbers and emails
        transaction_data = {
            "transaction_id": transaction_id,
            "buyer_id": f"USER-{random.randint(1000, 9999)}",
            "buyer_name": buyer_name,
            "buyer_phone": f"+601{random.randint(10000000, 99999999)}", # Format like +60123456789
            "buyer_email": fake.email(),
            "unit_id": unit_id,
            "current_stage": current_stage,
            "milestones": milestones
        }
        transactions.append(transaction_data)

    # 3. Save to JSON files
    with open("mock_properties.json", "w") as f:
        json.dump(properties, f, indent=4)
        
    with open("mock_transactions.json", "w") as f:
        json.dump(transactions, f, indent=4)

    print("Success! Created 'mock_properties.json' and 'mock_transactions.json'.")

if __name__ == "__main__":
    generate_mock_data(1000)