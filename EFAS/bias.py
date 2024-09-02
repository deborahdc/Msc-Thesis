#%% Developed by Deborah Dotta, July 2024

# reading data
import pandas as pd
import numpy as np
import os

# Function to calculate CDF
def calculate_cdf(data):
    sorted_data = np.sort(data)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    return sorted_data, cdf

# Function for quantile mapping
def quantile_mapping(reforecast_values, rean_sorted, rean_cdf, obs_sorted, obs_cdf):
    reforecast_cdf = np.interp(reforecast_values, rean_sorted, rean_cdf, left=0, right=1)
    corrected_values = np.interp(reforecast_cdf, obs_cdf, obs_sorted, left=obs_sorted[0], right=obs_sorted[-1])
    return corrected_values

# Define a function to perform bias correction for each month using quantile mapping
def bias_correction_qm(reforecast_data, rean_sorted, rean_cdf, obs_sorted, obs_cdf, months_of_interest):
    corrected_data = reforecast_data.copy()
    
    for month in months_of_interest:
        month_mask = reforecast_data['date'].dt.month == month
        month_data = reforecast_data[month_mask]
        
        for ensemble_member in [f'ensemble_{i}' for i in range(1, 26)]:
            reforecast_values = month_data[ensemble_member].values
            corrected_values = quantile_mapping(reforecast_values, rean_sorted, rean_cdf, obs_sorted, obs_cdf)
            corrected_values = np.maximum(corrected_values, 0)  # Ensure no negative values
            corrected_data.loc[month_mask, ensemble_member] = corrected_values
    
    return corrected_data

# Load the ensemble reforecast data
file_path = r'C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia\merged\Alazani Basin - Shakriani Hydrological Station_reforecast_efas_2006_2018.fcst'
column_names = ["date", "lead_time"] + [f'ensemble_{i}' for i in range(1, 26)]
usecols = list(range(27))  # Only read the first 27 columns
reforecast_data = pd.read_csv(file_path, delim_whitespace=True, header=None, names=column_names, usecols=usecols)
reforecast_data['date'] = pd.to_datetime(reforecast_data['date'], format='%Y%m%d%H')

# Load observed and reanalysis data
obs_file = r'C:\Users\dottacor\Documents2\GitFiles\Georgia_obs\Q-Alazani-Shaqriani.obs'
reanalysis_file = r'C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia_historical\output\discharge_data_1991_2018.txt'

observed_data = pd.read_csv(obs_file, delim_whitespace=True, header=None, names=["date", "flow"])
reanalysis_data = pd.read_csv(reanalysis_file, delim_whitespace=True, header=None, names=["date", "flow"])

# Convert date columns to datetime
observed_data['date'] = pd.to_datetime(observed_data['date'], format='%Y%m%d%H')
reanalysis_data['date'] = pd.to_datetime(reanalysis_data['date'], format='%Y%m%d')

# Remove non-finite values
observed_data = observed_data.replace([np.inf, -np.inf], np.nan).dropna()
reanalysis_data = reanalysis_data.replace([np.inf, -np.inf], np.nan).dropna()

# Calculate empirical CDFs for observed and reanalysis data over the whole period
obs_sorted, obs_cdf = calculate_cdf(observed_data['flow'])
rean_sorted, rean_cdf = calculate_cdf(reanalysis_data['flow'])

# Define the months of interest (all months)
months_of_interest = range(1, 13)

# Apply the bias correction using quantile mapping for the entire data
corrected_data = bias_correction_qm(reforecast_data, rean_sorted, rean_cdf, obs_sorted, obs_cdf, months_of_interest)

# Restore the original lead times and date format
corrected_data['date'] = reforecast_data['date'].dt.strftime('%Y%m%d%H')
corrected_data['lead_time'] = reforecast_data['lead_time']

# Reorganize the columns to match the original format
corrected_data = corrected_data[['date', 'lead_time'] + [f'ensemble_{i}' for i in range(1, 26)]]

# Save the corrected data with the same format as the input
corrected_dir = r'C:\Users\dottacor\Documents2\GitFiles\corrected'
os.makedirs(corrected_dir, exist_ok=True)
corrected_file_path = os.path.join(corrected_dir, 'corrected_reforecast_data_all.fcst')

# Ensure the output format is consistent with the input format
corrected_data.to_csv(corrected_file_path, index=False, sep=' ', header=False, float_format='%.1f')

print(f"Bias correction completed and saved to:", corrected_file_path)




























#%% other approach GAM

