#%% Developed by Deborah Dotta, June 2024
import os
import shutil

# Define base directory and output directory
base_directory = r"C:\Users\dottacor\Documents2\GitFiles\SEASHYPE_reforecast_data\Georgia"
output_directory = r"C:\Users\dottacor\Documents2\GitFiles\SEASHYPE_reforecast_data\Georgia\OUT_txt"

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Iterate over each year
for year in range(1993, 2016):
    year_directory = os.path.join(base_directory, str(year))
    
    # Iterate over each month
    for month in range(1, 13):
        month_directory = os.path.join(year_directory, str(month))
        
        # Iterate over each ensemble
        for ensemble in range(25):
            ensemble_directory = os.path.join(month_directory, str(ensemble))
            file_path = os.path.join(ensemble_directory, 'timeCOUT.txt')
            
            # Check if the timeCOUT.txt file exists
            if os.path.isfile(file_path):
                # Define the output file name
                output_file_name = f"{year}_{month}_{ensemble}.txt"
                output_file_path = os.path.join(output_directory, output_file_name)
                
                # Copy the file to the output directory with the new name
                shutil.copy(file_path, output_file_path)

print("Files have been copied and renamed successfully.")


#%%  

import os
import pandas as pd

# Define the input and output directories
input_directory = r"C:\Users\dottacor\Documents2\GitFiles\SEASHYPE_reforecast_data\Georgia\OUT_txt"
output_directory = os.path.join(input_directory, "step")

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Function to convert date format
def convert_date_format(date_str):
    return pd.to_datetime(date_str).strftime('%Y%m%d%H')

# Iterate over each file in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith(".txt"):
        file_path = os.path.join(input_directory, filename)
        
        # Read the file into a dataframe, skipping the first line
        df = pd.read_csv(file_path, sep='\t', skiprows=1)
        
        # Clean up column names
        df.columns = df.columns.str.strip()
        
        # Print column names for debugging
        print(f"Processing file: {filename}")
        print("Column names:", df.columns.tolist())
        
        # Check if the required columns exist
        if 'DATE' in df.columns and '316213' in df.columns:
            # Extract DATE and column 316213
            df = df[['DATE', '316213']]
            
            # Convert DATE format and add count column
            df['DATE'] = df['DATE'].apply(convert_date_format)
            df['COUNT'] = range(1, len(df) + 1)
            
            # Rearrange columns: DATE, COUNT, 316213
            df = df[['DATE', 'COUNT', '316213']]
            
            # Save the modified dataframe to the output directory without headers
            output_file_path = os.path.join(output_directory, filename)
            df.to_csv(output_file_path, sep='\t', index=False, header=False, float_format='%.3f')
        else:
            print(f"Required columns not found in {filename}")

print("Files have been processed and saved successfully.")
#%%


# Define the input and output directories
input_directory = r"C:\Users\dottacor\Documents2\GitFiles\SEASHYPE_reforecast_data\Georgia\OUT_txt\step"
output_directory = r"C:\Users\dottacor\Documents2\GitFiles\SEASHYPE_reforecast_data\Georgia\OUT_txt\merged"

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Initialize a list to store the contents of all files
all_data = []

# Iterate over each file in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith(".txt"):
        file_path = os.path.join(input_directory, filename)
        
        # Read the contents of the file
        with open(file_path, 'r') as file:
            file_data = file.readlines()
            all_data.extend(file_data)

# Define the output file path
output_file_path = os.path.join(output_directory, "merged.fcst")

# Write the combined data to the output file
with open(output_file_path, 'w') as output_file:
    output_file.writelines(all_data)

print("All files have been merged and saved successfully.")


#%%