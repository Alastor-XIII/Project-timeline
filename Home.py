import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import os

st.set_page_config(page_title="Project Timeline Pro", layout="wide")

# --- 1. Database Setup (CSV) ---
DB_FILE = "project_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            df['Start'] = pd.to_datetime(df['Start']).dt.date
            df['End'] = pd.to_datetime(df['End']).dt.date
            return df
        except:
            return pd.DataFrame(columns=["Project", "Activity", "Start", "End", "Status"])
    return pd.DataFrame(columns=["Project", "Activity", "Start", "End", "Status"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'master_df' not in st.session_state:
    st.session_state.master_df = load_data()

# --- 2. Sidebar Overview ---
with st.sidebar:
    st.title("🏗️ Project Overview")
    new_p = st.text_input("ชื่อโปรเจกต์ใหม่:")
    if st.button("➕ สร้างโปรเจกต์"):
        if new_p:
            new_row = pd.DataFrame([{"Project": new_p, "Activity": "เริ่มแผนงาน", "Start": date.today(), "End": date.today(), "Status": "Pending"}])
            st.session_state.master_df = pd.concat([st.session_state.master_df, new_row], ignore_index=True)
            save_data(st.session_state.master_df)
            st.rerun()

    st.markdown("---")
    project_list = st.session_state.master_df["Project"].unique().tolist()
    selected_project = st.selectbox("📂 เลือกโปรเจกต์:", options=project_list) if project_list else None

# --- 3. Main Interface ---
if selected_project:
    st.title(f"📊 Timeline: {selected_project}")
    
    # ดึงข้อมูลของโปรเจกต์ที่เลือก
    mask = st.session_state.master_df["Project"] == selected_project
    project_df = st.session_state.master_df[mask].copy()
    
    st.subheader("📝 รายละเอียดกิจกรรม")
    edited_df = st.data_editor(
        project_df,
        column_order=("Activity", "Start", "End", "Status"),
        num_rows="dynamic",
        column_config={
            "Start": st.column_config.DateColumn("วันเริ่ม", required=True, format="DD/MM/YYYY"),
            "End": st.column_config.DateColumn("วันเสร็จ", required=True, format="DD/MM/YYYY"),
            "Status": st.column_config.SelectboxColumn("สถานะ", options=["Pending", "In Progress", "Completed"])
        },
        use_container_width=True,
        key=f"editor_{selected_project}"
    )

    if st.button("💾 บันทึกข้อมูล (Save)"):
        other_projects = st.session_state.master_df[st.session_state.master
