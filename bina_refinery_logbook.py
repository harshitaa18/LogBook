import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', category=UserWarning)

import streamlit as st
import pandas as pd
import speech_recognition as sr
from datetime import datetime
import os

# Inject custom CSS for styling
st.markdown("""
<style>
/* General body and app styling */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
}

.stApp {
    background-color: #121212; /* Even darker background */
    color: #e0e0e0; /* Lighter text for better contrast */
    padding: 2rem; /* More padding */
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
    color: #ffffff; /* White headers */
    margin-top: 1.5rem; /* Space above headers */
    margin-bottom: 1rem; /* Space below headers */
}

/* Change cursor for selectboxes on hover (closed state) */
.stSelectbox div[data-baseweb="select"] {
    cursor: pointer !important;
    border-radius: 0.25rem; /* Rounded corners */
}

/* Change cursor for buttons on hover */
.stButton > button {
    cursor: pointer !important;
    background-color: #0a84ff; /* Accent color for buttons */
    color: white; /* White text on buttons */
    border-radius: 0.25rem; /* Rounded corners */
    padding: 0.5rem 1rem; /* Button padding */
    border: none; /* Remove default border */
    margin-top: 1rem; /* Space above buttons */
}

.stButton > button:hover {
    background-color: #0070cc; /* Darker accent on hover */
}

/* Change cursor for the open selectbox dropdown list */
.stSelectbox [role="listbox"] {
    cursor: default !important;
    background-color: #1e1e1e; /* Dark background for dropdown list */
    border: 1px solid #3a3a3a; /* Border for dropdown list */
    border-radius: 0.25rem; /* Rounded corners */
}

/* Change cursor for individual options within the open dropdown on hover */
.stSelectbox [role="option"] {
    cursor: pointer !important;
    color: #e0e0e0; /* Option text color */
    padding: 0.5rem 1rem; /* Padding for options */
}

.stSelectbox [role="option"]:hover {
    background-color: #3a3a3a; /* Highlight color on hover */
    color: #ffffff; /* White text on hover */
}

/* Style for input widgets */
.stNumberInput input, .stTextInput input {
    background-color: #1e1e1e; /* Dark background for inputs */
    color: #e0e0e0; /* Light text for inputs */
    border: 1px solid #3a3a3a; /* Border color */
    border-radius: 0.25rem; /* Rounded corners */
    padding: 0.5rem 1rem; /* Input padding */
}

/* Style for selectbox dropdown (selected value display) */
.stSelectbox div[role="button"] {
    background-color: #1e1e1e; /* Dark background */
    color: #e0e0e0; /* Light text */
    border: 1px solid #3a3a3a; /* Border color */
    border-radius: 0.25rem; /* Rounded corners */
    padding: 0.5rem 1rem; /* Padding */
}

/* Style for table headers */
.stDataFrame th {
    color: #ffffff; /* White text for headers */
    background-color: #2b2b2b; /* Darker background for headers */
}

/* Style for message boxes */
.stAlert {
    border-radius: 0.25rem; /* Rounded corners */
    padding: 1rem;
    margin-top: 1rem;
    margin-bottom: 1rem;
}

.stAlert.info {
    background-color: #0a2a4a; /* Dark blue */
    color: #90b0d0; /* Light blue text */
    border-color: #1a5a9a; /* Blue border */
}

.stAlert.success {
    background-color: #1a3a1a; /* Dark green */
    color: #90d090; /* Light green text */
    border-color: #2a7a2a; /* Green border */
}

.stAlert.error {
    background-color: #4a1a1a; /* Dark red */
    color: #d09090; /* Light red text */
    border-color: #9a2a2a; /* Red border */
}

</style>
""", unsafe_allow_html=True)

# Initialize session state - Moved to top
if 'readings' not in st.session_state:
    st.session_state.readings = {}
if 'transcript' not in st.session_state:
    st.session_state.transcript = ''
if 'is_listening' not in st.session_state:
    st.session_state.is_listening = False
if 'error' not in st.session_state:
    st.session_state.error = None
if 'selected_equipment' not in st.session_state:
    st.session_state.selected_equipment = None
if 'selected_parameter' not in st.session_state:
    st.session_state.selected_parameter = None

