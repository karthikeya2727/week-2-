import os
import pandas as pd

INCIDENT_FILE = "data/incident_log.xlsx"

def write_new_incident(req):
    import os
    os.makedirs(os.path.dirname(INCIDENT_FILE), exist_ok=True)
    print(f"Creating incident entry at: {os.path.abspath(INCIDENT_FILE)}")
    row = {
        "RequestID": req.request_id,
        "User": req.user_name,
        "Application": req.application,
        "Version": req.version,
        "Remarks": req.remarks,
        "Status": req.status
    }
    if os.path.exists(INCIDENT_FILE):
        df = pd.read_excel(INCIDENT_FILE)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_excel(INCIDENT_FILE, index=False)

def update_incident_status(req):
    """Update the status of an existing incident in the Excel file"""
    if not os.path.exists(INCIDENT_FILE):
        # If file doesn't exist, create it with the new incident
        write_new_incident(req)
        return
    
    # Read the existing Excel file
    df = pd.read_excel(INCIDENT_FILE)
    
    # Find the row with matching RequestID and update its status
    mask = df["RequestID"] == req.request_id
    if mask.any():
        df.loc[mask, "Status"] = req.status
        # Also update other fields that might have changed
        df.loc[mask, "User"] = req.user_name
        df.loc[mask, "Application"] = req.application
        df.loc[mask, "Version"] = req.version
        df.loc[mask, "Remarks"] = req.remarks
    else:
        # If RequestID not found, add as new incident
        row = {
            "RequestID": req.request_id,
            "User": req.user_name,
            "Application": req.application,
            "Version": req.version,
            "Remarks": req.remarks,
            "Status": req.status
        }
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    
    # Save the updated DataFrame back to Excel
    df.to_excel(INCIDENT_FILE, index=False)
