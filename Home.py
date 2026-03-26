# --- ส่วนการแสดงผล Gantt Chart (ปรับปรุงจุดที่ทำให้แท่งหาย) ---
    st.markdown("---")
    
    # 1. กรองเฉพาะแถวที่มีข้อมูลครบ และต้องเป็นชนิด datetime/date จริงๆ
    plot_df = edited_df.copy()
    plot_df['Start'] = pd.to_datetime(plot_df['Start'], errors='coerce')
    plot_df['End'] = pd.to_datetime(plot_df['End'], errors='coerce')
    
    # ลบแถวที่มีวันที่ว่าง (NaT) ทิ้งไปก่อนวาด
    plot_df = plot_df.dropna(subset=['Start', 'End', 'Activity'])
    
    # กรองเฉพาะแถวที่ วันเสร็จ >= วันเริ่ม เท่านั้น
    plot_df = plot_df[plot_df['End'] >= plot_df['Start']]
    
    if not plot_df.empty:
        try:
            # สร้าง Label แยกบรรทัด
            plot_df['Task_Label'] = plot_df['Activity'] + " (#" + (plot_df.index + 1).astype(str) + ")"
            
            fig = px.timeline(
                plot_df,
                x_start="Start",
                x_end="End",
                y="Task_Label",
                color="Status",
                text="Activity",
                color_discrete_map={"Completed": "#2ecc71", "In Progress": "#f1c40f", "Pending": "#e74c3c"}
            )
            
            # ปรับปรุงสเกล X
            fig.update_xaxes(showgrid=True, gridcolor='LightGrey', dtick="D1", tickformat="%d %b", side="top")
            fig.update_yaxes(autorange="reversed")
            
            fig.update_layout(
                height=300 + (len(plot_df) * 50), # เพิ่มความหนาของแท่งให้เห็นชัดขึ้น
                margin=dict(l=20, r=20, t=100, b=20),
                xaxis_title="📅 แผนงานรายวัน (Timeline)",
                shapes=[dict(
                    type='line', yref='paper', y0=0, y1=1,
                    xref='x', x0=date.today(), x1=date.today(),
                    line=dict(color="Red", width=2, dash="dash")
                )]
            )
            # ปรับแท่งกราฟให้หนาขึ้น
            fig.update_traces(width=0.7)
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error drawing graph: {e}")
    else:
        st.warning("⚠️ กรุณาตรวจสอบว่ากรอก 'วันเริ่ม' และ 'วันเสร็จ' ครบถ้วน และวันเสร็จต้องไม่มาก่อนวันเริ่มครับ")
