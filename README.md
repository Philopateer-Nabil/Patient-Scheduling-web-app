# Healthcare Patient Scheduling Optimizer

This project provides a web-based application built with Streamlit to optimize patient appointment scheduling. It uses a linear programming model to efficiently assign patients to available doctor time slots, maximizing the number of scheduled appointments.

## Key Features

  * **Optimized Scheduling:** Utilizes a linear programming model via the PuLP library to find the optimal schedule that maximizes the number of appointments.
  * **Flexible Data Input:** Users can either upload their own patient and doctor data via CSV files or generate sample data directly within the application.
  * **Resource Utilization Analysis:** After optimization, the application displays key metrics, including a detailed schedule, a list of unscheduled patients, and doctor utilization percentages with a corresponding bar chart.
  * **Interactive Web Interface:** A user-friendly interface built with Streamlit allows for easy data loading, optimization, and visualization of the results.

## Demo

## How It Works

The application operates based on three core components:

1.  **`app.py`**: The main Streamlit application file. It handles the user interface, data uploads, and displays the final schedule and analysis.
2.  **`optimizer.py`**: Contains the core scheduling logic. It takes patient and doctor availability data, formulates a linear programming problem to maximize appointments, and solves it.
3.  **`generate_dataset.py`**: A utility script to create sample CSV files for patients and doctors, which can be used for demonstration or testing purposes.

The optimization model aims to maximize the total number of scheduled appointments subject to two main constraints:

1.  Each patient can be scheduled for at most one appointment.
2.  Each doctor can handle at most one patient per available time slot.

## Getting Started

### Prerequisites

  * Python 3.7+
  * pip (Python package installer)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Philopateer-Nabil/Patient-Scheduling-web-app.git
    cd Patient-Scheduling-web-app
    ```

2.  **Install the required Python libraries:**

    ```bash
    pip install streamlit pandas pulp faker
    ```

      * **Note on Solvers:** PuLP requires a solver to be installed on your system. By default, it will try to use the CBC solver which is included with `pulp`. If it's not found, you may need to install one. For Debian/Ubuntu-based systems, you can install CBC with:
        ```bash
        sudo apt-get install coinor-cbc
        ```

### Running the Application

1.  **Launch the Streamlit app:**

    ```bash
    streamlit run app.py
    ```

2.  **Open your web browser** and navigate to the local URL provided by Streamlit.

## How to Use the App

1.  **Choose a Data Source:**

      * **Generate Sample Data:** Use the sliders in the sidebar to select the number of patients and doctors, then click "Generate and Load Data".
      * **Upload CSVs:** Select the "Upload CSVs" option and upload your patient and doctor data files. Ensure they follow the required format.

2.  **Review the Data:** The application will display the loaded patient and doctor data in dataframes.

3.  **Optimize the Schedule:** Click the "🚀 Optimize Schedule" button to run the optimization process.

4.  **View the Results:** The application will display:

      * **Optimized Schedule:** A table showing which patient is scheduled with which doctor and at what time.
      * **Resource Utilization:** A summary of how many appointments each doctor is handling, their total available slots, and their utilization percentage.
      * **Unscheduled Patients:** A list of any patients who could not be scheduled due to a lack of available slots.

## File Structure

```
.
├── app.py                  # Main Streamlit application file
├── optimizer.py            # Core optimization logic using PuLP
├── generate_dataset.py     # Script to generate sample data
└── README.md               # This file
```

### CSV File Format

To use your own data, the CSV files must have the following columns:

  * **`patients.csv`**:

      * `patient_id`: A unique identifier for each patient (e.g., P001).
      * `patient_name`: The name of the patient.

  * **`doctors.csv`**:

      * `doctor_id`: A unique identifier for each doctor (e.g., D01).
      * `doctor_name`: The name of the doctor.
      * `available_slots`: A semicolon-separated string of available time slots in `HH:MM` format (e.g., "09:00;09:30;11:00").



