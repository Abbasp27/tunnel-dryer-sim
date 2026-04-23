# app.py
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fpdf import FPDF
import tempfile
import os

# Custom Modules
from materials import MATERIAL_DB
from economics import calculate_operating_cost
from visuals3d import draw_process_simulation
from optimization import find_optimal_settings
from calculations import get_global_metrics, get_kinetics_data, get_spatial_log_df 

st.set_page_config(page_title="Industrial Tunnel Dryer Simulation", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# PERFORMANCE CACHING (Memory Engine)
# ==========================================
@st.cache_data
def cached_get_global_metrics(f_rate, i_m, f_m, r_time, l_dens, b_width, a_vel, t_hot):
    return get_global_metrics(f_rate, i_m, f_m, r_time, l_dens, b_width, a_vel, t_hot)

@st.cache_data
def cached_get_kinetics_data(t_len, i_m, f_m, t_hot):
    return get_kinetics_data(t_len, i_m, f_m, t_hot)

@st.cache_data
def cached_get_spatial_log_df(t_len, i_m, f_m, t_hot, f_type):
    return get_spatial_log_df(t_len, i_m, f_m, t_hot, f_type)

@st.cache_data
def cached_find_optimal_settings(mat_name, max_t, f_rate, i_m, f_m, l_dens, lpg_r, elec_r):
    return find_optimal_settings(mat_name, max_t, f_rate, i_m, f_m, l_dens, lpg_r, elec_r)

# ==========================================
# SIDEBAR: MASTER CONTROL PANEL (Inputs Only)
# ==========================================
st.sidebar.title("🧰 Master Control Panel")
st.sidebar.markdown("Configure physical and thermodynamic parameters.")

selected_material = st.sidebar.selectbox("Select Material Profile", list(MATERIAL_DB.keys()))
mat_data = MATERIAL_DB[selected_material]

# --- SECTION 1: MECHANICAL & FEED ---
st.sidebar.subheader("🔩 Mechanical Settings")
feed_rate = st.sidebar.number_input("Wet Feed Rate (kg/hr)", min_value=10, max_value=2000, value=100, step=10)
loading_density = st.sidebar.number_input("Loading Density (kg/m²)", min_value=1, max_value=200, value=int(mat_data["density"]), step=5)

ideal_speed = float(mat_data["ideal_belt_speed"])
belt_speed = st.sidebar.number_input("Belt Speed (m/min)", min_value=0.01, max_value=2.00, value=ideal_speed, step=0.01, format="%.2f")

# --- SECTION 2: THERMODYNAMICS ---
st.sidebar.subheader("🌡️ Thermodynamic Settings")
initial_moisture = st.sidebar.number_input("Initial Moisture (%)", min_value=1.0, max_value=99.0, value=float(mat_data["init_m"]), step=1.0) / 100
final_moisture = st.sidebar.number_input("Final Moisture (%)", min_value=0.1, max_value=50.0, value=float(mat_data["final_m"]), step=0.5) / 100

ideal_time = float(mat_data["ideal_time"])
residence_time = st.sidebar.number_input("Residence Time (hours)", min_value=0.1, max_value=24.0, value=ideal_time, step=0.5)

if selected_material == "Corn":
    ideal_vel = st.sidebar.number_input("Ideal Air Velocity (m/s)", value=float(mat_data["ideal_vel"]), step=0.1)
else:
    ideal_vel = float(mat_data["ideal_vel"])

air_velocity = st.sidebar.number_input("Air Velocity (m/s)", min_value=0.1, max_value=15.0, value=ideal_vel, step=0.1)

# ---> UPDATE: Load both new variables <---
default_ideal_temp = MATERIAL_DB[selected_material]["ideal_temp"] 
absolute_max_temp = MATERIAL_DB[selected_material]["max_temp"]   

# ---> UPDATE: Use both new variables in the input <---
T_hot_in = st.sidebar.number_input(
    f"Burner Temp (Max {absolute_max_temp}°C)", 
    min_value=20, 
    max_value=int(absolute_max_temp), 
    value=int(default_ideal_temp), 
    step=5
)

flow_type = st.sidebar.radio("Airflow Configuration", ["Co-Current", "Counter-Current", "Compare Both"])
lpg_rate = st.sidebar.number_input("LPG Cost (₹/kg)", value=90.0, step=1.0)
elec_rate = st.sidebar.number_input("Electricity Rate (₹/kWh)", value=8.0, step=0.5)


# ==========================================
# CORE KINEMATIC & MECHANICAL CALCULATIONS
# ==========================================
dynamic_tunnel_length = belt_speed * (residence_time * 60)
dynamic_belt_width = feed_rate / (belt_speed * 60 * loading_density)
water_evap_kg_hr = feed_rate * ((initial_moisture - final_moisture) / (1.0 - final_moisture))

metrics = cached_get_global_metrics(feed_rate, initial_moisture, final_moisture, residence_time, loading_density, dynamic_belt_width, air_velocity, T_hot_in)
metrics['tunnel_length'] = dynamic_tunnel_length

# ==========================================
# MAIN PAGE: MODERN TABBED NAVIGATION
# ==========================================
st.title(f"Industrial Tunnel Dryer Simulation: {selected_material}")

tab1, tab2, tab3, tab4 = st.tabs([
    "📐 Engineering Schematics", 
    "🔄 Real-Time Process", 
    "🏦 Utility Economics", 
    "⚡ High-Performance AI"
])

# --- TAB 1: ENGINEERING DESIGN ---
with tab1:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Tunnel Length", f"{dynamic_tunnel_length:.2f} m")
    col2.metric("Belt Speed", f"{belt_speed:.2f} m/min")
    col3.metric("Req. Belt Width", f"{dynamic_belt_width:.2f} m")
    col4.metric("Burner Load", f"{metrics['total_thermal_kw']:.1f} kW")
    col5.metric("Fan Power", f"{metrics['fan_kw']:.1f} kW")

    if dynamic_tunnel_length > 25:
        st.warning("⚠️ **Length Warning:** Industrial footprint is very large.")
    if dynamic_belt_width > 3.0:
        st.error("⚠️ **Width Warning:** Belt width exceeds standard manufacturing limits (3m).")

    x_range, m_co, t_co, m_cnt, t_cnt = cached_get_kinetics_data(metrics['tunnel_length'], initial_moisture, final_moisture, T_hot_in)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if flow_type in ["Co-Current", "Compare Both"]:
        fig.add_trace(go.Scatter(x=x_range, y=m_co, name='Moisture (Co)', line=dict(color='#4CA5FF', width=4)), secondary_y=False)
        fig.add_trace(go.Scatter(x=x_range, y=t_co, name='Air Temp (Co)', line=dict(color='#FF5A5A', width=2, dash='dot')), secondary_y=True)
    if flow_type in ["Counter-Current", "Compare Both"]:
        fig.add_trace(go.Scatter(x=x_range, y=m_cnt, name='Moisture (Counter)', line=dict(color='#00D4FF', width=4, dash='dash')), secondary_y=False)
        fig.add_trace(go.Scatter(x=x_range, y=t_cnt, name='Air Temp (Counter)', line=dict(color='#FF8C00', width=2, dash='dashdot')), secondary_y=True)

    fig.update_layout(template="plotly_dark", title_text=f"Drying Kinetics (Burner: {T_hot_in}°C)", legend=dict(orientation="h", yanchor="bottom", y=1.15, xanchor="right", x=1), margin=dict(t=100))
    fig.update_xaxes(title_text="Distance inside Tunnel (m)", range=[-0.2, metrics['tunnel_length'] + 0.2])
    fig.update_yaxes(title_text="Moisture Content (%)", color="#4CA5FF", secondary_y=False)
    fig.update_yaxes(title_text="Air Temperature (°C)", color="#FF5A5A", secondary_y=True, range=[35, T_hot_in + 10])

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Spatial Data Log")
    df_log = cached_get_spatial_log_df(metrics['tunnel_length'], initial_moisture, final_moisture, T_hot_in, flow_type)
    
    t_col1, t_col2 = st.columns([3, 1])
    with t_col1:
        st.dataframe(df_log, use_container_width=True, height=200)
    with t_col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        def create_pdf(current_fig, dataframe):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            def add_section_header(title):
                pdf.ln(4)
                pdf.set_fill_color(226, 232, 240)
                pdf.set_text_color(15, 23, 42)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 8, txt=f"  {title}", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Arial", '', 11)
                pdf.ln(2)

            def add_line(key, value):
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(60, 6, txt=f"{key}:")
                pdf.set_font("Arial", '', 10)
                pdf.cell(100, 6, txt=str(value), ln=True)

            pdf.set_fill_color(30, 41, 59)
            pdf.rect(0, 0, 210, 35, 'F')
            pdf.set_font("Arial", 'B', 22)
            pdf.set_text_color(255, 255, 255)
            pdf.set_y(8)
            pdf.cell(0, 10, txt="COMPREHENSIVE DIGITAL TWIN REPORT", ln=True, align='C')
            pdf.set_font("Arial", 'I', 12)
            pdf.set_text_color(148, 163, 184)
            pdf.cell(0, 8, txt=f"Material Profile: {selected_material}", ln=True, align='C')
            
            pdf.set_y(40)
            
            add_section_header("A. Defined Input Parameters")
            add_line("Wet Feed Rate", f"{feed_rate} kg/hr")
            add_line("Loading Density", f"{loading_density} kg/m²")
            add_line("Initial Moisture (wb)", f"{initial_moisture * 100:.1f} %")
            add_line("Final Moisture Target", f"{final_moisture * 100:.1f} %")
            add_line("Airflow Configuration", flow_type)
            add_line("Target Residence Time", f"{residence_time} hours")
            
            add_section_header("B. Calculated Mechanical Constraints")
            add_line("Required Tunnel Length", f"{dynamic_tunnel_length:.2f} meters")
            add_line("Required SS Belt Width", f"{dynamic_belt_width:.2f} meters")
            add_line("Set Belt Speed", f"{belt_speed:.2f} m/min")
            
            add_section_header("C. Thermodynamic Sizing")
            add_line("Burner Inlet Temperature", f"{T_hot_in} °C")
            add_line("Aerodynamic Velocity", f"{air_velocity} m/s")
            add_line("Evaporation Rate", f"{water_evap_kg_hr:.1f} kg of water / hour")
            add_line("Total Thermal Burner Load", f"{metrics['total_thermal_kw']:.1f} kW")
            add_line("Electric Fan/Blower Load", f"{metrics['fan_kw']:.1f} kW")
            
            pdf_costs = calculate_operating_cost(metrics['total_thermal_kw'], metrics['fan_kw'], lpg_rate, elec_rate)
            add_section_header("D. Utility Economics")
        
            add_line("Assumed LPG Rate", f"Rs. {lpg_rate:.2f} / kg")
            add_line("Assumed Electricity Rate", f"Rs. {elec_rate:.2f} / kWh")
            add_line("Hourly LPG Cost", f"Rs. {pdf_costs['lpg_cost_hr']:,.2f}")
            add_line("Hourly Electricity Cost", f"Rs. {pdf_costs['elec_cost_hr']:,.2f}")
            
            pdf.set_font("Arial", 'B', 11)
            pdf.set_text_color(34, 139, 34)
            pdf.cell(60, 8, txt="Total Operating Cost:")
            pdf.cell(100, 8, txt=f"Rs. {pdf_costs['total_cost_hr']:,.2f} / hour", ln=True)
            pdf.set_text_color(0, 0, 0)

            if dynamic_belt_width > 3.0 or dynamic_tunnel_length > 25.0:
                pdf.ln(5)
                pdf.set_fill_color(254, 226, 226)
                pdf.set_text_color(185, 28, 28)
                pdf.set_font("Arial", 'B', 11)
                pdf.cell(0, 8, txt="  E. CRITICAL MANUFACTURING WARNINGS", ln=True, fill=True)
                pdf.set_font("Arial", 'B', 10)
                if dynamic_belt_width > 3.0:
                    pdf.cell(0, 8, txt=f"  [!] BELT WIDTH ERROR: {dynamic_belt_width:.2f}m exceeds the maximum 3.0m structural limit.", ln=True)
                if dynamic_tunnel_length > 25.0:
                    pdf.cell(0, 8, txt=f"  [!] FOOTPRINT WARNING: {dynamic_tunnel_length:.2f}m tunnel may exceed standard factory floor space.", ln=True)
                pdf.set_text_color(0, 0, 0)
            
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(200, 10, txt="Spatial Drying Kinetics Graph", ln=True)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                pdf_fig = go.Figure(current_fig)
                pdf_fig.update_layout(template="plotly_white", paper_bgcolor="white", plot_bgcolor="white")
                pdf_fig.write_image(tmpfile.name, width=800, height=400)
                pdf.image(tmpfile.name, x=15, w=180)
                os.remove(tmpfile.name)
                
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="Process Data Log (Spatial Discretization)", ln=True)
            pdf.ln(2)
            
            pdf.set_font("Arial", 'B', 8) 
            pdf.set_fill_color(59, 130, 246)
            pdf.set_text_color(255, 255, 255)
            col_width = 190 / len(dataframe.columns)
            
            short_cols = [str(c).replace("Counter-Current", "Counter").replace("Co-Current", "Co").replace("Moisture", "Moist") for c in dataframe.columns]
            for col_name in short_cols:
                pdf.cell(col_width, 8, txt=col_name, border=1, fill=True, align='C')
            pdf.ln()
            
            pdf.set_font("Arial", '', 9)
            pdf.set_text_color(0, 0, 0)
            for i, row in dataframe.iterrows():
                if i % 2 == 0:
                    pdf.set_fill_color(241, 245, 249)
                else:
                    pdf.set_fill_color(255, 255, 255)
                for item in row:
                    val = f"{item:.2f}" if isinstance(item, float) else str(item)
                    pdf.cell(col_width, 7, txt=val, border=1, fill=True, align='C')
                pdf.ln()
            return pdf.output(dest="S").encode("latin-1")
            
        st.download_button("📥 Export PDF Report", data=create_pdf(fig, df_log), file_name=f"Report_{selected_material.replace(' ', '_')}.pdf", type="primary", use_container_width=True)

