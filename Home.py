# --- 4. การแสดงผล Gantt Chart (ปรับปรุงให้โชว์ครบทุกแถว) ---
    st.markdown("---")
    # กรองเฉพาะแถวที่มีข้อมูลครบ
    plot_df = edited_df.dropna(subset=['Activity', 'Start', 'End']).copy()
    
    if not plot_df.empty:
        try:
            # สร้างคอลัมน์พิเศษ "Label" เพื่อป้องกันชื่อซ้ำแล้วโดนยุบบรรทัด
            # โดยการเอาเลขลำดับแถวมาต่อท้ายชื่อกิจกรรม
            plot_df['Display_Name'] = plot_df['Activity'] + " (" + (plot_df.index + 1).astype(str) + ")"

            fig = px.timeline(
                plot_df,
                x_start="Start",
                x_end="End",
                y="Display_Name",  # ใช้ชื่อที่ต่อท้ายเลขลำดับ เพื่อบังคับแยกบรรทัด
                color="Status",
                text="Activity",    # แต่บนแท่งกราฟให้โชว์แค่ชื่อกิจกรรมปกติ
                color_discrete_map={"Completed": "#2ecc71", "In Progress": "#f1c40f", "Pending": "#e74c3c"}
            )
            
            # ปรับแต่งสเกลวันที่ (X-Axis)
            fig.update_xaxes(
                showgrid=True,
                gridcolor='LightGrey',
                dtick="D1",             # ช่องละ 1 วัน
                tickformat="%d %b",
                side="top"
            )
            
            # ปรับแกน Y ให้เรียงจากบนลงล่าง
            fig.update_yaxes(autorange="reversed", title="ลำดับกิจกรรม")
            
            fig.update_layout(
                height=300 + (len(plot_df) * 45), # ปรับความสูงให้พอดีกับจำนวนแถว
                margin=dict(l=20, r=20, t=100, b=20),
                xaxis_title="📅 แผนงานรายวัน (Daily Timeline)",
                shapes=[dict(
                    type='line', yref='paper', y0=0, y1=1,
                    xref='x', x0=date.today(), x1=date.today(),
                    line=dict(color="Red", width=2, dash="dash")
                )]
            )
            
            # ทำให้แท่งกราฟดูหนาขึ้นและอ่านง่าย
            fig.update_traces(marker_line_color='rgb(8,48,107)', marker_line_width=1.5, opacity=0.8)
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"ไม่สามารถวาดกราฟได้: {e}")
