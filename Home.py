import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import os

# 1. ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Project Timeline Pro", layout="wide")

# 2. ระบบจัดการฐานข้อมูล (CSV)
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

# 3. Sidebar
with st.sidebar:
    st.title("🏗️ Project Overview")
    new_p = st.text_input("ชื่อโปรเจกต์ใหม่:")
    if st.button("➕ สร้างโปรเจกต์"):
        if new_p:
            new_row = pd.DataFrame([{
                "Project": new_p, 
                "Activity": "Initial Plan", 
                "Start": date.today(), 
                "End": date.today(), 
                "Status": "Pending"
            }])
            st.session_state.master_df = pd.concat([st.session_state.master_df, new_row], ignore_index=True)
            save_data(st.session_state.master_df)
            st.rerun()

    st.markdown("---")  # บรรทัดนี้ต้องย่อหน้าให้ตรงกับ st.title ด้านบน
    project_list = st.session_state.master_df["Project"].unique().tolist()
    selected_project = st.selectbox("📂 เลือกโปรเจกต์:", options=project_list) if project_list else None

# 4. หน้าจอหลัก
if selected_project:
    st.title(f"📊 Timeline: {selected_project}")
    
    # ดึงข้อมูลโปรเจกต์ที่เลือก
    mask = st.session_state.master_df["Project"] == selected_project
    project_df = st.session_state.master_df[mask].copy().reset_index(drop=True)
    
    st.subheader("📝 รายละเอียดกิจกรรม")
    edited_df = st.data_editor(
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

    if st.button("💾 บันทึกข้อมูล (Save)"):
        other_projects = st.session_state.master_df[st.session_state.master_df["Project"] != selected_project]
        edited_df["Project"] = selected_project
        st.session_state.master_df = pd.concat([other_projects, edited_df], ignore_index=True)
        save_data(st.session_state.master_df)
        st.success("บันทึกเรียบร้อย!")
        st.rerun()

    # 5. Gantt Chart (บังคับแยกบรรทัดทุก Activity)
    st.markdown("---")
    plot_df = edited_df.dropna(subset=['Activity', 'Start', 'End']).copy()
    
    if not plot_df.empty:
        try:
            # สร้างชื่อที่ Unique เพื่อให้ Plotly แยกบรรทัดให้ครบทุกแถว
            plot_df['Display'] = plot_df['Activity'] + " (#" + (plot_df.index + 1).astype(str) + ")"
            
            fig = px.timeline(
                plot_df,
                x_start="Start", x_end="End", y="Display",
                color="Status", text="Activity",
                color_discrete_map={"Completed": "#2ecc71", "In Progress": "#f1c40f", "Pending": "#e74c3c"}
            )
            
            fig.update_xaxes(showgrid=True, gridcolor='LightGrey', dtick="D1", tickformat="%d %b", side="top")
            fig.update_yaxes(autorange="reversed", title="")
            
            fig.update_layout(
                height=300 + (len(plot_df) * 40),
                margin=dict(l=20, r=20, t=100, b=20),
                xaxis_title="📅 แผนงานรายวัน",
                shapes=[dict(
                    type='line', yref='paper', y0=0, y1=1,
                    xref='x', x0=date.today(), x1=date.today(),
                    line=dict(color="Red", width=2, dash="dash")
                )]
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("💡 กรุณากรอก Activity และวันที่ให้ครบถ้วน")
else:
    st.info("👈 เริ่มต้นโดยการเพิ่มชื่อโปรเจกต์ที่เมนูด้านซ้าย")