import pandas as pd
import numpy as np
from pygam import LinearGAM, s
import os

# Load the ensemble reforecast data
file_path = r'C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia\merged\Alazani Basin - Shakriani Hydrological Station_reforecast_efas_2006_2018.fcst'
column_names = ["date", "lead_time"] + [f'ensemble_{i}' for i in range(1, 26)]
usecols = list(range(27))  # Only read the first 27 columns
reforecast_data = pd.read_csv(file_path, delim_whitespace=True, header=None, names=column_names, usecols=usecols)
reforecast_data['date'] = pd.to_datetime(reforecast_data['date'], format='%Y%m%d%H')

# Load observed and reanalysis data
obs_file = r'C:\Users\dottacor\Documents2\GitFiles\Georgia_obs\Q-Alazani-Shaqriani.obs'
reanalysis_file = r'C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia_historical\output\discharge_data_1991_2018.txt'

observed_data = pd.read_csv(obs_file, delim_whitespace=True, header=None, names=["date", "flow"])
reanalysis_data = pd.read_csv(reanalysis_file, delim_whitespace=True, header=None, names=["date", "flow"])

# Convert date columns to datetime
observed_data['date'] = pd.to_datetime(observed_data['date'], format='%Y%m%d%H')
reanalysis_data['date'] = pd.to_datetime(reanalysis_data['date'], format='%Y%m%d')

# Merge reanalysis and observed data on date
merged_data = pd.merge(reanalysis_data, observed_data, on='date', suffixes=('_reanalysis', '_observed')).dropna()

# Fit GAM model for each month separately
def fit_gam(monthly_data):
    X = monthly_data['flow_reanalysis'].values.reshape(-1, 1)
    y = monthly_data['flow_observed'].values
    gam = LinearGAM(s(0)).fit(X, y)
    return gam

# Apply GAM correction for each ensemble member
def apply_gam_correction(reforecast_data, gam_models, months_of_interest):
    corrected_data = reforecast_data.copy()

    for month in months_of_interest:
        month_mask = reforecast_data['date'].dt.month == month
        month_data = reforecast_data[month_mask]

        gam_model = gam_models[month]
        
        for ensemble_member in [f'ensemble_{i}' for i in range(1, 26)]:
            reforecast_values = month_data[ensemble_member].values.reshape(-1, 1)
            corrected_values = gam_model.predict(reforecast_values)
            corrected_values = np.maximum(corrected_values, 0)  # Ensure no negative values
            corrected_data.loc[month_mask, ensemble_member] = corrected_values

    return corrected_data

# Train GAM models for each month
gam_models = {}
for month in range(1, 13):
    monthly_data = merged_data[merged_data['date'].dt.month == month]
    gam_models[month] = fit_gam(monthly_data)

# Define the months of interest (all months)
months_of_interest = range(1, 13)

# Apply the GAM correction for the entire data
corrected_data = apply_gam_correction(reforecast_data, gam_models, months_of_interest)

# Restore the original lead times and date format
corrected_data['date'] = reforecast_data['date'].dt.strftime('%Y%m%d%H')
corrected_data['lead_time'] = reforecast_data['lead_time']

# Reorganize the columns to match the original format
corrected_data = corrected_data[['date', 'lead_time'] + [f'ensemble_{i}' for i in range(1, 26)]]

# Save the corrected data with the same format as the input
corrected_dir = r'C:\Users\dottacor\Documents2\GitFiles\corrected'
os.makedirs(corrected_dir, exist_ok=True)
corrected_file_path = os.path.join(corrected_dir, 'corrected_reforecast_data_gam.fcst')

# Ensure the output format is consistent with the input format
corrected_data.to_csv(corrected_file_path, index=False, sep=' ', header=False, float_format='%.1f')

print(f"Bias correction completed and saved to:", corrected_file_path)















#%% another approach segmented
import pandas as pd
import numpy as np
from scipy.stats import gamma
import matplotlib.pyplot as plt

# Function to calculate CDF
def calculate_cdf(data):
    sorted_data = np.sort(data)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    return sorted_data, cdf

# Function for quantile mapping
def quantile_mapping(reforecast_values, rean_sorted, rean_cdf, obs_sorted, obs_cdf):
    reforecast_cdf = np.interp(reforecast_values, rean_sorted, rean_cdf, left=0, right=1)
    corrected_values = np.interp(reforecast_cdf, obs_cdf, obs_sorted, left=obs_sorted[0], right=obs_sorted[-1])
    return corrected_values

