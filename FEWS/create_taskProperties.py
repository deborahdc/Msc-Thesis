#%% Preliminaries
# Jan Verkade
# jan.verkade@deltares.nl
# create_taskProperties.py
# June 19, 2021
# Present script aims to create a taskProperties.xml file that will run various workflows as defined by user
#

#%% Preliminaries
import datetime as dt
from pathlib import Path
import os
import logging
from lxml import etree
import xml.etree.cElementTree as ET
import pandas as pd
import numpy as np

#%% Where am I?
if '__file__' in globals():
    my_path = Path(__file__).parent.absolute()
else:
    my_path = Path('.').parent.absolute()


#%% Set up logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
log_file = str( my_path /  'create_taskProperties.log' )
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level = logging.DEBUG, filename = log_file)
logging.info('Initiating logging. Please note that date/time stamps within log file are in local time.')
logging.debug('Running script as user '+os.getlogin())

#%% Create dataframe containing all workflows and time0 combinations
my_tasks = pd.read_csv('create_taskProperties.csv',parse_dates=True)
my_tasks['time0'] = pd.to_datetime(my_tasks['time0'],format='%d/%m/%Y %H:%M:%S')
my_tasks['coldState_fixedStartTime'] = pd.to_datetime(my_tasks['coldState_fixedStartTime'],format='%d/%m/%Y %H:%M:%S')
logging.info('csv file with tasks has been imported into dataframe')


#%% define function for adding <taskProperties> element
def create_taskProperties(time0,workflowId,stateSelection,coldState_groupId,coldState_fixedStartTime):
  tp_element = etree.Element('taskProperties')
  tp_element.append(etree.Element('userId')); tp_element[-1].text=os.getlogin()
  tp_element.append(etree.Element('workflowId')); tp_element[-1].text=workflowId
  tp_element.append(etree.Element('forecastPriority')); tp_element[-1].text='Normal'
  tp_element.append(etree.Element('makeForcastCurrent')); tp_element[-1].text='true'
  
  el_task_selection = etree.Element('taskSelection')
  el_single_task = etree.SubElement(el_task_selection, "singleTask")
  el_time0 = etree.SubElement(el_single_task,"time0")
  el_time0.text=time0.strftime('%Y-%m-%dT%H:%M:%S')
  
  if not(pd.isna(stateSelection)):
      el_state_selection = etree.Element('stateSelection')
      if stateSelection == 'cold':
          el_state_coldState = etree.SubElement(el_state_selection, 'coldState')
          if not pd.isna(coldState_groupId):
              el_state_groupId = etree.SubElement(el_state_coldState, 'groupId')
              el_state_groupId.text = str(int(coldState_groupId))
          if not pd.isna(coldState_fixedStartTime):
              el_state_groupId = etree.SubElement(el_state_coldState, 'fixedStartTime')
              el_state_groupId.set('date',coldState_fixedStartTime.strftime('%Y-%m-%d'))
              el_state_groupId.set('time',coldState_fixedStartTime.strftime('%H:%M:%S'))
              #el_state_groupId.text = coldState_fixedStartTime
              
      if stateSelection == 'warm':
        el_state_warmState = etree.SubElement(el_state_selection, 'warmState')
        etree.SubElement(el_state_warmState, 'stateSearchPeriod', {"start":"-5","end":"-3","unit":"week"})
        my_location = tp_element.find(".//makeForcastCurrent")
        my_location.addnext(el_state_selection)

  my_location = tp_element.find(".//workflowId")
  my_location.addnext(el_task_selection)
  
  if not pd.isna(coldState_fixedStartTime):
      my_location = tp_element.find(".//makeForcastCurrent")
      my_location.addnext(el_state_selection)
      
  return(tp_element)

#%% build actual xml file
logging.info('Creating xml file headers')
attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
nsmap = {None : "http://www.wldelft.nl/fews",
         "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

root = etree.Element("taskPropertiesPredefined", 
                     {attr_qname: "http://www.wldelft.nl/fews http://fews.wldelft.nl/schemas/version1.0/taskPropertiesPredefined.xsd"},
                     nsmap=nsmap)

logging.info('Creating ' + str(len(my_tasks.index)) + ' taskProperties elements')
for index, row in my_tasks.iterrows():
    logging.debug('Creating taskProperties element for ' + row['workflowId'] + ' @ ' + row['time0'].strftime('%Y-%m-%dT%H:%M:%S'))
    #print(row)
    tp_element = create_taskProperties(row['time0'], row['workflowId'], row['stateSelection'], row['coldState_groupId'], row['coldState_fixedStartTime'])
    root.append(tp_element)

#print(etree.tostring(root, pretty_print=True))
logging.info('Writing xml root to file')
etree.ElementTree(root).write('create_taskProperties.xml', pretty_print=True, xml_declaration=True, encoding="utf-8")


#%% Useful links
# On namespacing the xml file: https://stackoverflow.com/questions/46405690/how-to-include-the-namespaces-into-a-xml-file-using-lxml

