# app.py
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fpdf import FPDF

# Custom Modules
from materials import MATERIAL_DB
from economics import calculate_operating_cost
from visuals3d import draw_process_simulation
from optimization import find_optimal_settings
from calculations import get_global_metrics, get_kinetics_data, get_spatial_log_df # <--- NEW IMPORT

st.set_page_config(page_title="Tunnel Dryer Pro", layout="wide")

# ==========================================
# SIDEBAR: NAVIGATION & GLOBAL INPUTS
# ==========================================
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["⚙️ Engineering Design", "🎬 Process Animation", "💰 Financial Analytics", "🤖 AI Optimization Hub"])
st.sidebar.markdown("---")

st.sidebar.header("Operating Parameters")

# Sidebar Inputs
selected_material = st.sidebar.selectbox("Select Material", list(MATERIAL_DB.keys()))
mat_data = MATERIAL_DB[selected_material]

feed_rate = st.sidebar.slider("Wet Feed Rate (kg/hr)", 50, 500, 100)
initial_moisture = st.sidebar.slider("Initial Moisture (%)", 10.0, 95.0, mat_data["init_m"]) / 100
final_moisture = st.sidebar.slider("Final Moisture (%)", 1.0, 20.0, mat_data["final_m"]) / 100
residence_time = st.sidebar.slider("Residence Time (hours)", 0.5, 10.0, 4.0)

belt_width = st.sidebar.slider("SS Belt Width (m)", 0.5, 3.0, 1.5)
loading_density = st.sidebar.slider("Loading Density (kg/m²)", 10, 50, int(mat_data["density"]))
air_velocity = st.sidebar.slider("Air Velocity (m/s)", 0.5, 5.0, 1.5)

# Dynamic Temp bounds
max_safe_temp = st.sidebar.number_input("Max Safe Temp (°C)", value=mat_data["max_temp"]) if selected_material == "Custom (Manual Entry)" else mat_data["max_temp"]
T_hot_in = st.sidebar.slider("Burner Temperature (°C)", 40, int(max_safe_temp), int(max_safe_temp))

flow_type = st.sidebar.radio("Airflow Configuration", ["Co-Current", "Counter-Current", "Compare Both"])
lpg_rate = st.sidebar.number_input("LPG Cost (₹/kg)", value=90.0)
elec_rate = st.sidebar.number_input("Electricity Rate (₹/kWh)", value=8.0)

# ==========================================
# FETCH DATA FROM CALCULATIONS ENGINE
# ==========================================
metrics = get_global_metrics(feed_rate, initial_moisture, final_moisture, residence_time, loading_density, belt_width, air_velocity, T_hot_in)