# --- TAB 2: PROCESS ANIMATION ---
with tab2:
    draw_process_simulation(flow_type, metrics['tunnel_length'], dynamic_belt_width, air_velocity, selected_material, initial_moisture, final_moisture, T_hot_in)

# --- TAB 3: FINANCIAL ANALYTICS ---
with tab3:
    costs = calculate_operating_cost(metrics['total_thermal_kw'], metrics['fan_kw'], lpg_rate, elec_rate)
    c1, c2, c3 = st.columns(3)
    c1.metric("LPG Cost/hr", f"Rs. {costs['lpg_cost_hr']:,.2f}")
    c2.metric("Elec Cost/hr", f"Rs. {costs['elec_cost_hr']:,.2f}")
    c3.metric("Total Cost/hr", f"Rs. {costs['total_cost_hr']:,.2f}")

    fig_pie = go.Figure(data=[go.Pie(labels=['LPG', 'Elec'], values=[costs['lpg_cost_hr'], costs['elec_cost_hr']], hole=.4, marker_colors=['#FF5A5A', '#4CA5FF'])])
    fig_pie.update_layout(template="plotly_dark", title="Utility Cost Distribution")
    st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 4: AI OPTIMIZATION Hub ---
with tab4:
    st.markdown("Search thousands of parameter combinations to find the lowest operational cost.")
    if st.button("🚀 Run Optimization Engine", type="primary"):
        with st.spinner("Crunching mass balances and kinematic constraints..."):
            
            # ---> UPDATE: Make sure the AI uses absolute_max_temp <---
            opt_v, opt_t, opt_c, saving_pct, notes, matrix = cached_find_optimal_settings(
                selected_material, absolute_max_temp, feed_rate, initial_moisture, final_moisture, loading_density, lpg_rate, elec_rate
            )
            
            ai_tunnel_length = belt_speed * (opt_t * 60)
            ai_belt_width = feed_rate / (belt_speed * 60 * loading_density)
            
            # 3 equal columns for the numbers
            r1, r2, r3 = st.columns(3)
            r1.metric("Optimal Air Velocity", f"{opt_v:.1f} m/s")
            r2.metric("Optimal Res. Time", f"{opt_t:.1f} hrs")
            r3.metric("Projected Savings", f"{saving_pct}%")

            # A nice, wide banner for the text notes
            st.info(f"**AI Analysis Notes:** {notes}")
            
            if ai_belt_width > 3.0:
                st.error(f"❌ **AI Rejected:** Requires {ai_belt_width:.2f}m belt (Exceeds 3.0m limit).")
            else:
                st.success("✅ **AI Approved:** Cost-effective and structurally viable!")

            fig_opt = go.Figure(data=[go.Surface(z=matrix[2], x=matrix[0], y=matrix[1], colorscale='Viridis')])
            fig_opt.update_layout(template="plotly_dark", title="Cost Optimization Matrix", scene=dict(xaxis_title='Velocity', yaxis_title='Time', zaxis_title='Cost'), height=600)
            st.plotly_chart(fig_opt, use_container_width=True)
