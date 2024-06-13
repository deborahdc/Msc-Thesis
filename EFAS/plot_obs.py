#%%# Developed by Deborah Dotta, June 2024
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transform_and_save_data(input_filepath, output_filepath):
    # Read the data
    data = pd.read_csv(input_filepath, sep=r'\s+', header=None, names=['Year', 'Month', 'Day', 'Value'])

    # Ensure 'Value' column is numeric
    data['Value'] = pd.to_numeric(data['Value'], errors='coerce')

    # Create a datetime column
    data['Datetime'] = pd.to_datetime(data[['Year', 'Month', 'Day']])

    # Add an hour column with a fixed value of 00 (midnight)
    data['Hour'] = 0

    # Format the datetime to the required format yyyymmddhh
    data['Datetime_formatted'] = data['Datetime'].dt.strftime('%Y%m%d') + data['Hour'].astype(str).str.zfill(2)

    # Select required columns and save to .fcst file
    data[['Datetime_formatted', 'Value']].to_csv(output_filepath, sep=' ', index=False, header=False)
    logger.info(f"Data transformed and saved to {output_filepath}")
    return data

def plot_monthly_data(data, year, output_filepath):
    # Filter data for the selected year
    data['Year'] = data['Datetime'].dt.year
    data_filtered = data[data['Year'] == year]

    # Check if data is filtered correctly
    logger.info(f"Filtered data for the year {year}: {data_filtered.head()}")

    # Create a figure with subplots for each month
    fig, axes = plt.subplots(4, 3, figsize=(20, 15), sharey=True)
    axes = axes.flatten()

    for month in range(1, 13):
        ax = axes[month-1]
        data_month = data_filtered[data_filtered['Datetime'].dt.month == month]
        if not data_month.empty:
            ax.plot(data_month['Datetime'], data_month['Value'], label=f'{data_month["Datetime"].dt.strftime("%B %Y").iloc[0]}', color='blue')
            ax.set_title(data_month["Datetime"].dt.strftime("%B %Y").iloc[0])
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True)
        else:
            logger.warning(f"No data available for {year}-{month:02d}")

    fig.suptitle(f'Historical Data for {year}', fontsize=16)
    fig.tight_layout(rect=[0, 0.03, 1, 0.97])
    
    # Save plot
    plt.savefig(output_filepath)
    plt.close()
    logger.info(f"Plot saved as {output_filepath}")

def main():
    input_filepath = r'C:\Users\dottacor\Documents2\GitFiles\Georgia_obs\Q-Alazani-Shaqriani.txt'  # Update this path as necessary
    output_filepath = r'C:\Users\dottacor\Documents2\GitFiles\Georgia_obs\Q-Alazani-Shaqriani.obs'
    year_to_plot = 2009  # Specify the year to plot
    output_plot_filepath = rf'C:\Users\dottacor\Documents2\GitFiles\Georgia_obs\Historical_Data_{year_to_plot}.png'

    # Transform and save data
    data = transform_and_save_data(input_filepath, output_filepath)

    # Plot data for the specified year
    plot_monthly_data(data, year_to_plot, output_plot_filepath)

if __name__ == "__main__":
    main()


#%%
