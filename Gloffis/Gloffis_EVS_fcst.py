#%% Developped by Deborah, July 2024
#Takes output discharge from gloffis and formats into EVS format .fcst

import pandas as pd
import glob
import os

# Define input and output directories
input_directory = r'C:\Users\dottacor\OneDrive - Stichting Deltares\Documents\Git\Msc-Thesis\GLOFFIS\Output'  # keep all the output files here
output_directory = r'C:\Users\dottacor\OneDrive - Stichting Deltares\Documents\Git\Msc-Thesis\GLOFFIS\fcst'

# Define the station code
station_code = 'X007324'   # the one for Lobith

# Define the range of months to process
start_year = 1994
start_month = 1
end_year = 2015
end_month = 7

# Create a list of (year, month) tuples for the range
date_range = pd.date_range(start=f'{start_year}-{start_month:02d}', end=f'{end_year}-{end_month:02d}', freq='MS')
date_range = [(date.year, date.month) for date in date_range]

# Initialize an empty list to store the dataframes for the final combined output
final_df_list = []

# Loop over each (year, month) in the date range
for year, month in date_range:
    # Pattern to match the required files for the specific year and month
    file_pattern = os.path.join(input_directory, f'{year}{month:02d}*_wflow_sbm_rhine_*_forecast_seas5_Q.csv')

    # List of all matching files
    files = glob.glob(file_pattern)

    # Initialize an empty list to store the dataframes for the current month
    df_list = []

    # Loop through each file and process it
    for file in files:
        # Read the CSV file
        df = pd.read_csv(file)
        
        # Keep the first column and columns that have the code 'X007324'
        columns_to_keep = ['GMT'] + [col for col in df.columns if station_code in col]
        df = df[columns_to_keep]
        
        # Delete the first row
        df = df.iloc[1:].reset_index(drop=True)
        
        # Convert the 'GMT' column to datetime format
        df['GMT'] = pd.to_datetime(df['GMT'], infer_datetime_format=True)
        
        # Format the 'GMT' column to 'yyyymmddhh'
        df['GMT'] = df['GMT'].dt.strftime('%Y%m%d%H')
        
        # Insert the 'leadtime' column
        df.insert(1, 'leadtime', range(24, 24 * (len(df) + 1), 24))
        
        # Append the processed dataframe to the list for the current month
        df_list.append(df)

    # Concatenate all dataframes for the current month  #No need to save
    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)

        # Save the concatenated dataframe to a single .fcst file without the header
        #output_file = os.path.join(output_directory, f'{year}{month:02d}_{station_code}_combined_output.fcst')
        #combined_df.to_csv(output_file, index=False, header=False, sep=' ')

        # Append the monthly combined dataframe to the final list
        final_df_list.append(combined_df)

# Concatenate all the monthly combined dataframes into a single dataframe
if final_df_list:
    final_combined_df = pd.concat(final_df_list, ignore_index=True)

    # Save the final combined dataframe to a single .fcst file without the header
    final_output_file = os.path.join(output_directory, f'{station_code}_Q.fcst')
    final_combined_df.to_csv(final_output_file, index=False, header=False, sep=' ')

print("Processing completed and files saved successfully.")


#%%