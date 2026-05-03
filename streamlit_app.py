import streamlit as st
import pandas as pd
import os
import pymongo
from bson import ObjectId

st.set_page_config(page_title="User Management App", page_icon="👥", layout="wide")

# Try to load from Streamlit secrets if running on Streamlit Cloud
if "MONGODB_URL" in st.secrets:
    os.environ["MONGODB_URL"] = st.secrets["MONGODB_URL"]
if "DATABASE_NAME" in st.secrets:
    os.environ["DATABASE_NAME"] = st.secrets["DATABASE_NAME"]

# Import config after setting env vars
from app.core.config import settings

@st.cache_resource
def get_database():
    try:
        # Connect to MongoDB synchronously
        client = pymongo.MongoClient(os.environ.get("MONGODB_URL", settings.MONGODB_URL))
        db = client[os.environ.get("DATABASE_NAME", settings.DATABASE_NAME)]
        # Ping to check connection
        client.admin.command('ping')
        return db
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
        st.stop()

db = get_database()
collection = db["users"]

st.title("👥 User Management with Direct MongoDB Connection")
st.markdown("This Streamlit app interacts directly with MongoDB, bypassing the local FastAPI server for faster and more reliable deployment.")

# --- Helper Functions ---
def get_users():
    try:
        users = list(collection.find())
        # Convert ObjectId to string for easy display
        for u in users:
            u['_id'] = str(u['_id'])
        return users
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return []

def create_user(name, email, age):
    try:
        user_data = {"name": name, "email": email, "age": age}
        result = collection.insert_one(user_data)
        return True, str(result.inserted_id)
    except Exception as e:
        return False, str(e)

def update_user(user_id, name, email, age):
    try:
        user_data = {"name": name, "email": email, "age": age}
        result = collection.update_one({"_id": ObjectId(user_id)}, {"$set": user_data})
        if result.matched_count == 1:
            return True, "User updated successfully"
        return False, "User not found"
    except Exception as e:
        return False, str(e)

def delete_user(user_id):
    try:
        result = collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 1:
            return True, "User deleted successfully"
        return False, "User not found"
    except Exception as e:
        return False, str(e)

# --- UI Sections ---
tab1, tab2, tab3, tab4 = st.tabs(["View Users", "Add User", "Update User", "Delete User"])

with tab1:
    st.header("All Users")
    users = get_users()
    if users:
        df = pd.DataFrame(users)
        # Rename _id for display
        if '_id' in df.columns:
            df = df.rename(columns={'_id': 'User ID'})
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No users found in the database.")
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
                success, resp = create_user(name, email, age)
                if success:
                    st.success(f"User '{name}' added successfully!")
                else:
                    st.error(f"Failed to add user: {resp}")
            else:
                st.warning("Please fill in all fields.")

with tab3:
    st.header("Update Existing User")
    users_for_update = get_users()
    if users_for_update:
        user_options = {f"{u['name']} ({u.get('email', '')})": u['_id'] for u in users_for_update}
        selected_user_label = st.selectbox("Select User to Update", options=list(user_options.keys()))
        selected_user_id = user_options[selected_user_label]
        
        selected_user_data = next((u for u in users_for_update if u['_id'] == selected_user_id), None)
        
        if selected_user_data:
            with st.form("update_user_form"):
                new_name = st.text_input("New Name", value=selected_user_data.get('name', ''))
                new_email = st.text_input("New Email", value=selected_user_data.get('email', ''))
                new_age = st.number_input("New Age", min_value=1, max_value=150, step=1, value=selected_user_data.get('age', 18))
                
                update_submitted = st.form_submit_button("Update User")
                if update_submitted:
                    success, resp = update_user(selected_user_id, new_name, new_email, new_age)
                    if success:
                        st.success(f"User updated successfully!")
                    else:
                        st.error(f"Failed to update user: {resp}")
    else:
        st.info("No users available to update.")

with tab4:
    st.header("Delete User")
    users_for_delete = get_users()
    if users_for_delete:
        delete_options = {f"{u['name']} ({u.get('email', '')})": u['_id'] for u in users_for_delete}
        selected_delete_label = st.selectbox("Select User to Delete", options=list(delete_options.keys()))
        selected_delete_id = delete_options[selected_delete_label]
        
        st.warning(f"Are you sure you want to delete **{selected_delete_label}**?")
        if st.button("Yes, Delete User", type="primary"):
            success, resp = delete_user(selected_delete_id)
            if success:
                st.success("User deleted successfully!")
            else:
                st.error(f"Failed to delete user: {resp}")
    else:
        st.info("No users available to delete.")
