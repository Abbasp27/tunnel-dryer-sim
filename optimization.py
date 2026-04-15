# optimization.py
import numpy as np

def find_optimal_settings(feed_rate, init_m, final_m, loading_density, lpg_rate, elec_rate):
    # Test 50 velocities and 50 times (2,500 combinations)
    v_range = np.linspace(0.5, 5.0, 50)
    t_range = np.linspace(1.0, 10.0, 50)
    
    costs_z = np.zeros((50, 50))
    
    best_cost = float('inf')
    best_v = 0
    best_t = 0

    for i, v in enumerate(v_range):
        for j, t in enumerate(t_range):
            # Engineering Logic
            moisture_removed = feed_rate * ((init_m - final_m) / (1 - final_m))
            thermal_kw = ((moisture_removed * 2260) + (feed_rate * 2 * 30) + ((moisture_removed/0.022)*1.006*50)) * 1.15 / 3600
            fan_kw = 1.2 * (v**3) * 1.5 
            
            # Financial Logic
            hourly_cost = (thermal_kw / 13.6 * lpg_rate) + (fan_kw * elec_rate)
            costs_z[j][i] = hourly_cost
            
            if hourly_cost < best_cost:
                best_cost = hourly_cost
                best_v = v
                best_t = t
                
    return best_v, best_t, best_cost, (v_range, t_range, costs_z)