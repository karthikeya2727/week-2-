import os
import streamlit as st
from db import SessionLocal, create_request, get_all_requests, get_request_by_id, update_request_status, init_db, Base, engine
from excel_utils import write_new_incident, update_incident_status, INCIDENT_FILE
from rundeck_stub import simulate_installation
from llm_utils import parse_request_text
import pandas as pd

# Configure page
st.set_page_config(page_title="Teams Incident Bot Prototype", layout="wide")

# Load custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("💬 Teams Bot ")

# Function to reset the database
def reset_database():
    Base.metadata.drop_all(bind=engine)
    init_db()
    st.sidebar.success("Database reset successfully!")

# Function to reset the Excel file
def reset_excel():
    if os.path.exists(INCIDENT_FILE):
        os.remove(INCIDENT_FILE)
        st.sidebar.success("Excel file reset successfully!")
    else:
        st.sidebar.info("Excel file doesn't exist.")

from db import init_db
init_db()


# Settings section at the bottom of the sidebar
st.sidebar.subheader("Settings")
if st.sidebar.button("reset db"):
    reset_database()
if st.sidebar.button("reset excel"):
    reset_excel()

# List of application names for dropdown
APPLICATION_NAMES = [
    "",
    "Visual Studio Code",
    "IntelliJ IDEA",
    "Eclipse",
    "NetBeans",
    "Visual Studio",
    "Atom",
    "WebStorm",
    "CLion",
    "Xcode",
    "Cursor"
]

st.subheader("Create Request via Form")

with st.form("req_form"):
    user_name = st.text_input("User Name", value=st.session_state.get("user_name", ""))
    
    # Set the index for app_name based on session state
    try:
        app_index = APPLICATION_NAMES.index(st.session_state.get("app_name", "Choose an application"))
    except ValueError:
        app_index = 0
    app_name = st.selectbox("Application Name", options=APPLICATION_NAMES, index=app_index)
    
    version = st.text_input("Version (optional)", value=st.session_state.get("version", ""))
    
    # Remarks input
    st.markdown("##### Remarks")
    remarks = st.text_area("Enter your remarks here", height=100)
    
    # Submit button
    send_clicked = st.form_submit_button("Send", use_container_width=True)
    
    # Handle form submission
    if send_clicked:
        
        with SessionLocal() as session:
            req = create_request(session, user_name, app_name, version, remarks)
            write_new_incident(req)
        st.success(f"Request {req.request_id} submitted successfully! Scroll down to see all requests.")
        # Clear form fields by resetting session state
        st.session_state.user_name = ""
        st.session_state.version = ""
        st.session_state.remarks = ""
        # Don't show the request details at the top - just show success message
        st.rerun()



# Display all requests in a table format below the form
st.markdown("---")
st.subheader("All Requests")

# Get all requests and display them in a table
with SessionLocal() as session:
    requests = get_all_requests(session)

if requests:
    # Display as a table with action buttons
    for r in requests:
        cols = st.columns([1, 1, 1, 1, 2, 1, 2])
        cols[0].write(r.request_id)
        cols[1].write(r.user_name)
        cols[2].write(r.application)
        cols[3].write(r.version or "-")
        cols[4].write(r.remarks or "-")
        cols[5].write(r.status)
        
        # Action buttons in the last column
        with cols[6]:
            # Only show buttons if status is pending
            if r.status == "Pending":
                btn_cols = st.columns(2)
                with btn_cols[0]:
                    if st.button("Approve", key=f"approve_{r.request_id}", use_container_width=True):
                        with SessionLocal() as session:
                            # Refresh the request object to ensure we have the latest data
                            refreshed_request = get_request_by_id(session, r.request_id)
                            update_request_status(session, refreshed_request, "Approved", approver="Supervisor")
                            update_incident_status(refreshed_request)
                        st.success(f"Request {r.request_id} Approved")
                        st.rerun()
                with btn_cols[1]:
                    if st.button("Reject", key=f"reject_{r.request_id}", use_container_width=True):
                        with SessionLocal() as session:
                            # Refresh the request object to ensure we have the latest data
                            refreshed_request = get_request_by_id(session, r.request_id)
                            update_request_status(session, refreshed_request, "Rejected", approver="Supervisor")
                            update_incident_status(refreshed_request)
                        st.error(f"Request {r.request_id} Rejected")
                        st.rerun()
            else:
                # Show status if already approved/rejected
                st.write(r.status)