# Function for segmented quantile mapping
def segmented_quantile_mapping(reforecast_values, rean_sorted, rean_cdf, obs_sorted, obs_cdf, threshold):
    low_flow_mask = reforecast_values <= threshold
    high_flow_mask = reforecast_values > threshold
    
    corrected_values = np.zeros_like(reforecast_values)
    
    # Apply more aggressive correction for low flows
    corrected_values[low_flow_mask] = quantile_mapping(
        reforecast_values[low_flow_mask], rean_sorted, rean_cdf, obs_sorted, obs_cdf
    )
    
    # Apply standard correction for high flows
    corrected_values[high_flow_mask] = quantile_mapping(
        reforecast_values[high_flow_mask], rean_sorted, rean_cdf, obs_sorted, obs_cdf
    )
    
    return corrected_values

# Define a function to perform segmented bias correction for each month using quantile mapping
def bias_correction_segmented_qm(reforecast_data, rean_sorted, rean_cdf, obs_sorted, obs_cdf, months_of_interest, threshold):
    corrected_data = reforecast_data.copy()
    
    for month in months_of_interest:
        month_mask = reforecast_data['date'].dt.month == month
        month_data = reforecast_data[month_mask]
        
        for ensemble_member in [f'ensemble_{i}' for i in range(1, 26)]:
            reforecast_values = month_data[ensemble_member].values
            corrected_values = segmented_quantile_mapping(
                reforecast_values, rean_sorted, rean_cdf, obs_sorted, obs_cdf, threshold
            )
            corrected_values = np.maximum(corrected_values, 0)  # Ensure no negative values
            corrected_data.loc[month_mask, ensemble_member] = corrected_values
    
    return corrected_data

# Load the ensemble reforecast data
file_path = r'C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia\merged\Alazani Basin - Shakriani Hydrological Station_reforecast_efas_2006_2018.fcst'
column_names = ["date", "lead_time"] + [f'ensemble_{i}' for i in range(1, 26)]
usecols = list(range(27))  # Only read the first 27 columns
reforecast_data = pd.read_csv(file_path, delim_whitespace=True, header=None, names=column_names, usecols=usecols)
reforecast_data['date'] = pd.to_datetime(reforecast_data['date'], format='%Y%m%d%H')

# Load observed and reanalysis data
obs_file = r'C:\Users\dottacor\Documents2\GitFiles\Georgia_obs\Q-Alazani-Shaqriani.obs'
reanalysis_file = r'C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia_historical\output\discharge_data_1991_2018.txt'

observed_data = pd.read_csv(obs_file, delim_whitespace=True, header=None, names=["date", "flow"])
reanalysis_data = pd.read_csv(reanalysis_file, delim_whitespace=True, header=None, names=["date", "flow"])

# Convert date columns to datetime
observed_data['date'] = pd.to_datetime(observed_data['date'], format='%Y%m%d%H')
reanalysis_data['date'] = pd.to_datetime(reanalysis_data['date'], format='%Y%m%d')

# Remove non-finite values
observed_data = observed_data.replace([np.inf, -np.inf], np.nan).dropna()
reanalysis_data = reanalysis_data.replace([np.inf, -np.inf], np.nan).dropna()

# Calculate empirical CDFs for observed and reanalysis data over the whole period
obs_sorted, obs_cdf = calculate_cdf(observed_data['flow'])
rean_sorted, rean_cdf = calculate_cdf(reanalysis_data['flow'])

# Define the months of interest (all months)
months_of_interest = range(1, 13)

# Define the threshold for low flow separation (e.g., 30th percentile of reanalysis data)
threshold = np.percentile(rean_sorted, 30)

# Apply the segmented bias correction using quantile mapping for the entire data
corrected_data = bias_correction_segmented_qm(reforecast_data, rean_sorted, rean_cdf, obs_sorted, obs_cdf, months_of_interest, threshold)

# Restore the original lead times and date format
corrected_data['date'] = reforecast_data['date'].dt.strftime('%Y%m%d%H')
corrected_data['lead_time'] = reforecast_data['lead_time']

# Reorganize the columns to match the original format
corrected_data = corrected_data[['date', 'lead_time'] + [f'ensemble_{i}' for i in range(1, 26)]]

# Save the corrected data with the same format as the input
corrected_dir = r'C:\Users\dottacor\Documents2\GitFiles\corrected'
os.makedirs(corrected_dir, exist_ok=True)
corrected_file_path = os.path.join(corrected_dir, 'corrected_reforecast_data_segmented_qm.fcst')

