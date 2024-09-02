#%% Developed by Deborah Dotta, May 2024
import pandas as pd
import matplotlib.pyplot as plt
import os

# Define file paths
obs_file_path = r"C:\Users\dottacor\evs-SEASHYPE\obs\9503451_Q_SEASHYPE2.obs"
output_dir = r"C:\Users\dottacor\Documents2\GitFiles\Visualization_plots\Netherlands"

# Read the observational data into a pandas DataFrame
df_obs = pd.read_csv(obs_file_path, delim_whitespace=True, header=None)
df_obs.columns = ['Date', 'Value']

# Convert Date column to datetime
df_obs['Date'] = pd.to_datetime(df_obs['Date'], format='%Y%m%d')

# Filter data to include only the years 1901 to 2020
df_obs = df_obs[(df_obs['Date'].dt.year >= 1901) & (df_obs['Date'].dt.year <= 2020)]

# Extract year and month from Date
df_obs['Year'] = df_obs['Date'].dt.year
df_obs['Month'] = df_obs['Date'].dt.month

# Group by Year and Month and calculate the minimum value for each month of each year
monthly_min_each_year = df_obs.groupby(['Year', 'Month'])['Value'].min().reset_index()

# Group by Month and calculate the average of the minimum values for each month across the years
monthly_avg_min = monthly_min_each_year.groupby('Month')['Value'].mean().reset_index()

# Map month numbers to month names
month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
monthly_avg_min['Month_Name'] = monthly_avg_min['Month'].map(month_names)

# Thresholds for April to September
thresholds = {
    'Apr': 1000,
    'May': 1400,
    'Jun': 1300,
    'Jul': 1200,
    'Aug': 1100,
    'Sep': 1000
}

# Create a heatmap-like plot for the monthly average minimum values
plt.figure(figsize=(12, 6))

# Use the original Viridis palette with transparency
cmap = plt.get_cmap("viridis")
norm = plt.Normalize(monthly_avg_min['Value'].min(), monthly_avg_min['Value'].max())

colors = cmap(norm(monthly_avg_min['Value']))

# Set the transparency (alpha) to make the colors lighter
bars = plt.bar(monthly_avg_min['Month_Name'], monthly_avg_min['Value'], color='white', edgecolor='black')

# Add thresholds and red spans below them for the April to September period
for bar in bars:
    month = monthly_avg_min['Month_Name'][int(bar.get_x() + bar.get_width() / 2)]
    yval = bar.get_height()
    threshold = thresholds.get(month, None)
    
    # Set a default value_offset
    value_offset = 20
    
    if threshold is not None:
        threshold_offset = 30  # Default offset for the threshold label

        # Adjust offsets to prevent overlap
        if abs(yval - threshold) < 50:
            threshold_offset = 40
            value_offset = 200
        elif abs(yval - threshold) < 100:
            threshold_offset = 50
            value_offset = 80

        plt.plot([bar.get_x(), bar.get_x() + bar.get_width()], [threshold, threshold], color='black', linestyle='--', linewidth=1)
        plt.text(bar.get_x() + bar.get_width() / 2, threshold + threshold_offset, f'{threshold}', ha='center', va='bottom', color='black', fontsize=10)
        plt.fill_between([bar.get_x(), bar.get_x() + bar.get_width()], 0, threshold, color='red', alpha=0.2)

        # Place the value below the bar if it is smaller
        if yval < threshold:
            plt.text(bar.get_x() + bar.get_width() / 2, yval - value_offset, f'{int(yval)}', ha='center', va='top', fontsize=10)
        else:
            plt.text(bar.get_x() + bar.get_width() / 2, yval + value_offset, f'{int(yval)}', ha='center', va='bottom', fontsize=10)
    else:
        plt.text(bar.get_x() + bar.get_width() / 2, yval + value_offset, f'{int(yval)}', ha='center', va='bottom', fontsize=10)

# Add labels
plt.xlabel('Month', fontsize=14)
plt.ylabel('Average Minimum Discharge (m³/s)', fontsize=14)
# Add legend
plt.legend(['Drought alert ≤ thresholds'], loc='upper right', fontsize=12)

# Customize plot to remove the box around the data and keep only x and y axes
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['left'].set_linewidth(1)
plt.gca().spines['bottom'].set_linewidth(1)

# Set y-axis limit
plt.ylim(0, 5000)

# Save the plot
output_file_avg_min = os.path.join(output_dir, "monthly_avg_minimum_values_bars_with_thresholds_viridis_lighter_alpha.png")
plt.savefig(output_file_avg_min, bbox_inches='tight')

# Show the plot
plt.show()


#%%