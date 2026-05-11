import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""
in here the code will plot a table of "Power curve for a 1 MW wind turbine."
but in the formula that driven using the lecture notes
"""



# 1. The Formula
def calculate_power(wind_speed):
    v_ci = 3.0;
    v_r = 15.0;
    v_co = 25.0;
    P_r = 1000.0

    if wind_speed < v_ci or wind_speed > v_co:
        return 0.0
    elif wind_speed >= v_r:
        return P_r
    else:
        numerator = (wind_speed ** 3) - (v_ci ** 3)
        denominator = (v_r ** 3) - (v_ci ** 3)
        return P_r * (numerator / denominator)


# 2. Generate Data (Up to 30.5)
speeds = np.arange(0, 31.0, 0.5)
powers = [calculate_power(v) for v in speeds]

df_curve = pd.DataFrame({
    'Wind Speed (m/s)': speeds,
    'Power Output (kW)': powers
})

# 3. Plotting
plt.figure(figsize=(10, 6))
plt.plot(df_curve['Wind Speed (m/s)'], df_curve['Power Output (kW)'],
         color='red', marker='s', markersize=4, linestyle='-', linewidth=1.5)

# Formatting
plt.title('Figure 1: Synthesized Power Curve for 1 MW Turbine', fontsize=14)
plt.xlabel('Wind Speed [m/s]', fontsize=12, fontweight='bold')
plt.ylabel('Power [kW]', fontsize=12, fontweight='bold')
plt.grid(True, which='both', linestyle='--', alpha=0.7)

# --- CHANGED HERE: Zoom out to see up to 32 m/s ---
plt.xlim(0, 32)
plt.ylim(0, 1100)

# Annotations
plt.text(3, 50, 'Cut-in (3 m/s)', verticalalignment='bottom')
plt.text(15, 1020, 'Rated (15 m/s)', horizontalalignment='center')
plt.text(25.5, 50, 'Cut-out (25 m/s)', horizontalalignment='left')

# 4. SAVE THE PLOT
filename = "Figure1_PowerCurve.png"
plt.savefig(filename, dpi=300, bbox_inches='tight')

print(f"Plot saved successfully as: {filename}")

plt.show()