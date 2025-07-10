# optimizer.py
import pandas as pd
from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpStatus

# Define standard time slots globally or pass them around
# This must match the slots used in generate_dataset.py
STANDARD_TIME_SLOTS = [f"{h:02d}:{m:02d}" for h in range(9, 17) for m in (0, 30)]

def solve_schedule(patients_df, doctors_df, time_slots=STANDARD_TIME_SLOTS):
    """
    Optimizes patient scheduling using Linear Programming.

    Args:
        patients_df (pd.DataFrame): DataFrame with 'patient_id'.
        doctors_df (pd.DataFrame): DataFrame with 'doctor_id' and 'available_slots' (semicolon-separated string).
        time_slots (list): List of all possible time slots for scheduling.

    Returns:
        tuple: (schedule_df, unscheduled_patients_df, status_text)
               schedule_df: DataFrame of scheduled appointments ['patient_id', 'doctor_id', 'time_slot'].
               unscheduled_patients_df: DataFrame of patients who couldn't be scheduled.
               status_text: Status of the optimization (e.g., "Optimal", "Infeasible").
    """
    # --- Data Preparation ---
    patients = patients_df['patient_id'].tolist()
    
    doctors_avail = {}
    for _, row in doctors_df.iterrows():
        doc_id = row['doctor_id']
        # Ensure 'available_slots' is a string before splitting, handle NaN/None
        if pd.notna(row['available_slots']) and isinstance(row['available_slots'], str):
            avail_slots = row['available_slots'].split(';')
            doctors_avail[doc_id] = [slot for slot in avail_slots if slot in time_slots] # Filter valid slots
        else:
            doctors_avail[doc_id] = []


    # --- LP Model Initialization ---
    model = LpProblem("PatientScheduling", LpMaximize)

    # --- Decision Variables ---
    # x[p, d, t] = 1 if patient p is scheduled with doctor d at time t, 0 otherwise
    schedule_vars = LpVariable.dicts("Schedule",
                                     ((p, d, t) for p in patients for d in doctors_avail for t in doctors_avail[d]),
                                     cat='Binary')

    # --- Objective Function: Maximize the number of scheduled appointments ---
    model += lpSum(schedule_vars[p, d, t] for p in patients for d in doctors_avail for t in doctors_avail[d] if (p,d,t) in schedule_vars), "TotalScheduledAppointments"

    # --- Constraints ---
    # 1. Each patient can be scheduled at most once
    for p in patients:
        model += lpSum(schedule_vars[p, d, t] for d in doctors_avail for t in doctors_avail[d] if (p,d,t) in schedule_vars) <= 1, f"Patient_{p}_Once"

    # 2. Each doctor can see at most one patient per available time slot
    for d in doctors_avail:
        for t in doctors_avail[d]: # Only for slots where the doctor is available
            model += lpSum(schedule_vars[p, d, t] for p in patients if (p,d,t) in schedule_vars) <= 1, f"Doctor_{d}_Slot_{t.replace(':','_')}_Capacity"
            
    # --- Solve the LP ---
    # You might need to specify a solver, e.g., model.solve(PULP_CBC_CMD(msg=False))
    # If no solver is specified, PuLP will try to use a default one (CBC, GLPK, etc.)
    # Make sure you have one installed: pip install pulp, and then potentially a solver like `sudo apt-get install coinor-cbc glpk-utils`
    model.solve()
    status_text = LpStatus[model.status]

    # --- Extract Results ---
    scheduled_appointments = []
    if model.status == 1: # Optimal
        for p in patients:
            for d in doctors_avail:
                for t in doctors_avail[d]:
                    if (p,d,t) in schedule_vars and schedule_vars[p, d, t].varValue > 0.5: # Check if scheduled
                        scheduled_appointments.append({
                            'patient_id': p,
                            'doctor_id': d,
                            'time_slot': t
                        })
    
    schedule_df = pd.DataFrame(scheduled_appointments)
    
    # Identify unscheduled patients
    if not schedule_df.empty:
        scheduled_patient_ids = set(schedule_df['patient_id'])
    else:
        scheduled_patient_ids = set()
        
    all_patient_ids = set(patients_df['patient_id'])
    unscheduled_patient_ids = list(all_patient_ids - scheduled_patient_ids)
    
    unscheduled_patients_df = patients_df[patients_df['patient_id'].isin(unscheduled_patient_ids)]

    return schedule_df, unscheduled_patients_df, status_text

if __name__ == "__main__":
    # --- Test the optimizer standalone ---
    print("Testing optimizer standalone...")
    
    # Generate dummy data or load from CSVs created by generate_dataset.py
    try:
        patients_data = pd.read_csv("patients.csv")
        doctors_data = pd.read_csv("doctors.csv")
    except FileNotFoundError:
        print("CSV files not found. Please run generate_dataset.py first.")
        exit()

    print(f"\nLoaded {len(patients_data)} patients and {len(doctors_data)} doctors.")
    print("\nSample Doctor Availability:")
    for _, row in doctors_data.head(2).iterrows():
        print(f"{row['doctor_name']} ({row['doctor_id']}): {row['available_slots']}")

    print("\nRunning optimizer...")
    final_schedule_df, final_unscheduled_df, opt_status = solve_schedule(patients_data, doctors_data)

    print(f"\nOptimization Status: {opt_status}")

    if not final_schedule_df.empty:
        print("\n--- Scheduled Appointments ---")
        print(final_schedule_df.sort_values(by=['time_slot', 'doctor_id']))
        # Doctor utilization
        doctor_counts = final_schedule_df['doctor_id'].value_counts().reset_index()
        doctor_counts.columns = ['doctor_id', 'appointments_handled']
        print("\n--- Doctor Utilization (Scheduled Appointments) ---")
        print(doctor_counts)
    else:
        print("\nNo appointments could be scheduled.")

    if not final_unscheduled_df.empty:
        print("\n--- Unscheduled Patients ---")
        print(final_unscheduled_df)
    else:
        print("\nAll patients requiring an appointment were scheduled (if any).")
    
    print(f"\nTotal patients: {len(patients_data)}")
    print(f"Total scheduled: {len(final_schedule_df)}")
    print(f"Total unscheduled: {len(final_unscheduled_df)}")