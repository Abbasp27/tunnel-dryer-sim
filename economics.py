# economics.py

def calculate_operating_cost(thermal_kw, electrical_kw, lpg_rate, elec_rate):
    """
    Calculates the hourly operating cost of the dryer.
    LPG Energy Content: ~13.6 kWh per kg of gas.
    """
    # 1. LPG Cost Calculation
    lpg_kg_per_hr = thermal_kw / 13.6
    hourly_lpg_cost = lpg_kg_per_hr * lpg_rate
    
    # 2. Electricity Cost Calculation
    hourly_elec_cost = electrical_kw * elec_rate
    
    # 3. Totals
    total_hourly_cost = hourly_lpg_cost + hourly_elec_cost
    
    # 4. Cost per kg of wet feed processed
    # We will do this math dynamically in the main app!
    
    return {
        "lpg_kg_hr": lpg_kg_per_hr,
        "lpg_cost_hr": hourly_lpg_cost,
        "elec_cost_hr": hourly_elec_cost,
        "total_cost_hr": total_hourly_cost
    }