# Ensure the output format is consistent with the input format
corrected_data.to_csv(corrected_file_path, index=False, sep=' ', header=False, float_format='%.1f')

print(f"Bias correction completed and saved to:", corrected_file_path)















#%%
import pandas as pd
import numpy as np
from scipy.stats import gamma
from statsmodels.tsa.arima.model import ARIMA
import os

# Function to calculate CDF
def calculate_cdf(data):
    sorted_data = np.sort(data)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    return sorted_data, cdf

# Function for quantile mapping
def quantile_mapping(reforecast_values, rean_sorted, rean_cdf, obs_sorted, obs_cdf):
    reforecast_cdf = np.interp(reforecast_values, rean_sorted, rean_cdf, left=0, right=1)
    corrected_values = np.interp(reforecast_cdf, obs_cdf, obs_sorted, left=obs_sorted[0], right=obs_sorted[-1])
    return corrected_values

# Function for segmented quantile mapping
def segmented_quantile_mapping(reforecast_values, rean_sorted, rean_cdf, obs_sorted, obs_cdf, threshold):
    low_flow_mask = reforecast_values <= threshold
    high_flow_mask = reforecast_values > threshold
    
    corrected_values = np.zeros_like(reforecast_values)
    
    # Apply more aggressive correction for low flows
    corrected_values[low_flow_mask] = quantile_mapping(
        reforecast_values[low_flow_mask], rean_sorted, rean_cdf, obs_sorted, obs_cdf
    )
    
    # Apply standard correction for high flows
    corrected_values[high_flow_mask] = quantile_mapping(
        reforecast_values[high_flow_mask], rean_sorted, rean_cdf, obs_sorted, obs_cdf
    )
    
    return corrected_values

# Function to apply ARIMA model for temporal correction
def apply_arima_correction(observed_data, corrected_data):
    # Fit ARIMA model to observed data
    arima_model = ARIMA(observed_data, order=(1, 0, 0))  # Example order (1, 0, 0) for AR(1) model
    arima_fit = arima_model.fit()
    
    # Apply ARIMA model to corrected data
    corrected_arima = arima_fit.predict(start=0, end=len(corrected_data)-1, dynamic=False)
    
    # Combine results
    corrected_combined = corrected_data + corrected_arima
    
    # Ensure no negative values
    corrected_combined = np.maximum(corrected_combined, 0)
    
    return corrected_combined

# Define a function to perform segmented bias correction for each month using quantile mapping
def bias_correction_segmented_qm(reforecast_data, rean_sorted, rean_cdf, obs_sorted, obs_cdf, observed_data, months_of_interest, threshold):
    corrected_data = reforecast_data.copy()
    
    for month in months_of_interest:
        month_mask = reforecast_data['date'].dt.month == month
        month_data = reforecast_data[month_mask]
        
        for ensemble_member in [f'ensemble_{i}' for i in range(1, 26)]:
            reforecast_values = month_data[ensemble_member].values
            corrected_values = segmented_quantile_mapping(
                reforecast_values, rean_sorted, rean_cdf, obs_sorted, obs_cdf, threshold
            )
            corrected_values = np.maximum(corrected_values, 0)  # Ensure no negative values
            
            # Apply ARIMA correction
            observed_month_data = observed_data.loc[observed_data.index.month == month, 'flow']
            corrected_values_arima = apply_arima_correction(observed_month_data.values, corrected_values)
            
            corrected_data.loc[month_mask, ensemble_member] = corrected_values_arima
    
    return corrected_data

# Load the ensemble reforecast data
file_path = r'C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia\merged\Alazani Basin - Shakriani Hydrological Station_reforecast_efas_2006_2018.fcst'
column_names = ["date", "lead_time"] + [f'ensemble_{i}' for i in range(1, 26)]
usecols = list(range(27))  # Only read the first 27 columns
reforecast_data = pd.read_csv(file_path, delim_whitespace=True, header=None, names=column_names, usecols=usecols)
reforecast_data['date'] = pd.to_datetime(reforecast_data['date'], format='%Y%m%d%H')

# Load observed and reanalysis data
obs_file = r'C:\Users\dottacor\Documents2\GitFiles\Georgia_obs\Q-Alazani-Shaqriani.obs'
reanalysis_file = r'C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia_historical\output\discharge_data_1991_2018.txt'

observed_data = pd.read_csv(obs_file, delim_whitespace=True, header=None, names=["date", "flow"])
reanalysis_data = pd.read_csv(reanalysis_file, delim_whitespace=True, header=None, names=["date", "flow"])

