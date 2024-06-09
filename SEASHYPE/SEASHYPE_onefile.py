#%% Developed by Deborah Dotta, May 2024

import os
import pandas as pd

# Define base directory
base_directory = r"C:\Users\dottacor\OneDrive - Stichting Deltares\Documents\Git\Msc-Thesis\SEASHYPE\SEASHYPE_reforecast_data"

# Initialize an empty list to store the dataframes for the entire period
all_dataframes = []

# Iterate over each folder within the base directory
for folder_to_process in os.listdir(base_directory):
    folder_path = os.path.join(base_directory, folder_to_process)
    
    # Check if the item in the base directory is a folder
    if os.path.isdir(folder_path):
        # Initialize an empty list to store the dataframes for the current folder
        dataframes = []
        
        # Traverse through all files in the specified folder
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            # Check if the file is a joined .fcst file
            if file.endswith("_joined.fcst"):
                # Read the joined .fcst file into a dataframe
                df = pd.read_csv(file_path, sep='\t', header=None)
                # Append the dataframe to the list for the current folder
                dataframes.append(df)
        
        # Concatenate all dataframes vertically into one for the current folder
        if dataframes:
            combined_df_folder = pd.concat(dataframes, axis=0, ignore_index=True)
            # Append the concatenated dataframe of the current folder to the list for the entire period
            all_dataframes.append(combined_df_folder)

# Concatenate all dataframes vertically into one for the entire period
if all_dataframes:
    final_combined_df = pd.concat(all_dataframes, axis=0, ignore_index=True)
    # Write the combined dataframe to a new .fcst file for the entire period
    output_file = os.path.join(base_directory, "whole_period_joined.fcst")
    final_combined_df.to_csv(output_file, index=False, sep='\t', header=False)
    print(f"All data combined for the whole period and saved to {output_file}")
else:
    print("No joined .fcst files found in the folders.")

#%%

