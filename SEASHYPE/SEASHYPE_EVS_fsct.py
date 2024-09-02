#%% Developed by Deborah Dotta, May 2024
# This code extracts data from txt sent by SMHI (SEASHYPE data) and turns into EVS acceptable format - ensemble forecasts .fcst

import numpy as np
import pandas as pd
import os
from datetime import datetime


#%% Define paths
base_path = r"C:\Users\dottacor\OneDrive - Stichting Deltares\Documents\Git\Msc-Thesis\SEASHYPE\SEASHYPE_reforecast_data"

#%% Function to read and process individual ensemble file
def process_ensemble_file(file_path, ensemble_number):
    try:
        # Read the data, using space as the delimiter and skip only the first line (assuming it's the header)
        data = pd.read_csv(file_path, sep='\s+', skiprows=1, engine='python')
        # Convert 'DATE' to datetime, then to string in the format 'YYYYMMDD00'
        data['DATE'] = pd.to_datetime(data.iloc[:, 0], format='%Y-%m-%d', errors='coerce').dt.strftime('%Y%m%d00')
        if data['DATE'].isna().any():
            print(f"Failed to convert some 'DATE' entries to datetime in {file_path}")
            return None
        # Ensure we are selecting the 6th data column (column index 5, as indexing starts at 0)
        output_column_name = f"data_{ensemble_number:02d}"
        data = data.iloc[:, [0, 5]].rename(columns={data.columns[5]: output_column_name})
        return data
    except Exception as e:
        print(f"Failed to process {file_path}: {e}")
        return None

#%% Loop through years, months, and ensembles
for year in range(1994, 2015):  # Modified the range to start from 1993
    start_month = 1  # Start from January
    for month in range(start_month, 13):  # Loop through all months
        ensemble_data = []
        folder_path = os.path.join(base_path, f"{year}_SEASHYPE")
        for ensemble in range(25):  # Ensemble goes from 00 to 24
            file_name = f"{year}{month:02d}_{ensemble:02d}_COUT.txt"
            file_path = os.path.join(folder_path, file_name)
            if os.path.exists(file_path):
                result = process_ensemble_file(file_path, ensemble)
                if result is not None:
                    ensemble_data.append(result)
            else:
                print(f"File does not exist: {file_path}")

        if ensemble_data:
            # Concatenate data horizontally, align by 'DATE'
            combined_data = pd.concat(ensemble_data, axis=1)
            # Ensure no duplicated 'DATE' columns remain
            combined_data = combined_data.loc[:, ~combined_data.columns.duplicated(keep='first')]

            # Add a new column starting with 24 and increasing by 24 for each row
            new_column_values = np.arange(24, 24 * len(combined_data) + 1, 24)
            combined_data.insert(1, 'New_Column', new_column_values, True)

            # Round the values in the third column until the last one to three decimal places and add trailing zeros
            for column in combined_data.columns[2:]:
                combined_data[column] = combined_data[column].round(3).apply(lambda x: "{:.3f}".format(x))

            # Save the processed data to a new file with header but without column names
            output_file = os.path.join(folder_path, f"{year}{month:02d}_COUT.fcst")
            # Convert date format to YYYYMMDD00 without hyphens
            combined_data.iloc[:, 0] = combined_data.iloc[:, 0].str.replace('-', '') + '00'
            combined_data.to_csv(output_file, index=False, sep='\t', header=True, lineterminator='\n', encoding='utf-8')
            # Remove column names from the file
            with open(output_file, 'r+', encoding='utf-8') as file:
                lines = file.readlines()
                file.seek(0)
                file.writelines(lines[1:])
                file.truncate()
            print(f"Data for {year}-{month:02d} processed and saved to {output_file}")
        else:
            print(f"No ensemble data collected for {year}-{month:02d}")

print("All data processing complete.")

# %%
