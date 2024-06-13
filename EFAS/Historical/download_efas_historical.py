#%% Developmed by Deborah Dotta, June 2024

import cdsapi
import os
import zipfile

def retrieve_efas_historical(year, month, output_folder):
    c = cdsapi.Client()

    output_zip_path = os.path.join(output_folder, f'{year}{month}_EFAS_historical.zip')
    output_nc_path = os.path.join(output_folder, f'{year}{month}_EFAS_historical.nc')

    c.retrieve(
        'efas-historical',
        {
            'system_version': 'version_4_0',
            'variable': 'river_discharge_in_the_last_6_hours',
            'model_levels': 'surface_level',
            'hyear': year,
            'hmonth': month,
            'hday': [
                '01', '02', '03',
                '04', '05', '06',
                '07', '08', '09',
                '10', '11', '12',
                '13', '14', '15',
                '16', '17', '18',
                '19', '20', '21',
                '22', '23', '24',
                '25', '26', '27',
                '28', '29', '30',
                '31',
            ],
            'time': [
                '00:00', '06:00', '12:00',
                '18:00',
            ],
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
    start_year = int(input("Enter the start year (e.g., 2009): "))
    end_year = int(input("Enter the end year (e.g., 2020): "))
    start_month = int(input("Enter the start month (e.g., 1 for January): "))
    end_month = int(input("Enter the end month (e.g., 12 for December): "))
    output_folder = r"C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia_historical"  # Specify output folder here

    for year in range(start_year, end_year + 1):
        for month in range(start_month, end_month + 1):
            month_str = f'{month:02d}'  # Format month as two digits
            print(f"Processing year {year}, month {month_str}...")
            retrieve_efas_historical(year, month_str, output_folder)

if __name__ == "__main__":
    main()


#%%