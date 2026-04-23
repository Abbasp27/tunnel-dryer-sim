# materials.py
MATERIAL_DB = {
    "Dehydrated Tomatoes": {
        "init_m": 94.0, "final_m": 5.0, "density": 15, "max_temp": 200.0, "ideal_temp": 65.0, "ideal_vel": 2.5, "ideal_time": 7.0, "ideal_belt_speed": 0.05,
        "ideal_flow": "Co-Current",
        "flow_reason": "High sugar content. Co-current prevents scorching the dry product at the exit."
    },
    "Extruded Pasta": {
        "init_m": 30.0, "final_m": 12.0, "density": 30, "max_temp": 200.0, "ideal_temp": 85.0, "ideal_vel": 1.8, "ideal_time": 4.0, "ideal_belt_speed": 0.08,
        "ideal_flow": "Co-Current",
        "flow_reason": "Prevents case-hardening (crust formation) which traps internal moisture."
    },
    "Roasted Almonds": {
        "init_m": 15.0, "final_m": 5.0, "density": 35, "max_temp": 200.0, "ideal_temp": 145.0, "ideal_vel": 3.0, "ideal_time": 1.0, "ideal_belt_speed": 0.25,
        "ideal_flow": "Counter-Current",
        "flow_reason": "Robust material. Counter-current ensures maximum heat transfer for roasting."
    },
    "Pet Food Kibble": {
        "init_m": 22.0, "final_m": 8.0, "density": 40, "max_temp": 200.0, "ideal_temp": 115.0, "ideal_vel": 4.0, "ideal_time": 0.8, "ideal_belt_speed": 0.35,
        "ideal_flow": "Counter-Current",
        "flow_reason": "Dense pellet structure requires aggressive high heat at the discharge end."
    },
    "Tea Leaves / Herbs": {
        "init_m": 70.0, "final_m": 8.0, "density": 5, "max_temp": 200.0, "ideal_temp": 50.0, "ideal_vel": 0.8, "ideal_time": 3.0, "ideal_belt_speed": 0.12,
        "ideal_flow": "Co-Current",
        "flow_reason": "Highly volatile organic compounds. Co-current preserves flavor and color."
    },
    "Pharmaceutical Granules": {
        "init_m": 20.0, "final_m": 2.0, "density": 10, "max_temp": 200.0, "ideal_temp": 55.0, "ideal_vel": 1.0, "ideal_time": 4.5, "ideal_belt_speed": 0.06,
        "ideal_flow": "Co-Current",
        "flow_reason": "Thermolabile active ingredients. Requires gentle cooling gradient."
    },
    "Biomass (Wood Chips)": {
        "init_m": 50.0, "final_m": 10.0, "density": 45, "max_temp": 200.0, "ideal_temp": 120.0, "ideal_vel": 3.5, "ideal_time": 2.0, "ideal_belt_speed": 0.15,
        "ideal_flow": "Counter-Current",
        "flow_reason": "Extremely robust. Counter-current maximizes energy efficiency."
    },
    "Sliced Apples": {
        "init_m": 85.0, "final_m": 15.0, "density": 20, "max_temp": 200.0, "ideal_temp": 70.0, "ideal_vel": 2.2, "ideal_time": 5.0, "ideal_belt_speed": 0.07,
        "ideal_flow": "Co-Current",
        "flow_reason": "Prevents browning (Maillard reaction) and caramelization of fructose."
    },
    "Corn (Maize)": {
        "init_m": 25.0, "final_m": 13.0, "density": 40, "max_temp": 200.0, "ideal_temp": 90.0, "ideal_vel": 2.5, "ideal_time": 3.0, "ideal_belt_speed": 0.12,
        "ideal_flow": "Counter-Current",
        "flow_reason": "Thick pericarp (outer skin) requires high heat difference to drive out core moisture."
    }
}