# ==========================================
# PAGE ROUTING (UI ONLY)
# ==========================================
if page == "⚙️ Engineering Design":
    st.header("📊 Engineering Simulation Results")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tunnel Length", f"{metrics['tunnel_length']:.2f} m")
    col2.metric("Moisture Evaporated", f"{metrics['moisture_removed']:.2f} kg/hr")
    col3.metric("Burner Load", f"{metrics['total_thermal_kw']:.1f} kW")
    col4.metric("Fan Power", f"{metrics['fan_kw']:.1f} kW")

    if metrics['tunnel_length'] > 15:
        st.warning("⚠️ **Length Warning:** Design exceeds standard factory footprint.")

    # Fetch graph data
    x_range, m_co, t_co, m_cnt, t_cnt = get_kinetics_data(metrics['tunnel_length'], initial_moisture, final_moisture, T_hot_in)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if flow_type in ["Co-Current", "Compare Both"]:
        fig.add_trace(go.Scatter(x=x_range, y=m_co, name='Moisture (Co)', line=dict(color='#4CA5FF', width=4)), secondary_y=False)
        fig.add_trace(go.Scatter(x=x_range, y=t_co, name='Air Temp (Co)', line=dict(color='#FF5A5A', width=2, dash='dot')), secondary_y=True)
    if flow_type in ["Counter-Current", "Compare Both"]:
        fig.add_trace(go.Scatter(x=x_range, y=m_cnt, name='Moisture (Counter)', line=dict(color='#00D4FF', width=4, dash='dash')), secondary_y=False)
        fig.add_trace(go.Scatter(x=x_range, y=t_cnt, name='Air Temp (Counter)', line=dict(color='#FF8C00', width=2, dash='dashdot')), secondary_y=True)

    fig.update_layout(
        template="plotly_dark", 
        title_text=f"Drying Kinetics (Burner: {T_hot_in}°C)", 
        # Push legend higher (y=1.15) and anchor it to the right
        legend=dict(orientation="h", yanchor="bottom", y=1.15, xanchor="right", x=1),
        # Add 80 pixels of extra space at the top so the title/legend don't crush the graph
        margin=dict(t=80) 
    )
    fig.update_xaxes(title_text="Distance inside Tunnel (m)", range=[-0.1, metrics['tunnel_length'] + 0.1])
    fig.update_yaxes(title_text="Moisture Content (%)", color="#4CA5FF", secondary_y=False)
    fig.update_yaxes(title_text="Air Temperature (°C)", color="#FF5A5A", secondary_y=True, range=[35, T_hot_in + 10])

    st.plotly_chart(fig, use_container_width=True)

    # Fetch and display the Pandas Table
    st.markdown("### 📋 Spatial Data Log")
    df_log = get_spatial_log_df(metrics['tunnel_length'], initial_moisture, final_moisture, T_hot_in, flow_type)
    st.table(df_log)

    def create_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Tunnel Dryer Technical Report", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Length: {metrics['tunnel_length']:.2f} m | Thermal Load: {metrics['total_thermal_kw']:.1f} kW", ln=True)
        return pdf.output(dest="S").encode("latin-1")
    st.download_button("📥 Download PDF", data=create_pdf(), file_name="Report.pdf")

elif page == "🎬 Process Animation":
    st.header("🎬 Real-Time Process Simulation")
    draw_process_simulation(flow_type, metrics['tunnel_length'], belt_width, air_velocity)

elif page == "💰 Financial Analytics":
    st.header("💰 Operational Cost Analysis")
    costs = calculate_operating_cost(metrics['total_thermal_kw'], metrics['fan_kw'], lpg_rate, elec_rate)
    c1, c2, c3 = st.columns(3)
    c1.metric("LPG Cost/hr", f"₹ {costs['lpg_cost_hr']:,.2f}")
    c2.metric("Elec Cost/hr", f"₹ {costs['elec_cost_hr']:,.2f}")
    c3.metric("Total Cost/hr", f"₹ {costs['total_cost_hr']:,.2f}")

    fig_pie = go.Figure(data=[go.Pie(labels=['LPG', 'Elec'], values=[costs['lpg_cost_hr'], costs['elec_cost_hr']], hole=.4, marker_colors=['#FF5A5A', '#4CA5FF'])])
    fig_pie.update_layout(template="plotly_dark", title="Utility Cost Distribution")
    st.plotly_chart(fig_pie, use_container_width=True)

elif page == "🤖 AI Optimization Hub":
    st.header("🤖 Parameter Optimization")
    if st.button("🚀 Run Optimization Engine"):
        opt_v, opt_t, opt_c, matrix = find_optimal_settings(feed_rate, initial_moisture, final_moisture, loading_density, lpg_rate, elec_rate)
        st.success("Optimization Successful!")
        r1, r2, r3 = st.columns(3)
        r1.metric("Optimal Velocity", f"{opt_v:.2f} m/s")
        r2.metric("Optimal Time", f"{opt_t:.2f} hrs")
        r3.metric("Target Cost", f"₹ {opt_c:.2f}/hr")

        fig_opt = go.Figure(data=[go.Surface(z=matrix[2], x=matrix[0], y=matrix[1], colorscale='Viridis')])
        fig_opt.update_layout(template="plotly_dark", scene=dict(xaxis_title='Velocity', yaxis_title='Time', zaxis_title='Cost'), height=700)
        st.plotly_chart(fig_opt, use_container_width=True)