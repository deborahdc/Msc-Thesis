#%% Developed by Deborah Dotta, July 2024
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to calculate CDF
def calculate_cdf(data):
    sorted_data = np.sort(data)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    return sorted_data, cdf

# Function to filter data for specific months and years
def filter_data_for_months_and_years(data, years, months):
    return data[(data['date'].dt.year.isin(years)) & (data['date'].dt.month.isin(months))]

# Paths
obs_file = r'C:\Users\dottacor\Documents2\GitFiles\Georgia_obs\Q-Alazani-Shaqriani.obs'
reanalysis_file = r'C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia_historical\output\discharge_data_1991_2018.txt'

# Load data
observed_data = pd.read_csv(obs_file, delim_whitespace=True, header=None, names=["date", "flow"])
reanalysis_data = pd.read_csv(reanalysis_file, delim_whitespace=True, header=None, names=["date", "flow"])

# Convert date columns to datetime
observed_data['date'] = pd.to_datetime(observed_data['date'], format='%Y%m%d%H')
reanalysis_data['date'] = pd.to_datetime(reanalysis_data['date'], format='%Y%m%d')

# Define years and months of interest
years_of_interest = [1991, 2018]
summer_months = [6, 7, 8]  # June, July, August

# Filter data for summer months
obs_data_summer = filter_data_for_months_and_years(observed_data, years_of_interest, summer_months)
rean_data_summer = filter_data_for_months_and_years(reanalysis_data, years_of_interest, summer_months)

# Calculate CDFs
obs_sorted, obs_cdf = calculate_cdf(obs_data_summer['flow'])
rean_sorted, rean_cdf = calculate_cdf(rean_data_summer['flow'])

# Calculate percentiles
obs_10th = np.percentile(obs_data_summer['flow'], 10)
obs_20th = np.percentile(obs_data_summer['flow'], 20)
obs_33rd = np.percentile(obs_data_summer['flow'], 33)
rean_10th = np.percentile(rean_data_summer['flow'], 10)
rean_20th = np.percentile(rean_data_summer['flow'], 20)
rean_33rd = np.percentile(rean_data_summer['flow'], 33)

# Plotting CDFs for summer months
plt.figure(figsize=(10, 6))
plt.plot(obs_sorted, obs_cdf, 'o-', color='gray', label='Observed', markersize=4)  # Decreased marker size
plt.plot(rean_sorted, rean_cdf, 's-', color='black', label='Reanalysis EFAS', markersize=3)  # Decreased marker size
#plt.axvline(x=obs_10th, color='red', linestyle='--', label='Observed 10th percentile')
#plt.axvline(x=obs_20th, color='blue', linestyle='--', label='Observed 20th percentile')
#plt.axvline(x=obs_33rd, color='orange', linestyle='--', label='Observed 33rd percentile')
#plt.axvline(x=rean_10th, color='purple', linestyle='--', label='Reanalysis 10th percentile')
#plt.axvline(x=rean_20th, color='yellow', linestyle='--', label='Reanalysis 20th percentile')
#plt.axvline(x=rean_33rd, color='brown', linestyle='--', label='Reanalysis 33rd percentile')
plt.xlabel('Discharge (m³/s)')
plt.ylabel('CDF')
plt.title('June, July, August')
plt.legend()
plt.show()

# Print percentile values
print(f'Observed 10th percentile: {obs_10th} m³/s')
print(f'Observed 20th percentile: {obs_20th} m³/s')
print(f'Observed 33rd percentile: {obs_33rd} m³/s')
print(f'Reanalysis 10th percentile: {rean_10th} m³/s')
print(f'Reanalysis 20th percentile: {rean_20th} m³/s')
print(f'Reanalysis 33rd percentile: {rean_33rd} m³/s')


#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to calculate CDF
def calculate_cdf(data):
    sorted_data = np.sort(data)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    return sorted_data, cdf

# Function to filter data for specific months and years
def filter_data_for_months_and_years(data, years, months):
    return data[(data['date'].dt.year.isin(years)) & (data['date'].dt.month.isin(months))]

# Paths
obs_file = r'C:\Users\dottacor\Documents2\GitFiles\Georgia_obs\Q-Alazani-Shaqriani.obs'
reanalysis_file = r'C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia_historical\output\discharge_data_1991_2018.txt'

# Load data
observed_data = pd.read_csv(obs_file, delim_whitespace=True, header=None, names=["date", "flow"])
reanalysis_data = pd.read_csv(reanalysis_file, delim_whitespace=True, header=None, names=["date", "flow"])

# Convert date columns to datetime
observed_data['date'] = pd.to_datetime(observed_data['date'], format='%Y%m%d%H')
reanalysis_data['date'] = pd.to_datetime(reanalysis_data['date'], format='%Y%m%d')

# Define years and months of interest
years_of_interest = [1991, 2018]
summer_months = [6, 7, 8]  # June, July, August

# Filter data for summer months
obs_data_summer = filter_data_for_months_and_years(observed_data, years_of_interest, summer_months)
rean_data_summer = filter_data_for_months_and_years(reanalysis_data, years_of_interest, summer_months)

# Calculate monthly volumes
obs_data_summer['month_year'] = obs_data_summer['date'].dt.to_period('M')
rean_data_summer['month_year'] = rean_data_summer['date'].dt.to_period('M')

obs_monthly_volume = obs_data_summer.groupby('month_year')['flow'].sum()
rean_monthly_volume = rean_data_summer.groupby('month_year')['flow'].sum()

# Calculate CDFs
obs_sorted, obs_cdf = calculate_cdf(obs_monthly_volume)
rean_sorted, rean_cdf = calculate_cdf(rean_monthly_volume)

# Calculate 10th, 20th, and 33rd percentiles
obs_10th = np.percentile(obs_monthly_volume, 10)
obs_20th = np.percentile(obs_monthly_volume, 20)
obs_33rd = np.percentile(obs_monthly_volume, 33)
rean_10th = np.percentile(rean_monthly_volume, 10)
rean_20th = np.percentile(rean_monthly_volume, 20)
rean_33rd = np.percentile(rean_monthly_volume, 33)

# Plotting CDFs for summer months
plt.figure(figsize=(10, 6))
plt.plot(obs_sorted, obs_cdf, 'o-', color='green', label='Observed volume - Shaqriani', markersize=4)
plt.plot(rean_sorted, rean_cdf, 's-', color='blue', label='EFAS Historical Reanalysis', markersize=4)
plt.xlabel('Monthly Volume (m³)')
plt.ylabel('CDF')
plt.title('CDF for Monthly Volumes in June, July, August')
plt.legend()
plt.show()

# Print percentile values
print(f'Observed 10th percentile: {obs_10th} m³')
print(f'Observed 20th percentile: {obs_20th} m³')
print(f'Observed 33rd percentile: {obs_33rd} m³')
print(f'Reanalysis 10th percentile: {rean_10th} m³')
print(f'Reanalysis 20th percentile: {rean_20th} m³')
print(f'Reanalysis 33rd percentile: {rean_33rd} m³')


#%%