# Convert date columns to datetime
observed_data['date'] = pd.to_datetime(observed_data['date'], format='%Y%m%d%H')
reanalysis_data['date'] = pd.to_datetime(reanalysis_data['date'], format='%Y%m%d')

# Set the date column as index for observed data
observed_data.set_index('date', inplace=True)

# Remove non-finite values
observed_data = observed_data.replace([np.inf, -np.inf], np.nan).dropna()
reanalysis_data = reanalysis_data.replace([np.inf, -np.inf], np.nan).dropna()

# Calculate empirical CDFs for observed and reanalysis data over the whole period
obs_sorted, obs_cdf = calculate_cdf(observed_data['flow'])
rean_sorted, rean_cdf = calculate_cdf(reanalysis_data['flow'])

# Define the months of interest (all months)
months_of_interest = range(1, 13)

# Define the threshold for low flow separation (e.g., 30th percentile of reanalysis data)
threshold = np.percentile(rean_sorted, 30)

# Apply the segmented bias correction using quantile mapping and ARIMA for the entire data
corrected_data = bias_correction_segmented_qm(reforecast_data, rean_sorted, rean_cdf, obs_sorted, obs_cdf, observed_data, months_of_interest, threshold)

# Restore the original lead times and date format
corrected_data['date'] = reforecast_data['date'].dt.strftime('%Y%m%d%H')
corrected_data['lead_time'] = reforecast_data['lead_time']

# Reorganize the columns to match the original format
corrected_data = corrected_data[['date', 'lead_time'] + [f'ensemble_{i}' for i in range(1, 26)]]

# Save the corrected data with the same format as the input
corrected_dir = r'C:\Users\dottacor\Documents2\GitFiles\corrected'
os.makedirs(corrected_dir, exist_ok=True)
corrected_file_path = os.path.join(corrected_dir, 'corrected_reforecast_data_segmented_qm_arima.fcst')

# Ensure the output format is consistent with the input format
corrected_data.to_csv(corrected_file_path, index=False, sep=' ', header=False, float_format='%.1f')

print(f"Bias correction completed and saved to:", corrected_file_path)


























#%%

#This approach should help in maintaining the ensemble spread while correcting for bias, especially in low flow conditions. By segmenting the data and applying ARIMA correction, we account for both distributional and temporal biases, leading to more reliable forecasts. This should result in better-preserved ensemble structures and reduced overfitting, especially for low flows.

#Compare the results from this method with the previous methods to evaluate if the low flow corrections are more accurate and if the ensemble spread is better maintained.

import pandas as pd
import numpy as np
from scipy.stats import gamma
from statsmodels.tsa.arima.model import ARIMA
import os

# Function to calculate CDF
def calculate_cdf(data):
    sorted_data = np.sort(data)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    return sorted_data, cdf

# Function for quantile mapping
def quantile_mapping(reforecast_values, rean_sorted, rean_cdf, obs_sorted, obs_cdf):
    reforecast_cdf = np.interp(reforecast_values, rean_sorted, rean_cdf, left=0, right=1)
    corrected_values = np.interp(reforecast_cdf, obs_cdf, obs_sorted, left=obs_sorted[0], right=obs_sorted[-1])
    return corrected_values

# Function for segmented quantile mapping
def segmented_quantile_mapping(reforecast_values, rean_sorted, rean_cdf, obs_sorted, obs_cdf, threshold):
    low_flow_mask = reforecast_values <= threshold
    high_flow_mask = reforecast_values > threshold
    
    corrected_values = np.zeros_like(reforecast_values)
    
    # Apply more aggressive correction for low flows
    corrected_values[low_flow_mask] = quantile_mapping(
        reforecast_values[low_flow_mask], rean_sorted, rean_cdf, obs_sorted, obs_cdf
    )
    
    # Apply standard correction for high flows
    corrected_values[high_flow_mask] = quantile_mapping(
        reforecast_values[high_flow_mask], rean_sorted, rean_cdf, obs_sorted, obs_cdf
    )
    
    return corrected_values

# Function to apply ARIMA model for temporal correction
def apply_arima_correction(observed_data, corrected_data):
    # Fit ARIMA model to observed data
    arima_model = ARIMA(observed_data, order=(1, 0, 0))  # Example order (1, 0, 0) for AR(1) model
    arima_fit = arima_model.fit()
    
    # Apply ARIMA model to corrected data
    corrected_arima = arima_fit.predict(start=0, end=len(corrected_data)-1, dynamic=False)
    
    # Combine results
    corrected_combined = corrected_data + corrected_arima
    
    # Ensure no negative values
    corrected_combined = np.maximum(corrected_combined, 0)
    
    return corrected_combined

