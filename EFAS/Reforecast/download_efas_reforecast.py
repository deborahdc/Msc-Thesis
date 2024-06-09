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
                47.5, 40, 44,
                43.5,
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
    year = input("Enter the year (e.g., 1995): ")
    month = input("Enter the month (e.g., 05 for May): ")
    output_folder = r"C:\Users\dottacor\OneDrive - Stichting Deltares\Documents\Git\Msc-Thesis\EFAS\Reforecast"  # Specify output folder here

    retrieve_efas_seasonal_reforecast(year, month, output_folder)

if __name__ == "__main__":
    main()
#%%