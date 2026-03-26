import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

st.set_page_config(page_title="Project Timeline", layout="wide")

# ฟังก์ชันแปลงข้อมูลให้เป็นชนิดที่ถูกต้อง
def prepare_df(df):
    if not df.empty:
        df['Start'] = pd.to_datetime(df['Start']).dt.date
        df['End'] = pd.to_datetime(df['End']).dt.date
    return df

if 'all_projects' not in st.session_state:
    # สร้างข้อมูลเริ่มต้นด้วยชนิดข้อมูล date โดยตรง
    st.session_state.all_projects = {
        "Project Alpha": pd.DataFrame([
            {"Activity": "Design Phase", "Start": date(2026, 3, 1), "End": date(2026, 3, 10), "Status": "Completed"},
            {"Activity": "Procurement", "Start": date(2026, 3, 11), "End": date(2026, 3, 25), "Status": "In Progress"}
        ]),
    }

with st.sidebar:
    st.title("📂 Project Management")
    new_p_name = st.text_input("สร้างโปรเจกต์ใหม่:")
    if st.button("➕ Create"):
        if new_p_name and new_p_name not in st.session_state.all_projects:
            # สร้าง DataFrame เปล่าที่มีคอลัมน์ครบ
            st.session_state.all_projects[new_p_name] = pd.DataFrame(columns=["Activity", "Start", "End", "Status"])
            st.rerun()
    
    st.markdown("---")
    selected_project = st.selectbox("เลือกโปรเจกต์:", options=list(st.session_state.all_projects.keys()))

st.title(f"📊 Timeline: {selected_project}")

# ดึงข้อมูลและตรวจสอบ Type
df = st.session_state.all_projects[selected_project]
df = prepare_df(df)

st.subheader("📝 Fill Activities")
# แก้ไขจุดที่ทำให้เกิด Error โดยระบุ Schema ให้ชัดเจน
edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    column_config={
        "Activity": st.column_config.TextColumn("Activity", required=True),
        "Start": st.column_config.DateColumn("Start Date", format="YYYY-MM-DD", required=True),
        "End": st.column_config.DateColumn("End Date", format="YYYY-MM-DD", required=True),
        "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "In Progress", "Completed"], default="Pending")
    },
    use_container_width=True,
    key=f"editor_{selected_project}"
)

# บันทึกค่า
st.session_state.all_projects[selected_project] = edited_df

# กราฟ Timeline
if not edited_df.empty and edited_df["Start"].notnull().any():
    try:
        # กรองแถวที่ข้อมูลไม่ครบออกก่อนวาดกราฟ
        plot_df = edited_df.dropna(subset=['Start', 'End', 'Activity'])
        
        if not plot_df.empty:
            fig = px.timeline(
                plot_df,
                x_start="Start",
                x_end="End",
                y="Activity",
                color="Status",
                color_discrete_map={"Completed": "#2ecc71", "In Progress": "#f1c40f", "Pending": "#e74c3c"}
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info("กำลังรอข้อมูลที่สมบูรณ์เพื่อวาดกราฟ...")
