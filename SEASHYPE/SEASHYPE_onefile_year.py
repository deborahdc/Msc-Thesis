#%% Developed by Deborah Dotta, May 2024

import os
import pandas as pd

# Define base directory
base_directory = r"C:\Users\dottacor\OneDrive - Stichting Deltares\Documents\Git\Msc-Thesis\SEASHYPE\SEASHYPE_reforecast_data"

# Iterate over each folder within the base directory
for folder_to_process in os.listdir(base_directory):
    folder_path = os.path.join(base_directory, folder_to_process)
    
    # Check if the item in the base directory is a folder
    if os.path.isdir(folder_path):
        dataframes = []  # Initialize an empty list to store the dataframes
        
        # Traverse through all files in the specified folder
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            # Check if the file is a .fcst file
            if file.endswith(".fcst"):
                # Read the .fcst file into a dataframe
                df = pd.read_csv(file_path, sep='\t', header=None)
                # Append the dataframe to the list
                dataframes.append(df)
        
        # Concatenate all dataframes vertically into one
        if dataframes:
            final_combined_df = pd.concat(dataframes, axis=0, ignore_index=True)
            # Write the combined dataframe to a new .fcst file inside the folder
            output_file = os.path.join(folder_path, f"{folder_to_process}_joined.fcst")
            final_combined_df.to_csv(output_file, index=False, sep='\t', header=False)
            print(f"All data combined and saved to {output_file}")
        else:
            print(f"No .fcst files found in the folder: {folder_to_process}")

#%%
