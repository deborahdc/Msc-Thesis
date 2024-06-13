#%% Developmed by Deborah Dotta, May 2024

import cdsapi
import os
import zipfile

def retrieve_efas_seasonal_reforecast(year, month, output_folder):
    c = cdsapi.Client()

    leadtimes = list(range(24, 5161, 24))  # Generate lead times from 24 to 5160 hours in steps of 24 hours

    output_zip_path = os.path.join(output_folder, f'{year}{month}_EFAS_seasonal_reforecast.zip')
    output_nc_path = os.path.join(output_folder, f'{year}{month}_EFAS_seasonal_reforecast.nc')

    c.retrieve(
        'efas-seasonal-reforecast',
        {
            'system_version': 'version_4_0',
            'variable': 'river_discharge_in_the_last_24_hours',
            'model_levels': 'surface_level',
            'hyear': year,
            'hmonth': month,
            'leadtime_hour': leadtimes,
            'format': 'netcdf4.zip',
            'area': [
                43.5, 40, 40,
                47.5,
            ],
        },
        output_zip_path)  # Save file in specified directory

    # Unzip the downloaded file
    with zipfile.ZipFile(output_zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_folder)

    # Get list of files extracted from the zip
    extracted_files = zip_ref.namelist()

    # Find the NetCDF file and rename it
    for file in extracted_files:
        if file.endswith('.nc'):
            os.rename(os.path.join(output_folder, file), output_nc_path)
            break

def main():
    start_year = int(input("Enter the start year (e.g., 1995): "))
    end_year = int(input("Enter the end year (e.g., 2020): "))
    start_month = int(input("Enter the start month (e.g., 5 for May): "))
    end_month = int(input("Enter the end month (e.g., 9 for September): "))
    output_folder = r"C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia"  # Specify output folder here

    for year in range(start_year, end_year + 1):
        for month in range(start_month, end_month + 1):
            month_str = f'{month:02d}'  # Format month as two digits
            print(f"Processing year {year}, month {month_str}...")
            retrieve_efas_seasonal_reforecast(year, month_str, output_folder)

if __name__ == "__main__":
    main()


#%%