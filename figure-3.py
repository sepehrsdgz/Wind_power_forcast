import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import weibull_min
from scipy.special import gamma

"""this file makes the Weibull distributions of the selected locations. 
The Weibull parameters (k and c) are determined using mean wind speed-standard deviation method """

def calculate_weibull_parameters(data_series):
    """
    Calculates k and c using the Mean/StdDev method
    mentioned in Section 5.1 of the paper.
    """
    mean = data_series.mean()
    std = data_series.std()

    # Approximate formula for k (standard in wind energy)
    k = (std / mean) ** (-1.086)

    # Formula for c
    c = mean / gamma(1 + 1 / k)

    return k, c


# ==========================================
# 1. LOAD DATA
# ==========================================
df_chicago = pd.read_csv("prepared_chicago.csv")
df_detroit = pd.read_csv("prepared_detroit.csv")

# ==========================================
# 2. CALCULATE PARAMETERS & PDF
# ==========================================
# We use the Mean_WindSpeed column (Daily means)
k_chi, c_chi = calculate_weibull_parameters(df_chicago['Mean_WindSpeed'])
k_det, c_det = calculate_weibull_parameters(df_detroit['Mean_WindSpeed'])

print(f"Chicago: k={k_chi:.2f}, c={c_chi:.2f}")
print(f"Detroit: k={k_det:.2f}, c={c_det:.2f}")

# Define X-axis for wind speeds (0 to 20 m/s)
x = np.linspace(0, 20, 100)

# Calculate Probability Density Functions (PDF)
pdf_chi = (k_chi / c_chi) * (x / c_chi) ** (k_chi - 1) * np.exp(-(x / c_chi) ** k_chi)
pdf_det = (k_det / c_det) * (x / c_det) ** (k_det - 1) * np.exp(-(x / c_det) ** k_det)

# ==========================================
# 3. PLOTTING (Replicating Fig. 5)
# ==========================================
plt.figure(figsize=(9, 6))

# Plot Chicago (with markers every few steps to match paper style)
plt.plot(x, pdf_chi, label='Chicago', color='red', marker='o',
         markevery=5, markersize=5, markerfacecolor='white')

# Plot Detroit (with different markers)
plt.plot(x, pdf_det, label='Detroit', color='green', marker='^',
         markevery=5, markersize=5, markerfacecolor='white')

# Formatting to match the paper
plt.title('Figure 5: Wind speed frequency distributions (Replicated)', fontsize=12)
plt.xlabel('Wind speed [m/s]', fontsize=11, fontweight='bold')
plt.ylabel('Probability density distribution', fontsize=11, fontweight='bold')

plt.xlim(0, 20)
plt.ylim(0, 0.5)  # Adjust based on your peak height
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

# Save the plot
plt.savefig("Figure5_FrequencyDistribution.png", dpi=300)
plt.show()