# Equipment and their parameters
EQUIPMENT_PARAMETERS = {
    "Crude Distillation Unit (CDU)": {
        "Top Temperature": "°C",
        "Bottom Temperature": "°C",
        "Feed Rate": "BPD",
        "Pressure": "bar",
        "Overhead Temperature": "°C"
    },
    "Vacuum Distillation Unit (VDU)": {
        "Vacuum Pressure": "bar",
        "Feed Temperature": "°C",
        "Bottom Temperature": "°C",
        "Steam Rate": "kg/hr",
        "Residue Flow": "BPD"
    },
    "Hydrocracker Unit": {
        "Reactor Temperature": "°C",
        "Reactor Pressure": "bar",
        "Hydrogen Flow": "Nm³/hr",
        "Feed Rate": "BPD",
        "Product Yield": "%"
    },
    "FCC Unit": {
        "Riser Temperature": "°C",
        "Regenerator Temperature": "°C",
        "Catalyst Circulation": "ton/hr",
        "Feed Rate": "BPD",
        "Pressure": "bar"
    },
    "Hydrotreater Unit": {
        "Reactor Temperature": "°C",
        "Reactor Pressure": "bar",
        "Hydrogen Flow": "Nm³/hr",
        "Feed Rate": "BPD",
        "Sulfur Content": "ppm"
    },
    "Sulfur Recovery Unit (SRU)": {
        "Reactor Temperature": "°C",
        "Acid Gas Flow": "Nm³/hr",
        "Air Flow": "Nm³/hr",
        "Sulfur Production": "ton/day",
        "Tail Gas H2S": "ppm"
    },
    "Power Plant": {
        "Steam Pressure": "bar",
        "Steam Temperature": "°C",
        "Power Generation": "MW",
        "Boiler Efficiency": "%",
        "Fuel Consumption": "ton/hr"
    },
    "Waste Water Treatment": {
        "pH Level": "pH",
        "COD": "mg/L",
        "Oil Content": "mg/L",
        "Flow Rate": "m³/hr",
        "TSS": "mg/L"
    },
    "Storage Tanks": {
        "Tank Level": "%",
        "Temperature": "°C",
        "Pressure": "bar",
        "Vapor Pressure": "bar",
        "Water Content": "%"
    },
    "Flare System": {
        "Flare Gas Flow": "Nm³/hr",
        "Flare Tip Temperature": "°C",
        "Pilot Flame Temperature": "°C",
        "Steam Flow": "kg/hr",
        "Smoke Number": "scale"
    }
}

# Define common units for parameter types
COMMON_PARAMETER_UNITS = {
    "Temperature": ["°C", "°F", "K"],
    "Pressure": ["bar", "psi", "Pa", "kPa", "MPa"],
    "Flow Rate": ["BPD", "m³/hr", "kg/hr", "Nm³/hr", "ton/hr"],
    "Level": ["%"],
    "Yield": ["%"],
    "Content": ["ppm", "mg/L", "%"],
    "Production": ["ton/day", "MW"],
    "Efficiency": ["%"],
    "Consumption": ["ton/hr"],
    "pH": ["pH"],
    "Smoke Number": ["scale"]
}

# Map specific parameters to common types
PARAMETER_TYPE_MAPPING = {
    "Top Temperature": "Temperature",
    "Bottom Temperature": "Temperature",
    "Feed Temperature": "Temperature",
    "Overhead Temperature": "Temperature",
    "Vacuum Pressure": "Pressure",
    "Pressure": "Pressure",
    "Reactor Temperature": "Temperature",
    "Reactor Pressure": "Pressure",
    "Hydrogen Flow": "Flow Rate",
    "Feed Rate": "Flow Rate",
    "Product Yield": "Yield",
    "Riser Temperature": "Temperature",
    "Regenerator Temperature": "°C",
    "Catalyst Circulation": "Flow Rate",
    "Sulfur Content": "Content",
    "Acid Gas Flow": "Flow Rate",
    "Air Flow": "Flow Rate",
    "Sulfur Production": "Production",
    "Tail Gas H2S": "Content",
    "Steam Pressure": "Pressure",
    "Steam Temperature": "Temperature",
    "Power Generation": "Production",
    "Boiler Efficiency": "Efficiency",
    "Fuel Consumption": "Consumption",
    "pH Level": "pH",
    "COD": "Content",
    "Oil Content": "Content",
    "Flow Rate": "Flow Rate",
    "TSS": "Content",
    "Tank Level": "Level",
    "Temperature": "Temperature",
    "Pressure": "Pressure",
    "Vapor Pressure": "Pressure",
    "Water Content": "Content",
    "Flare Gas Flow": "Flow Rate",
    "Flare Tip Temperature": "Temperature",
    "Pilot Flame Temperature": "Temperature",
    "Steam Flow": "Flow Rate",
    "Smoke Number": "Smoke Number"
}

