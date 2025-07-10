# app.py
import streamlit as st
import pandas as pd
from optimizer import solve_schedule, STANDARD_TIME_SLOTS # Import from optimizer.py
from generate_dataset import generate_patients_csv, generate_doctors_csv, TIME_SLOTS as GENERATOR_TIME_SLOTS # Import from generator
import os

# Ensure generator and optimizer use consistent time slots if not passed explicitly
# For this app, we'll primarily use STANDARD_TIME_SLOTS from the optimizer
APP_TIME_SLOTS = STANDARD_TIME_SLOTS

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Patient Scheduling Optimizer")

st.title("🏥 Healthcare Patient Scheduling Optimizer")
st.markdown("""
This application uses Linear Programming to optimize patient appointment scheduling
based on doctor availability and patient demand.
""")

# --- Helper Functions ---
def load_data(patients_file, doctors_file):
    patients_df = None
    doctors_df = None
    if patients_file:
        try:
            patients_df = pd.read_csv(patients_file)
        except Exception as e:
            st.error(f"Error loading patients CSV: {e}")
    if doctors_file:
        try:
            doctors_df = pd.read_csv(doctors_file)
            # Ensure 'available_slots' is string, handle potential float NaNs from empty cells
            if 'available_slots' in doctors_df.columns:
                 doctors_df['available_slots'] = doctors_df['available_slots'].astype(str).replace('nan', '')
        except Exception as e:
            st.error(f"Error loading doctors CSV: {e}")
    return patients_df, doctors_df

def display_schedule_summary(schedule_df, unscheduled_df, doctors_df):
    st.subheader("🗓️ Optimized Schedule")
    if not schedule_df.empty:
        # Merge with doctor names for readability
        schedule_display = schedule_df.merge(doctors_df[['doctor_id', 'doctor_name']], on='doctor_id', how='left')
        # Merge with patient names for readability (if patient_name exists)
        if 'patient_name' in st.session_state.patients_df.columns:
             schedule_display = schedule_display.merge(st.session_state.patients_df[['patient_id', 'patient_name']], on='patient_id', how='left')
             schedule_display = schedule_display[['patient_id', 'patient_name', 'doctor_id', 'doctor_name', 'time_slot']]


        st.dataframe(schedule_display.sort_values(by=['time_slot', 'doctor_name']))
        
        st.subheader("📊 Resource Utilization")
        # Doctor utilization
        if not schedule_df.empty:
            doctor_counts = schedule_df['doctor_id'].value_counts().reset_index()
            doctor_counts.columns = ['doctor_id', 'appointments_handled']
            
            # Get total available slots per doctor for utilization percentage
            total_available_slots = []
            for _, doc_row in doctors_df.iterrows():
                slots_str = doc_row.get('available_slots', '')
                num_slots = len(slots_str.split(';')) if slots_str else 0
                total_available_slots.append({'doctor_id': doc_row['doctor_id'], 'total_slots': num_slots})
            
            total_slots_df = pd.DataFrame(total_available_slots)
            doctor_utilization = doctor_counts.merge(total_slots_df, on='doctor_id', how='left')
            doctor_utilization = doctor_utilization.merge(doctors_df[['doctor_id', 'doctor_name']], on='doctor_id', how='left')

            # Calculate utilization percentage
            doctor_utilization['utilization_percentage'] = doctor_utilization.apply(
                lambda row: (row['appointments_handled'] / row['total_slots'] * 100) if row['total_slots'] > 0 else 0, axis=1
            )
            doctor_utilization = doctor_utilization[['doctor_name', 'appointments_handled', 'total_slots', 'utilization_percentage']]
            st.dataframe(doctor_utilization)
            st.bar_chart(doctor_utilization.set_index('doctor_name')['utilization_percentage'])

    else:
        st.warning("No appointments could be scheduled based on the current data and constraints.")

    if not unscheduled_df.empty:
        st.subheader("⚠️ Unscheduled Patients")
        # Merge with patient names for readability if available
        if 'patient_name' in st.session_state.patients_df.columns:
            unscheduled_display = unscheduled_df.merge(st.session_state.patients_df[['patient_id', 'patient_name']], on='patient_id', how='left')
            display_columns = ['patient_id', 'patient_name']
        else:
            unscheduled_display = unscheduled_df.copy()
            display_columns = ['patient_id']
        
        # Only select columns that exist in the DataFrame
        available_columns = [col for col in display_columns if col in unscheduled_display.columns]
        st.dataframe(unscheduled_display[available_columns])
    else:
        st.success("All patients were successfully scheduled!")


