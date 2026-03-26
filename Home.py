import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import os

st.set_page_config(page_title="Project Timeline Pro", layout="wide")

# --- 1. ระบบจัดการไฟล์ (Database จำลอง) ---
DB_FILE = "project_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # แปลง String กลับเป็น Date
        df['Start'] = pd.to_datetime(df['Start']).dt.date
        df['End'] = pd.to_datetime(df['End']).dt.date
        return df
    return pd.DataFrame(columns=["Project", "Activity", "Start", "End", "Status"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# โหลดข้อมูลมาไว้ใน Session
if 'master_df' not in st.session_state:
    st.session_state.master_df = load_data()

# --- 2. ส่วนของ Sidebar (Overview) ---
with st.sidebar:
    st.title("🏗️ Project Overview")
    
    # เพิ่มโปรเจกต์ใหม่
    new_p = st.text_input("ชื่อโปรเจกต์ใหม่:")
    if st.button("➕ สร้างโปรเจกต์"):
        if new_p:
            new_row = pd.DataFrame([{"Project": new_p, "Activity": "เริ่มแผนงาน", "Start": date.today(), "End": date.today(), "Status": "Pending"}])
            st.session_state.master_df = pd.concat([st.session_state.master_df, new_row], ignore_index=True)
            save_data(st.session_state.master_df)
            st.rerun()

    st.markdown("---")
    project_list = st.session_state.master_df["Project"].unique().tolist()
    if project_list:
        selected_project = st.selectbox("📂 เลือกโปรเจกต์ที่จะจัดการ:", options=project_list)
    else:
        selected_project = None

# --- 3. ส่วนแสดงผลและการแก้ไข ---
if selected_project:
    st.title(f"📊 Timeline: {selected_project}")
    
    # ดึงเฉพาะข้อมูลของโปรเจกต์ที่เลือก
    project_df = st.session_state.master_df[st.session_state.master_df["Project"] == selected_project].copy()
    
    st.subheader("📝 แก้ไขกิจกรรม (พิมพ์ลงตารางได้เลย)")
    
    # แก้ไขข้อมูลผ่าน Data Editor
    edited_project_df = st.data_editor(
        project_df,
        column_order=("Activity", "Start", "End", "Status"),
        num_rows="dynamic",
        column_config={
            "Start": st.column_config.DateColumn("วันเริ่ม", required=True),
            "End": st.column_config.DateColumn("วันเสร็จ", required=True),
            "Status": st.column_config.SelectboxColumn("สถานะ", options=["Pending", "In Progress", "Completed"])
        },
        use_container_width=True,
        key=f"editor_{selected_project}"
    )

    # ปุ่มบันทึกข้อมูล (เพื่อให้ข้อมูลลงไฟล์ CSV ถาวร)
    if st.button("💾 บันทึกการแก้ไขทั้งหมด"):
        # อัปเดตข้อมูลกลับไปที่ Master DF
        other_projects = st.session_state.master_df[st.session_state.master_df["Project"] != selected_project]
        edited_project_df["Project"] = selected_project # กันพลาด
        st.session_state.master_df = pd.concat([other_projects, edited_project_df], ignore_index=True)
        save_data(st.session_state.master_df)
        st.success("บันทึกข้อมูลลงระบบเรียบร้อยแล้ว!")
        st.rerun()

    # --- 4. การแสดงผล Timeline (Real-time) ---
    st.markdown("---")
    if not edited_project_df.empty:
        # ตรวจสอบว่ามีวันที่ครบไหมก่อนวาด
        plot_df = edited_project_df.dropna(subset=['Start', 'End', 'Activity'])
        if not plot_df.empty:
            fig = px.timeline(
                plot_df,
                x_start="Start",
                x_end="End",
                y="Activity",
                color="Status",
                color_discrete_map={"Completed": "#2ecc71", "In Progress": "#f1c40f", "Pending": "#e74c3c"},
                title=f"Gantt Chart - {selected_project}"
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("กรุณากรอกกิจกรรมและวันที่ให้ครบถ้วนเพื่อแสดง Timeline")

else:
    st.info("👈 เริ่มต้นโดยการเพิ่มชื่อโปรเจกต์ที่แถบด้านซ้าย")
