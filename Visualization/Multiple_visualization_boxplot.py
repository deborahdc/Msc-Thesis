#%% Developed by Deborah Dotta, July 2024
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D
from calendar import monthrange

# Load the forecast data
forecast_file_path = 'C:/Users/dottacor/Documents2/GitFiles/SEASHYPE_reforecast_data/Georgia/forecast.fcst'
obs_file_path = 'C:/Users/dottacor/Documents2/GitFiles/Georgia_obs/Q-Alazani-Shaqriani_monthly.obs'

# Read the forecast data
df = pd.read_csv(forecast_file_path, delim_whitespace=True, header=None)
df.columns = ['date', 'leadtime'] + [f'ensemble_{i}' for i in range(1, 26)]

# Convert date to datetime format
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

# Load the observed monthly data
obs_data = pd.read_csv(obs_file_path, delim_whitespace=True, header=None, names=['date', 'discharge'])
obs_data['date'] = pd.to_datetime(obs_data['date'], format='%Y%m%d')
obs_data.set_index('date', inplace=True)

# Remove invalid discharge values
obs_data = obs_data[obs_data['discharge'] >= 0]

# Calculate volume (m³) from discharge (m³/s)
def calculate_volume(row):
    days_in_month = monthrange(row.name.year, row.name.month)[1]
    seconds_in_month = days_in_month * 24 * 60 * 60
    return row['discharge'] * seconds_in_month

obs_data['volume'] = obs_data.apply(calculate_volume, axis=1)

# Aggregate observed data to monthly sums
obs_monthly_sum = obs_data['volume'].resample('M').sum()

# Function to format y-axis labels in millions
def millions(x, pos):
    return '%1.0fM' % (x * 1e-6)

formatter = FuncFormatter(millions)

# Create a figure with 12 subplots (one for each starting month in 2000)
year = 2013
fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(24, 18))
axes = axes.flatten()

# Custom properties for the boxplot
boxprops = dict(facecolor='#66b3ff', color='#0059b3', linewidth=0.7)
medianprops = dict(color='#0059b3', linewidth=0.7)
whiskerprops = dict(color='#0059b3', linewidth=0.7)
capprops = dict(color='#0059b3', linewidth=0.7)
flierprops = dict(markerfacecolor='#0059b3', marker='o', markersize=5, alpha=0.5)

# Generate boxplots for each starting month in 2000
for i in range(12):
    forecast_start_date = pd.to_datetime(f'{year}0101', format='%Y%m%d') + pd.DateOffset(months=i)
    filtered_df = df[(df['date'] == forecast_start_date) & (df['leadtime'] <= 7)]
    
    data_to_plot = []
    for leadtime in range(1, 8):
        data_for_leadtime = filtered_df[filtered_df['leadtime'] == leadtime].iloc[:, 2:].values.flatten()
        days_in_month = monthrange(year, forecast_start_date.month)[1]
        data_to_plot.append(data_for_leadtime * (days_in_month * 24 * 60 * 60))  # Convert to volume
    
    months_labels = [(forecast_start_date + pd.DateOffset(months=j)).strftime('%b %Y') for j in range(7)]
    
    bplot = axes[i].boxplot(data_to_plot, labels=months_labels, patch_artist=True, showmeans=True, meanline=True,
                            boxprops=boxprops, medianprops=medianprops, whiskerprops=whiskerprops, capprops=capprops,
                            flierprops=flierprops, showfliers=False)
    
    # Plot observed monthly sums
    obs_values_sum = []
    for j in range(7):
        current_month = forecast_start_date + pd.DateOffset(months=j)
        if current_month.strftime('%Y-%m') in obs_monthly_sum.index.strftime('%Y-%m'):
            obs_values_sum.append(obs_monthly_sum.loc[current_month.strftime('%Y-%m')])
        else:
            obs_values_sum.append(None)
    
    # Plot observed data in the middle of each month
    obs_positions = [j + 1 for j in range(7)]
    
    axes[i].plot(obs_positions, obs_values_sum, color='grey', linestyle='-', marker='o', label='Observed Sum')
    
    axes[i].set_title(f'{forecast_start_date.strftime("%B %Y")}')
    axes[i].set_ylabel('Volume (m³)')
    axes[i].yaxis.set_major_formatter(formatter)
    axes[i].grid(True, which='both', axis='y', linestyle='--', linewidth=0.7)
    axes[i].grid(False, which='both', axis='x')

# Creating a custom legend
legend_elements = [
    Line2D([0], [0], color='#66b3ff', marker='o', lw=1, label='Reforecast SEASHYPE', markersize=4),
    Line2D([0], [0], marker='o', color='w', label='Observed', markerfacecolor='grey', markersize=4)
]

fig.legend(handles=legend_elements, loc='upper center', ncol=2, fontsize='large')

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()

#%%