# --- Session State Initialization ---
if 'patients_df' not in st.session_state:
    st.session_state.patients_df = None
if 'doctors_df' not in st.session_state:
    st.session_state.doctors_df = None
if 'schedule_df' not in st.session_state:
    st.session_state.schedule_df = pd.DataFrame()
if 'unscheduled_df' not in st.session_state:
    st.session_state.unscheduled_df = pd.DataFrame()
if 'opt_status' not in st.session_state:
    st.session_state.opt_status = ""

# --- Sidebar for Data Input and Generation ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    data_source = st.radio("Select Data Source:", ("Upload CSVs", "Generate Sample Data"))

    if data_source == "Generate Sample Data":
        st.subheader("Sample Data Generation")
        num_patients_gen = st.slider("Number of Patients", 10, 200, 50, 10)
        num_doctors_gen = st.slider("Number of Doctors", 1, 10, 3, 1)
        if st.button("Generate and Load Data"):
            pat_file = "temp_patients.csv"
            doc_file = "temp_doctors.csv"
            generate_patients_csv(pat_file, num_patients_gen)
            generate_doctors_csv(doc_file, num_doctors_gen, time_slots=GENERATOR_TIME_SLOTS)
            st.session_state.patients_df, st.session_state.doctors_df = load_data(pat_file, doc_file)
            st.success("Sample data generated and loaded!")
            # Clean up temp files
            if os.path.exists(pat_file): os.remove(pat_file)
            if os.path.exists(doc_file): os.remove(doc_file)


    elif data_source == "Upload CSVs":
        st.subheader("Upload Data Files")
        patients_file_up = st.file_uploader("Upload Patients CSV", type="csv")
        doctors_file_up = st.file_uploader("Upload Doctors CSV", type="csv")
        if patients_file_up and doctors_file_up:
            st.session_state.patients_df, st.session_state.doctors_df = load_data(patients_file_up, doctors_file_up)
            if st.session_state.patients_df is not None and st.session_state.doctors_df is not None:
                 st.success("Data loaded successfully from CSVs!")


    st.markdown("---")
    st.info(f"Time slots for scheduling: {', '.join(APP_TIME_SLOTS)}")

# --- Main Area for Data Display and Editing ---
if st.session_state.patients_df is not None:
    st.subheader("Current Patient List")
    st.dataframe(st.session_state.patients_df, height=200)

if st.session_state.doctors_df is not None:
    st.subheader("Current Doctor Availability")
    st.markdown("""
    Current doctor availability for scheduling. Time slots are shown in HH:MM format.
    """)
    
    # Display the doctors dataframe
    st.dataframe(st.session_state.doctors_df)


# --- Optimization Trigger ---
if st.session_state.patients_df is not None and st.session_state.doctors_df is not None:
    if not st.session_state.patients_df.empty and not st.session_state.doctors_df.empty:
        if st.button("🚀 Optimize Schedule", type="primary", use_container_width=True):
            with st.spinner("Optimizing schedule... Please wait."):
                # Pass the potentially edited doctors_df from session state
                schedule_df, unscheduled_df, opt_status = solve_schedule(
                    st.session_state.patients_df, 
                    st.session_state.doctors_df, # Use the (potentially edited) dataframe
                    time_slots=APP_TIME_SLOTS
                )
                st.session_state.schedule_df = schedule_df
                st.session_state.unscheduled_df = unscheduled_df
                st.session_state.opt_status = opt_status
            
            if st.session_state.opt_status:
                 st.success(f"Optimization Complete! Status: {st.session_state.opt_status}")
            else:
                 st.error("Optimization failed or returned no status.")
    else:
        st.warning("Please load or generate data with at least one patient and one doctor.")
else:
    st.info("Please load or generate data using the sidebar to begin.")


# --- Display Results ---
if not st.session_state.schedule_df.empty or not st.session_state.unscheduled_df.empty:
    display_schedule_summary(st.session_state.schedule_df, st.session_state.unscheduled_df, st.session_state.doctors_df)