def initialize_excel():
    """Initialize the Excel file if it doesn't exist"""
    if not os.path.exists('bina_refinery_log.xlsx'):
        df = pd.DataFrame(columns=['Equipment', 'Parameter', 'Value', 'Unit', 'Timestamp'])
        df.to_excel('bina_refinery_log.xlsx', index=False)

def append_to_excel(equipment, parameter, value, unit):
    """Append a new reading to the Excel file"""
    df = pd.read_excel('bina_refinery_log.xlsx')
    new_row = {
        'Equipment': equipment,
        'Parameter': parameter,
        'Value': value,
        'Unit': unit,
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel('bina_refinery_log.xlsx', index=False)

def get_voice_input():
    """Capture voice input using speech_recognition"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Please speak now.")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            st.error("Could not understand audio")
            return None
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")
            return None

def extract_numeric_value(text):
    """Extract numeric value from text"""
    import re
    # Find all numbers in the text
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    if numbers:
        return float(numbers[0])
    return None

# Initialize the Excel file
initialize_excel()

# Streamlit UI
st.title("Bina Refinery Operations Logbook")
st.write("Voice-controlled logbook for refinery operations")

# Select equipment
equipment = st.selectbox("Select Equipment", options=list(EQUIPMENT_PARAMETERS.keys()))
st.session_state.selected_equipment = equipment

# Parameter selection based on equipment
parameters = EQUIPMENT_PARAMETERS[equipment]
parameter = st.selectbox("Select Parameter", options=list(parameters.keys()))
st.session_state.selected_parameter = parameter

# Display default unit for the selected parameter
unit = parameters[parameter]
st.write(f"Default Unit: {unit}")

# Voice input button
if st.button("🎤 Start Voice Input"):
    voice_input = get_voice_input()
    if voice_input:
        st.write(f"Voice Input: {voice_input}")
        value = extract_numeric_value(voice_input)
        if value is not None:
            # Use the default unit for voice input
            append_to_excel(equipment, parameter, value, unit)
            # Also update session state for CSV export and display with default unit
            if equipment not in st.session_state.readings:
                st.session_state.readings[equipment] = {}
            st.session_state.readings[equipment][parameter] = {
                "value": value,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "in_normal_range": None, # We don't have range check for voice yet
                "alert_message": ""
            }
            st.success(f"Logged: {parameter} = {value} {unit}")
        else:
            st.error("Could not extract a numeric value from the voice input")

# Manual input option
manual_value = st.number_input("Or enter value manually", format="%.2f", key="manual_value_input")

# Get available units for the selected parameter
parameter_type = PARAMETER_TYPE_MAPPING.get(parameter, None)
available_units = COMMON_PARAMETER_UNITS.get(parameter_type, [unit]) # Use default unit if type not found

# Select unit for manual input
selected_unit = st.selectbox("Select Unit", options=available_units, key="manual_unit_select")

if manual_value != 0.0:
    if st.button("Save Manual Input", key="save_manual_button"):
        # Append to Excel using the selected unit
        append_to_excel(equipment, parameter, manual_value, selected_unit)

        # Also update session state for CSV export and display
        # (Assuming range check is only for manual input for now)
        in_range, alert_msg = (None, "") # Placeholder, implement range check if needed for manual
        if equipment not in st.session_state.readings:
            st.session_state.readings[equipment] = {}
        st.session_state.readings[equipment][parameter] = {
            "value": manual_value,
            "Unit": selected_unit, # Use the selected unit
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "in_normal_range": in_range,
            "alert_message": alert_msg
        }

        st.success(f"Logged: {parameter} = {manual_value} {selected_unit}")

# Display current log
st.subheader("Current Log")
try:
    df = pd.read_excel('bina_refinery_log.xlsx')
    # Add a 1-based index column
    df.insert(0, 'Entry #', range(1, 1 + len(df)))
    st.dataframe(df, hide_index=True) # Hide the default 0-based index
except FileNotFoundError:
    st.write("No log entries yet.")
except Exception as e:
    st.error(f"An error occurred while displaying the log: {e}")

# Export all readings as CSV button
if st.button("Export Readings as CSV"):
    # Read data directly from the Excel file
    try:
        df_export = pd.read_excel('bina_refinery_log.xlsx')
        if not df_export.empty:
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download CSV", data=csv, file_name="readings.csv", mime="text/csv")
        else:
            st.warning("No readings to export.")
    except FileNotFoundError:
        st.warning("No readings to export yet (Excel file not found).")
    except Exception as e:
        st.error(f"An error occurred during CSV export: {e}") 