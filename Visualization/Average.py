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

# Filter data to include only the years from 1901 to 2020
df_obs = df_obs[(df_obs['Date'].dt.year >= 2003) & (df_obs['Date'].dt.year <= 2003)]

# Extract month from Date
df_obs['Month'] = df_obs['Date'].dt.month

# Group by Month and calculate the mean value
monthly_avg = df_obs.groupby('Month')['Value'].mean().reset_index()

# Map month numbers to month names
month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
monthly_avg['Month_Name'] = monthly_avg['Month'].map(month_names)

# Thresholds for April to September
thresholds = {
    'Apr': 1000,
    'May': 1400,
    'Jun': 1300,
    'Jul': 1200,
    'Aug': 1100,
    'Sep': 1000
}

# Create a heatmap-like plot for the monthly averages
plt.figure(figsize=(12, 6))
cmap = plt.get_cmap("viridis_r")  # Use the inverted Viridis palette
norm = plt.Normalize(monthly_avg['Value'].min(), monthly_avg['Value'].max())

colors = cmap(norm(monthly_avg['Value']))

bars = plt.bar(monthly_avg['Month_Name'], monthly_avg['Value'], color=colors, edgecolor='black')

# Add thresholds and red spans below them for the April to September period
for bar in bars:
    month = monthly_avg['Month_Name'][int(bar.get_x() + bar.get_width() / 2)]
    if month in thresholds:
        plt.plot([bar.get_x(), bar.get_x() + bar.get_width()], [thresholds[month], thresholds[month]], color='black', linestyle='--', linewidth=1)
        plt.text(bar.get_x() + bar.get_width() / 2, thresholds[month], f'{thresholds[month]}',
                 ha='center', va='bottom', color='black', fontsize=10)
        plt.fill_between([bar.get_x(), bar.get_x() + bar.get_width()], 0, thresholds[month], color='red', alpha=0.2)

# Add average values on top of each bar
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{int(yval)}', ha='center', va='bottom', fontsize=10)

# Add labels
plt.xlabel('Month', fontsize=14)
plt.ylabel('Average Discharge (m³/s)', fontsize=14)

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
output_file_avg = os.path.join(output_dir, "monthly_average_values_bars_with_thresholds_viridis_inverted.png")
plt.savefig(output_file_avg, bbox_inches='tight')

# Show the plot
plt.show()



#%%

#%%
import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.dates import DateFormatter, DayLocator
import numpy as np

# Define file paths
obs_file_path = r"C:\Users\dottacor\evs-SEASHYPE\obs\9503451_Q_SEASHYPE2.obs"
output_dir = r"C:\Users\dottacor\Documents2\GitFiles\Visualization_plots\Netherlands"

# Read the observational data into a pandas DataFrame
df_obs = pd.read_csv(obs_file_path, delim_whitespace=True, header=None)
df_obs.columns = ['Date', 'Value']

# Convert Date column to datetime
df_obs['Date'] = pd.to_datetime(df_obs['Date'], format='%Y%m%d')

# Thresholds for April to September
thresholds = {
    'April': 1000,
    'May': 1400,
    'June': 1300,
    'July': 1200,
    'August': 1100,
    'September': 1000
}

# Function to filter data for a specific year and months from April to September
def filter_data_for_month(df, year, month):
    start_date = f'{year}-{month:02d}-01'
    end_date = f'{year}-{month:02d}-{pd.Period(start_date).days_in_month}'
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    return df.loc[mask]

# Function to plot observational data
def plot_observational_data(ax, df, month_name, year, month, threshold):
    # Plot the observational data with color coding based on the threshold
    ax.plot(df['Date'], df['Value'], color='black', linewidth=2)
    
    # Add threshold line
    ax.axhline(threshold, color='red', linestyle='--', linewidth=1)
    ax.text(df['Date'].iloc[0], threshold + 10, f'{threshold}', color='red', fontsize=10, va='bottom', ha='left')

    # Add labels and title
    ax.set_xlabel('Day', fontsize=12)
    ax.set_ylabel('Q (m³/s)', fontsize=12)
    ax.set_title(f'{month_name}', fontsize=14)

    # Set custom x-axis ticks
    days_in_month = pd.Period(f'{year}-{month:02d}').days_in_month
    ticks = [1, 5, 10, 15, 20, 25, days_in_month]
    tick_labels = [f'{tick:02d}' for tick in ticks]
    
    ax.set_xticks(pd.to_datetime([f'{year}-{month:02d}-{day:02d}' for day in ticks]))
    ax.set_xticklabels(tick_labels)

    # Rotate x-axis labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    # Customize plot to remove the box around the data and keep only x and y axes
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)

# User input for the year
selected_year = 2003  # Change this to the desired year
months = ['April', 'May', 'June', 'July', 'August', 'September']

# Plot observational data for each month
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(18, 12))
plt.subplots_adjust(hspace=0.5, wspace=0.3)
axes = axes.flatten()

for i, month in enumerate(months):
    df_filtered = filter_data_for_month(df_obs, selected_year, i + 4)
    plot_observational_data(axes[i], df_filtered, month, selected_year, i + 4, thresholds[month])

# Add a legend for the red dashed line
lines = [plt.Line2D([0], [0], color='red', linestyle='--', linewidth=2)]
labels = ['Drought alert ≤ thresholds']
fig.legend(lines, labels, loc='upper right', fontsize=12)

# Save the observational data plot
output_file_obs = os.path.join(output_dir, f"observational_data_{selected_year}_April_to_September_with_thresholds.png")
plt.savefig(output_file_obs, bbox_inches='tight')

# Show the observational data plot (optional)
plt.show()
#%%

#%%

#%%


#%%

#%%

