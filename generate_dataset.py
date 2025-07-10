# generate_dataset.py
import csv
import random
from faker import Faker

fake = Faker()

# --- Configuration ---
NUM_PATIENTS = 50
NUM_DOCTORS = 5
TIME_SLOTS = [f"{h:02d}:{m:02d}" for h in range(9, 17) for m in (0, 30)] # 9:00 AM to 4:30 PM
# Example: ['09:00', '09:30', '10:00', ..., '16:30']

MIN_SLOTS_PER_DOCTOR = 8  # Min slots a doctor is available for
MAX_SLOTS_PER_DOCTOR = len(TIME_SLOTS) - 4 # Max slots (e.g., ensure some breaks)

def generate_patients_csv(filename="patients.csv", num_patients=NUM_PATIENTS):
    """Generates a CSV file with patient data."""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['patient_id', 'patient_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(num_patients):
            writer.writerow({
                'patient_id': f'P{i+1:03d}',
                'patient_name': fake.name()
            })
    print(f"Generated {filename} with {num_patients} patients.")

def generate_doctors_csv(filename="doctors.csv", num_doctors=NUM_DOCTORS, time_slots=TIME_SLOTS):
    """Generates a CSV file with doctor data and their availability."""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['doctor_id', 'doctor_name', 'available_slots']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(num_doctors):
            num_available_slots = random.randint(MIN_SLOTS_PER_DOCTOR, MAX_SLOTS_PER_DOCTOR)
            available_slots = sorted(random.sample(time_slots, num_available_slots))
            writer.writerow({
                'doctor_id': f'D{i+1:02d}',
                'doctor_name': f"Dr. {fake.last_name()}",
                'available_slots': ";".join(available_slots) # Semicolon-separated
            })
    print(f"Generated {filename} with {num_doctors} doctors.")

if __name__ == "__main__":
    generate_patients_csv()
    generate_doctors_csv()
    print("\nSample Time Slots:")
    print(TIME_SLOTS)