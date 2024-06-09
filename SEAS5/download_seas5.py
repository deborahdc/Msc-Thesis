#%% Preliminaries
# Jan Verkade - jan.verkade@deltares.nl
# download_era5.py
# April 30, 2021
# This script looks at a pi run file to determine the download period
# in absence thereof, tzero will be set to current date and import folder location to current path
# updated 4-4-2024 by Deborah Dotta

#%% Preliminaries
import datetime as dt
from pathlib import Path
import os
import logging
import cdsapi
import xml.etree.cElementTree as ET


#%% Where am I?
if '__file__' in globals():
    my_path = Path(__file__).parent.absolute()
else:
    my_path = Path('.').parent.absolute()


#%% Set up logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
log_file = str( my_path /  'download_seas5.log' )
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level = logging.INFO, filename = log_file)
logging.info('Initiating logging. Note date/time stamps within log file are in local time.')
logging.debug('Running CDS API script as user '+os.getlogin())


#%% Create credentials file if that does not already exist # replace for your own credentials
my_credentials = {"url": "https://cds.climate.copernicus.eu/api/v2",
                  "key": "298991:3c60fd0f-afd7-40a1-b7a5-15bac644860c"}

my_cred_file = os.path.expanduser("~/.cdsapirc")
if not(os.path.exists(my_cred_file)):
    logging.debug('Pre-existing CDS credentials file not found; creating a new one')
    f= open(my_cred_file,"w+")
    for k, v in my_credentials.items():
        f.write(str(k) + ': '+ str(v) + '\n')
    f.close()
else:
    my_vars = {}
    with open(my_cred_file) as myfile:
        for line in myfile:
            name, var = line.partition(":")[::2]
            my_vars[name.strip()] = var
    logging.debug('Pre-existing CDS credentials file found. Using API key '+my_vars['key'])


#%% If there is a runinfo.xml file, read it
my_runinfo_file = Path(my_path) / 'runinfo.xml'
if my_runinfo_file.is_file():
    logging.info('runinfo.xml found')
    tree = ET.parse(my_runinfo_file)
    ns = '{http://www.wldelft.nl/fews/PI}'
    day0 = tree.find('{0}time0'.format(ns)).get('date')
    day0 = dt.datetime.strptime(day0, "%Y-%m-%d")
    day0 = day0.replace(day=1)
    props = tree.find('{0}properties/{0}string'.format(ns))
    import_folder = props.attrib.get('value') #Assumption: there is a single key/value pair only
    logging.info('From runinfo.xml, identified day0 as ' + str(day0))
    logging.info('From runinfo.xml, identified import_folder as ' + import_folder)
else:
    logging.info('No runinfo.xml file found. Setting custom start date for data retrieval.')
    day0 = dt.datetime(2008, 6, 1)  # Replace with your desired year, month, day   #changed this part
    import_folder = str(Path(my_path) )
    logging.info('Set day0 to ' + str(day0))
    logging.info('Set import_folder to ' + import_folder)

logging.debug('day0: ' + str(day0))
day0_str= '{}'.format(day0.strftime("%Y-%m-%d"))

#%% Build server object and retrieve the data: 24h native time step variables
c = cdsapi.Client()
logging.debug('CDS client object built.')
logging.debug('Using credentials from '+my_cred_file)

deltat = 24
my_lt = list(range(0,4320+deltat,deltat))
my_variables = ['surface_solar_radiation_downwards','total_precipitation']
target_file = str( Path(import_folder) / (day0.strftime("%Y%m%d") + '_seas5_'+str(deltat)+'h.grib.tmp') )
logging.debug('Target file: ' + target_file)

my_request = {
        'originating_centre':'ecmwf',
        'system':'51',
        'variable': my_variables,
        'date': day0_str,
        'leadtime_hour':my_lt
        }

logging.debug('Request: ' + str(my_request) )

start = dt.datetime.now()
logging.info('Sending request to CDS at ' + start.strftime('%A, %B %d, %Y, %H:%M:%S'))

c.retrieve('seasonal-original-single-levels',my_request,target_file)

end = dt.datetime.now()
logging.info('Finished retrieval at ' + end.strftime("%A, %B %d, %Y, %H:%M:%S"))

duration = round( (end-start).total_seconds() )
logging.info('Retrieval required ' + str(duration) + ' seconds.')

#Rename target file
os.rename(target_file,target_file.replace(".grib.tmp",".grib"))
logging.info('Downloaded file renamed from ' + target_file + ' to ' + target_file.replace(".grib.tmp",".grib"))



#%% Build server object and retrieve the data: 6h native time step variables
c = cdsapi.Client()
logging.debug('CDS client object built.')
logging.debug('Using credentials from '+my_cred_file)

deltat = 6
my_lt = list(range(0,4320+deltat,deltat))
my_variables = ['2m_temperature']
target_file = str( Path(import_folder) / (day0.strftime("%Y%m%d") + '_seas5_'+str(deltat)+'h.grib.tmp') )
logging.debug('Target file: ' + target_file)

my_request = {
        'originating_centre':'ecmwf',
        'system':'51',
        'variable': my_variables,
        'date': day0_str,
        'leadtime_hour':my_lt
        }

logging.debug('Request: ' + str(my_request) )

start = dt.datetime.now()
logging.info('Sending request to CDS at ' + start.strftime('%A, %B %d, %Y, %H:%M:%S'))

c.retrieve('seasonal-original-single-levels',my_request,target_file)

end = dt.datetime.now()
logging.info('Finished retrieval at ' + end.strftime("%A, %B %d, %Y, %H:%M:%S"))

duration = round( (end-start).total_seconds() )
logging.info('Retrieval required ' + str(duration) + ' seconds.')

#Rename target file
os.rename(target_file,target_file.replace(".grib.tmp",".grib"))
logging.info('Downloaded file renamed from ' + target_file + ' to ' + target_file.replace(".grib.tmp",".grib"))

# %%
