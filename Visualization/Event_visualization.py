#%% Developed by Deborah Dotta, May 2024
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import pickle

# Define file paths
data_file_path = r"C:\Users\dottacor\Documents2\GitFiles\SEASHYPE_reforecast_data\TheNetherlands\whole_period_joined.fcst"
pickle_file_path = r"C:\Users\dottacor\Documents2\GitFiles\SEASHYPE_reforecast_data\TheNetherlands\processed_data.pkl"

#%% Read and process data if pickle file doesn't exist
if not os.path.exists(pickle_file_path):
    # Read the data into a pandas DataFrame
    df = pd.read_csv(data_file_path, delim_whitespace=True, header=None)
    df.columns = ['Date', 'Leadtime'] + [f'Member_{i}' for i in range(1, 26)]

    # Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d%H%M')

    # Save the processed DataFrame to a pickle file
    with open(pickle_file_path, 'wb') as f:
        pickle.dump(df, f)

else:
    # Load the processed DataFrame from the pickle file
    with open(pickle_file_path, 'rb') as f:
        df = pickle.load(f)

#%% Specify start date, leadtime, number of days to display, and tick interval
start_date = '2013-04-01 00:00'
start_leadtime = 24
num_days = 211  # Number of days to display
tick_interval_days = 30  # Interval for x-axis ticks in days

# Filter data to include only the specified start date and lead time
df_start = df[(df['Date'] == start_date) & (df['Leadtime'] == start_leadtime)]

if df_start.empty:
    raise ValueError("No data found for the specified start date and lead time")

# Debug: Print start index details
print("Start Date and Leadtime:", df_start)

# Get the index of the starting point
start_index = df_start.index[0]

# Calculate the end index based on the number of days to display (each day corresponds to 24 hours lead time)
end_index = start_index + num_days

# Filter data for the specified range
df_filtered = df.iloc[start_index:end_index]

# Debug: Print filtered data
print("Filtered Data:\n", df_filtered.head(20))

# Ensure only the required columns (Date, Leadtime, and Member_1 to Member_25) are used
df_filtered = df_filtered[['Date', 'Leadtime'] + [f'Member_{i}' for i in range(1, 26)]]

# Calculate percentiles and mean for each row (without grouping by Date)
percentile_10 = df_filtered.apply(lambda x: np.percentile(x[2:], 10), axis=1)
percentile_30 = df_filtered.apply(lambda x: np.percentile(x[2:], 30), axis=1)
percentile_70 = df_filtered.apply(lambda x: np.percentile(x[2:], 70), axis=1)
percentile_90 = df_filtered.apply(lambda x: np.percentile(x[2:], 90), axis=1)
mean = df_filtered.apply(lambda x: np.mean(x[2:]), axis=1)

# Debug: Print calculated percentiles and mean
print("Percentile 10:\n", percentile_10.head())
print("Percentile 30:\n", percentile_30.head())
print("Percentile 70:\n", percentile_70.head())
print("Percentile 90:\n", percentile_90.head())
print("Mean:\n", mean.head())

# Calculate the day range for the x-axis
day_range = np.arange(0, len(df_filtered))

#%% Plot Percentiles and Mean
plt.figure(figsize=(12, 6))

# Set the font to Calibri
plt.rcParams["font.family"] = "Calibri"

# Plot the percentiles
plt.fill_between(day_range, percentile_30, percentile_70, color='skyblue', alpha=0.6, label='30-70th Percentile')
plt.fill_between(day_range, percentile_10, percentile_90, color='#66b3ff', alpha=0.3, label='10-90th Percentile')
plt.plot(day_range, mean, color='#0059b3', label='Ensemble Mean', linewidth=2)

# Add labels and title
plt.xlabel('Time (days)', fontsize=12)
plt.ylabel('Discharge (m³/s)', fontsize=12)
plt.title(pd.to_datetime(start_date).strftime('%d %B %Y'), fontsize=10)

# Customize plot to remove the box around the data and keep only x and y axes
ax = plt.gca()
ax.spines['left'].set_linewidth(1)
ax.spines['bottom'].set_linewidth(1)

# Set x-axis ticks to show every tick_interval_days days
tick_positions = np.arange(0, len(day_range), tick_interval_days)
ax.set_xticks(tick_positions)
ax.set_xticklabels(day_range[tick_positions], ha='right')

# Add legend inside the plot
plt.legend(loc='upper right')

# Remove the grid
plt.grid(False)

# Save the plot
output_dir = r"C:\Users\dottacor\Documents2\GitFiles\Visualization_plots\Netherlands"
output_file = os.path.join(output_dir, "percentiles_visualization.png")
plt.savefig(output_file, bbox_inches='tight')

# Show the plot (optional)
plt.show()

#%% Plot Single Runs with Colorful Lines
plt.figure(figsize=(12, 6))

# Set the font to Calibri
plt.rcParams["font.family"] = "Calibri"

# Define a list of colors for the single runs
colors = plt.cm.get_cmap('tab20', 25)

for member in range(1, 26):
    plt.plot(day_range, df_filtered[f'Member_{member}'], color=colors(member-1), linewidth=1)

# Add labels and title
plt.xlabel('Time (days)', fontsize=12)
plt.ylabel('Discharge (m³/s)', fontsize=12)
plt.title(pd.to_datetime(start_date).strftime('%d %B %Y'), fontsize=10)

# Customize plot to remove the box around the data and keep only x and y axes
ax = plt.gca()
ax.spines['left'].set_linewidth(1)
ax.spines['bottom'].set_linewidth(1)

# Set x-axis ticks to show every tick_interval_days days
tick_positions = np.arange(0, len(day_range), tick_interval_days)
ax.set_xticks(tick_positions)
ax.set_xticklabels(day_range[tick_positions], ha='right')

# Add a single legend entry for all members inside the plot
plt.plot([], [], color='gray', label='25 Models')
plt.legend(loc='upper right')

# Remove the grid
plt.grid(False)

# Save the plot
output_dir = r"C:\Users\dottacor\Documents2\GitFiles\Visualization_plots\Netherlands"
output_file = os.path.join(output_dir, "single_runs_visualization.png")
plt.savefig(output_file, bbox_inches='tight')

# Show the plot (optional)
plt.show()

# %%
