import streamlit as st
import requests
import pandas as pd
import socket
import subprocess
import sys
import time

# Auto-start FastAPI server in the background if it's not running
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

if not is_port_in_use(8000):
    subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"])
    time.sleep(2)  # Give the backend a moment to start

# Define the FastAPI backend URL
API_URL = "http://127.0.0.1:8000/api/v1/users/"

st.set_page_config(page_title="User Management App", page_icon="👥", layout="wide")

st.title("👥 User Management with FastAPI & MongoDB")
st.markdown("This Streamlit app interacts with our FastAPI backend to perform CRUD operations on users.")

# --- Helper Functions ---
def get_users():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching users: {response.text}")
            return []
    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")
        return []

def create_user(name, email, age):
    payload = {"name": name, "email": email, "age": age}
    response = requests.post(API_URL, json=payload)
    return response

def update_user(user_id, name, email, age):
    payload = {"name": name, "email": email, "age": age}
    response = requests.put(f"{API_URL}{user_id}", json=payload)
    return response

def delete_user(user_id):
    response = requests.delete(f"{API_URL}{user_id}")
    return response

# --- UI Sections ---

tab1, tab2, tab3, tab4 = st.tabs(["View Users", "Add User", "Update User", "Delete User"])

with tab1:
    st.header("All Users")
    users = get_users()
    if users:
        # Convert list of dicts to a pandas DataFrame for better display
        df = pd.DataFrame(users)
        
        # Rename _id or id for display if needed
        if 'id' in df.columns:
            df = df.rename(columns={'id': 'User ID'})
        elif '_id' in df.columns:
            df = df.rename(columns={'_id': 'User ID'})
            
        # Display the dataframe
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No users found or could not connect to the database.")
        if st.button("Refresh Users"):
            st.rerun()

with tab2:
    st.header("Add New User")
    with st.form("add_user_form", clear_on_submit=True):
        name = st.text_input("Name")
        email = st.text_input("Email")
        age = st.number_input("Age", min_value=1, max_value=150, step=1)
        
        submitted = st.form_submit_button("Create User")
        if submitted:
            if name and email and age:
                resp = create_user(name, email, age)
                if resp.status_code == 201:
                    st.success(f"User '{name}' added successfully!")
                else:
                    st.error(f"Failed to add user: {resp.text}")
            else:
                st.warning("Please fill in all fields.")

with tab3:
    st.header("Update Existing User")
    users_for_update = get_users()
    if users_for_update:
        user_options = {f"{u['name']} ({u['email']})": u.get('id', u.get('_id')) for u in users_for_update}
        selected_user_label = st.selectbox("Select User to Update", options=list(user_options.keys()))
        selected_user_id = user_options[selected_user_label]
        
        # Find the selected user's current data
        selected_user_data = next((u for u in users_for_update if u.get('id', u.get('_id')) == selected_user_id), None)
        
        if selected_user_data:
            with st.form("update_user_form"):
                new_name = st.text_input("New Name", value=selected_user_data['name'])
                new_email = st.text_input("New Email", value=selected_user_data['email'])
                new_age = st.number_input("New Age", min_value=1, max_value=150, step=1, value=selected_user_data['age'])
                
                update_submitted = st.form_submit_button("Update User")
                if update_submitted:
                    resp = update_user(selected_user_id, new_name, new_email, new_age)
                    if resp.status_code == 200:
                        st.success(f"User '{new_name}' updated successfully!")
                    else:
                        st.error(f"Failed to update user: {resp.text}")
    else:
        st.info("No users available to update.")

with tab4:
    st.header("Delete User")
    users_for_delete = get_users()
    if users_for_delete:
        delete_options = {f"{u['name']} ({u['email']})": u.get('id', u.get('_id')) for u in users_for_delete}
        selected_delete_label = st.selectbox("Select User to Delete", options=list(delete_options.keys()))
        selected_delete_id = delete_options[selected_delete_label]
        
        st.warning(f"Are you sure you want to delete **{selected_delete_label}**?")
        if st.button("Yes, Delete User", type="primary"):
            resp = delete_user(selected_delete_id)
            if resp.status_code == 204:
                st.success("User deleted successfully!")
            else:
                st.error(f"Failed to delete user: {resp.text}")
    else:
        st.info("No users available to delete.")
