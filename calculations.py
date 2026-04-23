# calculations.py
import numpy as np
import pandas as pd

def get_global_metrics(feed_rate, initial_m, final_m, residence_time, density, width, air_vel, t_hot):
    """Calculates top-level mechanical and thermal loads."""
    moisture_removed = feed_rate * ((initial_m - final_m) / (1 - final_m))
    belt_area = (feed_rate * residence_time) / density
    tunnel_length = belt_area / width
    
    # Thermodynamics
    Q_evap = (moisture_removed * 2260) / 3600  
    Q_air = ((moisture_removed / 0.022) * 1.006 * max(t_hot - 30, 10)) / 3600  
    total_thermal_kw = (Q_evap + Q_air) * 1.15  
    fan_kw = 1.2 * (air_vel ** 3) * width
    
    return {
        "moisture_removed": moisture_removed,
        "tunnel_length": tunnel_length,
        "total_thermal_kw": total_thermal_kw,
        "fan_kw": fan_kw
    }

def get_kinetics_data(tunnel_length, initial_m, final_m, t_hot, steps=100):
    """Calculates the physical curves for the drying process."""
    x_range = np.linspace(0, tunnel_length, steps)
    z = x_range / tunnel_length  
    t_cool = 45.0  

    # Co-Current Physics
    k_t_co, k_m_co = 4.0, 2.0
    t_co = t_cool + (t_hot - t_cool) * (np.exp(-k_t_co * z) - np.exp(-k_t_co)) / (1 - np.exp(-k_t_co))
    m_co = (final_m + (initial_m - final_m) * (np.exp(-k_m_co * z) - np.exp(-k_m_co)) / (1 - np.exp(-k_m_co))) * 100

    # Counter-Current Physics
    k_t_cnt, k_m_cnt = 3.0, 2.5
    t_cnt = t_cool + (t_hot - t_cool) * (np.exp(k_t_cnt * z) - 1) / (np.exp(k_t_cnt) - 1)
    m_cnt = (initial_m - (initial_m - final_m) * (np.exp(k_m_cnt * z) - 1) / (np.exp(k_m_cnt) - 1)) * 100

    return x_range, m_co, t_co, m_cnt, t_cnt

def get_spatial_log_df(tunnel_length, initial_m, final_m, t_hot, flow_type):
    """Generates the Pandas DataFrame for the Spatial Data Log."""
    table_x = np.arange(0, tunnel_length + 0.1, 2) 
    if table_x[-1] < tunnel_length:
        table_x = np.append(table_x, tunnel_length)

    # Get data specifically for these exact points
    _, m_co, t_co, m_cnt, t_cnt = get_kinetics_data(tunnel_length, initial_m, final_m, t_hot, steps=len(table_x))
    
    # Recalculate z manually for these specific points to match exact distances
    z = table_x / tunnel_length
    t_cool = 45.0
    t_co = t_cool + (t_hot - t_cool) * (np.exp(-4.0 * z) - np.exp(-4.0)) / (1 - np.exp(-4.0))
    m_co = (final_m + (initial_m - final_m) * (np.exp(-2.0 * z) - np.exp(-2.0)) / (1 - np.exp(-2.0))) * 100
    t_cnt = t_cool + (t_hot - t_cool) * (np.exp(3.0 * z) - 1) / (np.exp(3.0) - 1)
    m_cnt = (initial_m - (initial_m - final_m) * (np.exp(2.5 * z) - 1) / (np.exp(2.5) - 1)) * 100

    table_data = {"Distance (m)": [f"{x:.1f}" for x in table_x]}

    if flow_type in ["Co-Current", "Compare Both"]:
        table_data["Co-Current Moisture (%)"] = [f"{m:.1f}" for m in m_co]
        table_data["Co-Current Temp (°C)"] = [f"{t:.1f}" for t in t_co]

    if flow_type in ["Counter-Current", "Compare Both"]:
        table_data["Counter-Current Moisture (%)"] = [f"{m:.1f}" for m in m_cnt]
        table_data["Counter-Current Temp (°C)"] = [f"{t:.1f}" for t in t_cnt]

    return pd.DataFrame(table_data)
