import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Engineering Project Timeline", layout="wide")

# 2. Session State Management (เสมือน Database ชั่วคราว)
if 'all_projects' not in st.session_state:
    # สร้างโครงสร้างข้อมูลเริ่มต้น
    st.session_state.all_projects = {
        "Project Alpha": pd.DataFrame([
            {"Activity": "Design Phase", "Start": "2026-03-01", "End": "2026-03-10", "Status": "Completed"},
            {"Activity": "Procurement", "Start": "2026-03-11", "End": "2026-03-25", "Status": "In Progress"}
        ]),
        "Project Beta": pd.DataFrame([
            {"Activity": "Site Preparation", "Start": "2026-04-01", "End": "2026-04-15", "Status": "Pending"}
        ])
    }

# --- SIDEBAR: Project Selection & Management ---
with st.sidebar:
    st.title("📂 Project Management")
    
    # ส่วนเพิ่มโปรเจกต์ใหม่
    new_p_name = st.text_input("สร้างโปรเจกต์ใหม่ (ชื่อ):")
    if st.button("➕ Create Project"):
        if new_p_name and new_p_name not in st.session_state.all_projects:
            st.session_state.all_projects[new_p_name] = pd.DataFrame(columns=["Activity", "Start", "End", "Status"])
            st.success(f"สร้าง {new_p_name} แล้ว")
            st.rerun()

    st.markdown("---")
    
    # ส่วนเลือกโปรเจกต์ที่จะดู
    selected_project = st.selectbox(
        "🔎 เลือกโปรเจกต์เพื่อดู Timeline:",
        options=list(st.session_state.all_projects.keys())
    )

# --- MAIN CONTENT ---
st.title(f"📊 Timeline: {selected_project}")

# ดึงข้อมูลของโปรเจกต์ที่เลือก
df = st.session_state.all_projects[selected_project]

# ส่วนที่ 1: การกรอกข้อมูล Activity (Interactive Table)
st.subheader("📝 Fill Activities")
st.info("คุณสามารถพิมพ์ลงในตารางด้านล่างเพื่อเพิ่มหรือแก้ไข Activity ได้เลย (กดปุ่มว่างด้านล่างสุดเพื่อเพิ่มแถว)")

# ใช้ data_editor เพื่อให้ผู้ใช้กรอกข้อมูลได้เหมือน Excel
edited_df = st.data_editor(
    df,
    num_rows="dynamic", # ให้เพิ่ม/ลบแถวได้
    column_config={
        "Start": st.column_config.DateColumn("Start Date"),
        "End": st.column_config.DateColumn("End Date"),
        "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "In Progress", "Completed"])
    },
    use_container_width=True,
    key=f"editor_{selected_project}"
)

# บันทึกค่าที่แก้ลง Session State
st.session_state.all_projects[selected_project] = edited_df

# ส่วนที่ 2: การแสดงผล Timeline (Gantt Chart)
st.markdown("---")
st.subheader("📅 Gantt Chart Visual")

if not edited_df.empty and edited_df["Start"].notnull().all():
    try:
        # วาดกราฟ Timeline
        fig = px.timeline(
            edited_df,
            x_start="Start",
            x_end="End",
            y="Activity",
            color="Status",
            color_discrete_map={"Completed": "#2ecc71", "In Progress": "#f1c40f", "Pending": "#e74c3c"},
            text="Activity"
        )
        
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            xaxis_title="Timeline",
            yaxis_title="",
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error("กรุณากรอกข้อมูลวันที่ (Start/End) ให้ครบถ้วนเพื่อแสดงผลกราฟ")
else:
    st.warning("กรุณาเพิ่ม Activity และระบุวันที่ในตารางด้านบน")

# ปุ่มลบโปรเจกต์
if st.sidebar.button("🗑️ Delete Current Project", type="secondary"):
    del st.session_state.all_projects[selected_project]
    st.rerun()
