import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import os

# 1. ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Engineering Project Timeline", layout="wide")

# 2. ระบบจัดการฐานข้อมูล (CSV)
DB_FILE = "project_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # แปลง String กลับเป็น Date Object
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

# 3. Sidebar: จัดการโปรเจกต์
with st.sidebar:
    st.title("🏗️ Project Management")
    new_p = st.text_input("ชื่อโปรเจกต์ใหม่:")
    if st.button("➕ สร้างโปรเจกต์"):
        if new_p:
            new_row = pd.DataFrame([{
                "Project": new_p, 
                "Activity": "แผนงานเริ่มต้น", 
                "Start": date.today(), 
                "End": date.today(), 
                "Status": "Pending"
            }])
            st.session_state.master_df = pd.concat([st.session_state.master_df, new_row], ignore_index=True)
            save_data(st.session_state.master_df)
            st.rerun()

    st.markdown("---")
    project_list = st.session_state.master_df["Project"].unique().tolist()
    selected_project = st.selectbox("📂 เลือกโปรเจกต์ที่จะดู:", options=project_list) if project_list else None

# 4. หน้าจอหลัก: การแก้ไขและแสดงผล
if selected_project:
    st.title(f"📊 Timeline: {selected_project}")
    
    # ดึงข้อมูลของโปรเจกต์ที่เลือก
    mask = st.session_state.master_df["Project"] == selected_project
    project_df = st.session_state.master_df[mask].copy().reset_index(drop=True)
    
    st.subheader("📝 รายละเอียดกิจกรรม (กรอกข้อมูลในตารางด้านล่าง)")
    # ใช้ Data Editor เพื่อให้พิมพ์แก้ไขได้เหมือน Excel
    edited_df = st.data_editor(
        project_df,
        column_order=("Activity", "Start", "End", "Status"),
        num_rows="dynamic", # ให้กดเพิ่มแถวเองได้ที่ท้ายตาราง
        column_config={
            "Activity": st.column_config.TextColumn("กิจกรรม", required=True),
            "Start": st.column_config.DateColumn("วันเริ่ม", required=True, format="DD/MM/YYYY"),
            "End": st.column_config.DateColumn("วันเสร็จ", required=True, format="DD/MM/YYYY"),
            "Status": st.column_config.SelectboxColumn("สถานะ", options=["Pending", "In Progress", "Completed"])
        },
        use_container_width=True,
        key=f"editor_{selected_project}"
    )

    if st.button("💾 บันทึกการแก้ไข (Save All)"):
        # กรองเอาโปรเจกต์อื่นออกก่อน แล้วรวมอันที่แก้ใหม่เข้าไป
        other_projects = st.session_state.master_df[st.session_state.master_df["Project"] != selected_project]
        edited_df["Project"] = selected_project
        st.session_state.master_df = pd.concat([other_projects, edited_df], ignore_index=True)
        save_data(st.session_state.master_df)
        st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
        st.rerun()

    # 5. การแสดงผล Gantt Chart (หัวใจสำคัญคือการแยกบรรทัด)
    st.markdown("---")
    # กรองเฉพาะแถวที่มีข้อมูล "ครบถ้วน" เท่านั้นมาวาดกราฟ
    plot_df = edited_df.dropna(subset=['Activity', 'Start', 'End']).copy()
    
    if not plot_df.empty:
        try:
            # สร้างคอลัมน์พิเศษ "Task_Label" เพื่อบังคับให้ Plotly แยกบรรทัดให้ครบทุกแถว (แม้ชื่อกิจกรรมจะซ้ำกัน)
            plot_df['Task_Label'] = plot_df['Activity'] + " (#" + (plot_df.index + 1).astype(str) + ")"
            
            fig = px.timeline(
                plot_df,
                x_start="Start",
                x_end="End",
                y="Task_Label", # ใช้คอลัมน์ที่ Unique เพื่อให้โชว์ครบทุกบรรทัด
                color="Status",
                text="Activity", # แสดงชื่อกิจกรรมปกติบนแท่งกราฟ
                color_discrete_map={"Completed": "#2ecc71", "In Progress": "#f1c40f", "Pending": "#e74c3c"}
            )
            
            # ปรับปรุงสเกลวันที่และเส้นตาราง (Grid)
            fig.update_xaxes(
                showgrid=True,
                gridcolor='LightGrey',
                dtick="D1",             # สเกลช่องละ 1 วัน
                tickformat="%d %b",     # วันที่ เดือน
                side="top"              # สเกลวันที่อยู่ด้านบน
            )
            
            fig.update_yaxes(autorange="reversed", title="") # เรียงงานแรกไว้บนสุด
            
            fig.update_layout(
                height=300 + (len(plot_df) * 45), # ปรับความสูงกราฟตามจำนวนงานที่กรอก
                margin=dict(l=20, r=20, t=100, b=20),
                xaxis_title="📅 แผนงานรายวัน (Timeline)",
                # เส้นบอกวันที่ปัจจุบัน (Today Line)
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
        st.info("💡 กรุณากรอกชื่อกิจกรรม วันเริ่มต้น และวันเสร็จสิ้น ให้ครบถ้วนในตารางด้านบน")
else:
    st.info("👈 เริ่มต้นใช้งานโดยการเพิ่มชื่อโปรเจกต์ที่เมนูด้านซ้าย")
