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

#%% Define function to plot percentiles
def plot_percentiles(start_date, ax):
    start_leadtime = 24
    num_days = 91  # Number of days to display
    tick_interval_days = 15  # Interval for x-axis ticks in days

    # Filter data to include only the specified start date and lead time
    df_start = df[(df['Date'] == start_date) & (df['Leadtime'] == start_leadtime)]

    if df_start.empty:
        raise ValueError("No data found for the specified start date and lead time")

    # Get the index of the starting point
    start_index = df_start.index[0]

    # Calculate the end index based on the number of days to display (each day corresponds to 24 hours lead time)
    end_index = start_index + num_days

    # Filter data for the specified range
    df_filtered = df.iloc[start_index:end_index]

    # Ensure only the required columns (Date, Leadtime, and Member_1 to Member_25) are used
    df_filtered = df_filtered[['Date', 'Leadtime'] + [f'Member_{i}' for i in range(1, 26)]]

    # Calculate percentiles and mean for each row (without grouping by Date)
    percentile_10 = df_filtered.apply(lambda x: np.percentile(x[2:], 10), axis=1)
    percentile_30 = df_filtered.apply(lambda x: np.percentile(x[2:], 30), axis=1)
    percentile_70 = df_filtered.apply(lambda x: np.percentile(x[2:], 70), axis=1)
    percentile_90 = df_filtered.apply(lambda x: np.percentile(x[2:], 90), axis=1)
    mean = df_filtered.apply(lambda x: np.mean(x[2:]), axis=1)

    # Calculate the day range for the x-axis
    day_range = np.arange(0, len(df_filtered))

    # Plot Percentiles and Mean
    ax.fill_between(day_range, percentile_30, percentile_70, color='skyblue', alpha=0.6, label='30-70th Percentile')
    ax.fill_between(day_range, percentile_10, percentile_90, color='#66b3ff', alpha=0.3, label='10-90th Percentile')
    ax.plot(day_range, mean, color='#0059b3', label='Ensemble Mean', linewidth=2)

    # Add labels and title
    ax.set_xlabel('Time (days)', fontsize=12)
    ax.set_ylabel('Discharge (m³/s)', fontsize=12)
    ax.set_title(pd.to_datetime(start_date).strftime('%d %B %Y'), fontsize=10)

    # Customize plot to remove the box around the data and keep only x and y axes
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)

    # Set x-axis ticks to show every tick_interval_days days
    tick_positions = np.arange(0, len(day_range), tick_interval_days)
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(day_range[tick_positions], ha='right')

    # Add legend inside the plot
    if start_date == start_dates[0]:
        ax.legend(loc='upper right')

#%% Define function to plot single runs
def plot_single_runs(start_date, ax):
    start_leadtime = 24
    num_days = 91  # Number of days to display
    tick_interval_days = 15  # Interval for x-axis ticks in days

    # Filter data to include only the specified start date and lead time
    df_start = df[(df['Date'] == start_date) & (df['Leadtime'] == start_leadtime)]

    if df_start.empty:
        raise ValueError("No data found for the specified start date and lead time")

    # Get the index of the starting point
    start_index = df_start.index[0]

    # Calculate the end index based on the number of days to display (each day corresponds to 24 hours lead time)
    end_index = start_index + num_days

    # Filter data for the specified range
    df_filtered = df.iloc[start_index:end_index]

    # Ensure only the required columns (Date, Leadtime, and Member_1 to Member_25) are used
    df_filtered = df_filtered[['Date', 'Leadtime'] + [f'Member_{i}' for i in range(1, 26)]]

    # Calculate the day range for the x-axis
    day_range = np.arange(0, len(df_filtered))

    # Plot Single Runs with Colorful Lines
    colors = plt.cm.get_cmap('tab20', 25)
    for member in range(1, 26):
        ax.plot(day_range, df_filtered[f'Member_{member}'], color=colors(member-1), linewidth=1)

    # Add labels and title
    ax.set_xlabel('Time (days)', fontsize=12)
    ax.set_ylabel('Discharge (m³/s)', fontsize=12)
    ax.set_title(pd.to_datetime(start_date).strftime('%d %B %Y'), fontsize=10)

    # Customize plot to remove the box around the data and keep only x and y axes
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)

    # Set x-axis ticks to show every tick_interval_days days
    tick_positions = np.arange(0, len(day_range), tick_interval_days)
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(day_range[tick_positions], ha='right')

    # Add a single legend entry for all members inside the plot
    if start_date == start_dates[0]:
        ax.plot([], [], color='gray', label='25 Models')
        ax.legend(loc='upper right')

#%% Plot multiple graphs in two grids
output_dir = r"C:\Users\dottacor\Documents2\GitFiles\Visualization_plots\Netherlands"
start_dates = [f'2013-{month:02d}-01 00:00' for month in range(1, 13)]

# Plot percentiles
fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(18, 24))
plt.subplots_adjust(hspace=0.5, wspace=0.3)
axes = axes.flatten()

for i, start_date in enumerate(start_dates):
    plot_percentiles(start_date, axes[i])

# Save the large percentiles plot
output_file_percentiles = os.path.join(output_dir, "year_visualization_percentiles.png")
plt.savefig(output_file_percentiles, bbox_inches='tight')

# Show the large percentiles plot (optional)
plt.show()

# Plot single runs
fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(18, 24))
plt.subplots_adjust(hspace=0.5, wspace=0.3)
axes = axes.flatten()

for i, start_date in enumerate(start_dates):
    plot_single_runs(start_date, axes[i])

# Save the large single runs plot
output_file_single_runs = os.path.join(output_dir, "year_visualization_single_runs.png")
plt.savefig(output_file_single_runs, bbox_inches='tight')

# Show the large single runs plot (optional)
plt.show()



#%%