if not plot_df.empty:
            try:
                fig = px.timeline(
                    plot_df,
                    x_start="Start",
                    x_end="End",
                    y="Activity",
                    color="Status",
                    text="Activity", # แสดงชื่อกิจกรรมบนแท่งกราฟเลย
                    color_discrete_map={"Completed": "#2ecc71", "In Progress": "#f1c40f", "Pending": "#e74c3c"}
                )

                # --- ส่วนการปรับสเกลให้ไม่โล่ง ---
                fig.update_yaxes(autorange="reversed", showgrid=True) # แสดงเส้นกริดแนวนอน
                
                fig.update_xaxes(
                    showgrid=True,             # แสดงเส้นกริดแนวตั้ง (เส้นเทียบวัน)
                    gridwidth=1, 
                    gridcolor='LightGrey',
                    dtick="D1",                # บังคับให้แสดงสเกลทุกๆ 1 วัน (ถ้าช่วงงานสั้น)
                    # ถ้าช่วงงานยาวมาก ให้เปลี่ยน D1 เป็น "M1" (เดือน) หรือ 604800000 (1 สัปดาห์)
                    tickformat="%d %b\n%Y",    # รูปแบบวันที่: วัน เดือน ปี (ขึ้นบรรทัดใหม่)
                    side="top"                 # เอาสเกลวันที่ไว้ด้านบนให้ดูง่ายเหมือน MS Project
                )

                fig.update_layout(
                    xaxis_title="Timeline (Day-by-Day Scale)",
                    yaxis_title="",
                    height=300 + (len(plot_df) * 40), # ปรับความสูงตามจำนวนงาน
                    margin=dict(l=20, r=20, t=100, b=20),
                    showlegend=True,
                    legend_alignment="left",
                    # เพิ่มเส้นบอก "วันนี้" (Today Line)
                    shapes=[dict(
                        type='line', yref='paper', y0=0, y1=1,
                        xref='x', x0=date.today(), x1=date.today(),
                        line=dict(color="Red", width=2, dash="dash")
                    )],
                    annotations=[dict(
                        x=date.today(), y=0, xref="x", yref="paper",
                        text="Today", showarrow=False, font=dict(color="Red")
                    )]
                )
                
                # ทำให้แท่งกราฟเล็กลงหน่อยเพื่อให้เห็นเส้นสเกลชัดขึ้น
                fig.update_traces(width=0.6) 
                
                st.plotly_chart(fig, use_container_width=True)
