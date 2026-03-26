import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import os

st.set_page_config(page_title="Project Timeline Pro", layout="wide")

# --- 1. ระบบจัดการฐานข้อมูล (CSV) ---
DB_FILE = "project_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # แปลงข้อมูลวันที่ให้ถูกต้อง
            df['Start'] = pd.to_datetime(df['Start']).dt.date
            df['End'] = pd.to_datetime(df['End']).dt.date
            return df
        except:
            return pd.DataFrame(columns=["Project", "Activity", "Start", "End", "Status"])
    return pd.DataFrame(columns=["Project", "Activity", "Start", "End", "Status"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# โหลดข้อมูลเข้าสู่ระบบ
if 'master_df' not in st.session_state:
    st.session_state.master_df = load_data()

# --- 2. Sidebar สำหรับเลือกโปรเจกต์ ---
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

    st.markdown("---")
    project_list = st.session_state.master_df["Project"].unique().tolist()
    selected_project = st.selectbox("📂 เลือกโปรเจกต์:", options=project_list) if project_list else None

# --- 3. ส่วนหน้าจอหลัก (Main Interface) ---
if selected_project:
    st.title(f"📊 Timeline: {selected_project}")
    
    # ดึงเฉพาะข้อมูลของโปรเจกต์ที่เลือกออกมาแก้ไข
    current_project_mask = st.session_state.master_df["Project"] == selected_project
    project_df = st.session_state.master_df[current_project_mask].copy()
    
    st.subheader("📝 รายละเอียดกิจกรรม (พิมพ์เพื่อแก้ไข)")
    
    # แก้ไขข้อมูลผ่านตารางอัจฉริยะ
    edited_df = st.data_editor(
        project_df,
        column_order=("Activity", "Start", "End", "Status"),
        num_rows="dynamic",
        column_config={
            "Activity": st.column_config.TextColumn("กิจกรรม", required=True),
            "Start": st.column_config.DateColumn("วันเริ่ม", required=True, format="DD/MM/YYYY"),
            "End": st.column_config.DateColumn("วันเสร็จ", required=True, format="DD/MM/YYYY"),
            "Status": st.column_config.SelectboxColumn("สถานะ", options=["Pending", "In Progress", "Completed"])
        },
        use_container_width=True,
        key=f"editor_{selected_project}"
    )

    if st.button("💾 บันทึกข้อมูลลงระบบ (Save All)"):
        # กรองเอาโปรเจกต์อื่นออกมาไว้ก่อน
        other_projects_df = st.session_state.master_df[st.session_state.master_df["Project"] != selected_project]
        # บังคับให้คอลัมน์ Project เป็นชื่อที่เลือกเสมอ
        edited_df["Project"] = selected_project
        # รวมโปรเจกต์อื่นกับโปรเจกต์ที่แก้ใหม่เข้าด้วยกัน
        st.session_state.master_df = pd.concat([other_projects_df, edited_df], ignore_index=True)
        save_data(st.session_state.master_df)
        st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
        st.rerun()

    # --- 4. การแสดงผล Gantt Chart พร้อมสเกลละเอียด ---
    st.markdown("---")
    # กรองเฉพาะแถวที่มีข้อมูลพร้อมวาดกราฟ
    plot_df = edited_df.dropna(subset=['Activity', 'Start', 'End'])
    
    if not plot_df.empty:
        try:
            fig = px.timeline(
                plot_df,
                x_start="Start",
                x_end="End",
                y="Activity",
                color="Status",
                text="Activity",
                color_discrete_map={"Completed": "#2ecc71", "In Progress": "#f1c40f", "Pending": "#e74c3c"}
            )
            
            # ปรับแต่งสเกล X (วันที่) ให้เห็นเส้นตารางทุกวัน
            fig.update_xaxes(
                showgrid=True,
                gridcolor='LightGrey',
                dtick="D1",             # ช่องละ 1 วัน
                tickformat="%d %b",     # วันที่ เดือน
                side="top"              # สเกลอยู่ด้านบน
            )
            
            fig.update_yaxes(autorange="reversed", showgrid=True)
            
            fig.update_layout(
                height=300 + (len(plot_df) * 35),
                margin=dict(l=20, r=20, t=100, b=20),
                xaxis_title="📅 แผนงานรายวัน (Daily Timeline)",
                # เพิ่มเส้นบอกวันที่ปัจจุบัน
                shapes=[dict(
                    type='line', yref='paper', y0=0, y1=1,
                    xref='x', x0=date.today(), x1=date.today(),
                    line=dict(color="Red", width=2, dash="dash")
                )]
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"ไม่สามารถวาดกราฟได้: {e}")
    else:
        st.info("💡 กรุณากรอก Activity และวันที่ให้ครบถ้วนในตารางด้านบน")

else:
    st.info("👈 กรุณาเพิ่มชื่อโปรเจกต์ใหม่ที่เมนูด้านซ้ายเพื่อเริ่มต้นใช้งาน")