# Define a function to perform segmented bias correction for each month using quantile mapping
def bias_correction_segmented_qm(reforecast_data, rean_sorted, rean_cdf, obs_sorted, obs_cdf, observed_data, months_of_interest, threshold):
    corrected_data = reforecast_data.copy()
    
    for month in months_of_interest:
        month_mask = reforecast_data['date'].dt.month == month
        month_data = reforecast_data[month_mask]
        
        for ensemble_member in [f'ensemble_{i}' for i in range(1, 26)]:
            reforecast_values = month_data[ensemble_member].values
            corrected_values = segmented_quantile_mapping(
                reforecast_values, rean_sorted, rean_cdf, obs_sorted, obs_cdf, threshold
            )
            corrected_values = np.maximum(corrected_values, 0)  # Ensure no negative values
            
            # Apply ARIMA correction
            observed_month_data = observed_data.loc[observed_data.index.month == month, 'flow']
            corrected_values_arima = apply_arima_correction(observed_month_data.values, corrected_values)
            
            corrected_data.loc[month_mask, ensemble_member] = corrected_values_arima
    
    return corrected_data

# Load the ensemble reforecast data
file_path = r'C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia\merged\Alazani Basin - Shakriani Hydrological Station_reforecast_efas_2006_2018.fcst'
column_names = ["date", "lead_time"] + [f'ensemble_{i}' for i in range(1, 26)]
usecols = list(range(27))  # Only read the first 27 columns
reforecast_data = pd.read_csv(file_path, delim_whitespace=True, header=None, names=column_names, usecols=usecols)
reforecast_data['date'] = pd.to_datetime(reforecast_data['date'], format='%Y%m%d%H')

# Load observed and reanalysis data
obs_file = r'C:\Users\dottacor\Documents2\GitFiles\Georgia_obs\Q-Alazani-Shaqriani.obs'
reanalysis_file = r'C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia_historical\output\discharge_data_1991_2018.txt'

observed_data = pd.read_csv(obs_file, delim_whitespace=True, header=None, names=["date", "flow"])
reanalysis_data = pd.read_csv(reanalysis_file, delim_whitespace=True, header=None, names=["date", "flow"])

# Convert date columns to datetime
observed_data['date'] = pd.to_datetime(observed_data['date'], format='%Y%m%d%H')
reanalysis_data['date'] = pd.to_datetime(reanalysis_data['date'], format='%Y%m%d')

# Set the date column as index for observed data
observed_data.set_index('date', inplace=True)

# Remove non-finite values
observed_data = observed_data.replace([np.inf, -np.inf], np.nan).dropna()
reanalysis_data = reanalysis_data.replace([np.inf, -np.inf], np.nan).dropna()

# Calculate empirical CDFs for observed and reanalysis data over the whole period
obs_sorted, obs_cdf = calculate_cdf(observed_data['flow'])
rean_sorted, rean_cdf = calculate_cdf(reanalysis_data['flow'])

# Define the months of interest (all months)
months_of_interest = range(1, 13)

# Define the threshold for low flow separation (e.g., 30th percentile of reanalysis data)
threshold = np.percentile(rean_sorted, 30)

# Apply the segmented bias correction using quantile mapping and ARIMA for the entire data
corrected_data = bias_correction_segmented_qm(reforecast_data, rean_sorted, rean_cdf, obs_sorted, obs_cdf, observed_data, months_of_interest, threshold)

# Restore the original lead times and date format
corrected_data['date'] = reforecast_data['date'].dt.strftime('%Y%m%d%H')
corrected_data['lead_time'] = reforecast_data['lead_time']

# Reorganize the columns to match the original format
corrected_data = corrected_data[['date', 'lead_time'] + [f'ensemble_{i}' for i in range(1, 26)]]

# Save the corrected data with the same format as the input
corrected_dir = r'C:\Users\dottacor\Documents2\GitFiles\corrected'
os.makedirs(corrected_dir, exist_ok=True)
corrected_file_path = os.path.join(corrected_dir, 'corrected_reforecast_data_segmented_qm_arima.fcst')

# Ensure the output format is consistent with the input format
corrected_data.to_csv(corrected_file_path, index=False, sep=' ', header=False, float_format='%.1f')

print(f"Bias correction completed and saved to:", corrected_file_path)

#%%