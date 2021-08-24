# Civis container: https://platform.civisanalytics.com/spa/#/scripts/containers/97400118

#!/usr/bin/env python
# coding: utf-8

# In[1]:


# load the necessary packages
import pandas as pd
import numpy as np
from parsons import Redshift, Table, VAN, S3, utilities
import datetime
from datetime import date
from requests.exceptions import HTTPError
import os
import logging 

logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(levelname)s %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel('INFO')

# In[2]:


# # loacl enviro variables
# os.environ['REDSHIFT_PORT']
# os.environ['REDSHIFT_DB']
# os.environ['REDSHIFT_HOST']
# os.environ['REDSHIFT_USERNAME']
# os.environ['REDSHIFT_PASSWORD']
# os.environ['S3_TEMP_BUCKET']
# os.environ['AWS_ACCESS_KEY_ID']
# os.environ['AWS_SECRET_ACCESS_KEY']
# van_key = os.environ['VAN_API_KEY']


# In[3]:


#CIVIS enviro variables 
os.environ['REDSHIFT_PORT']
os.environ['REDSHIFT_DB'] = os.environ['REDSHIFT_DATABASE']
os.environ['REDSHIFT_HOST']
os.environ['REDSHIFT_USERNAME'] = os.environ['REDSHIFT_CREDENTIAL_USERNAME'] 
os.environ['REDSHIFT_PASSWORD'] = os.environ['REDSHIFT_CREDENTIAL_PASSWORD'] 
os.environ['S3_TEMP_BUCKET'] = 'parsons-tmc'
os.environ['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']
van_key = os.environ['VAN_PASSWORD']


# In[4]:


#init Redshift instance
rs = Redshift()
ea = VAN(db = 'EveryAction', api_key = van_key)


# In[5]:


# table = rs.query('select contacts.vanid from sunrise_ea.tsm_tmc_contacts_sm contacts limit 500')
table = rs.query("""
                with max_date as (
                  select contacts.vanid
                  , max(datemodified) as max_datemod
                  , max(date_updated) as max_dateup
                  from sunrise_ea.tsm_tmc_contacts_sm contacts
                  left join sunrise.contacts_extra_fields fields
                  ON contacts.vanid = fields.vanid
                  where contacts.personcommitteeid=86718
                  group by 1
                  )
              select vanid
              from max_date
              where max_datemod > max_dateup
              or max_dateup is null
                """)
if table.num_rows > 0:
  logger.info(f"Found {table.num_rows} records to get extra fields for.")
  list_vanid = table.to_dataframe()['vanid'].to_list()


  # In[6]:


  # init dict with variables for final table
  result_dict = {}

  result_dict['vanid'] = []
  result_dict['dob'] = []
  result_dict['race'] = []
  result_dict['gender'] = []
  result_dict['class'] = []
  result_dict['hub'] = []
  result_dict['hub_role'] = []
  result_dict['secondary_hub_role'] = []
  result_dict['other_hub_role'] = []
  result_dict['active'] = []

  error_messages = []


  # For every vanid in the list pulled from the SELECT statement above:
  # Check if the response is a dictionary to avoid throwing Civis an error (in the case of a bad vanid where the result is NONE)
  # Then parse the JSON dump to get vanid, dob, all of the races and genders the user selected, class, hub, and hub role.

  # Append any error messages to the error list. At the moment, this script does not push the erorr messages to an error table.


  for person in list_vanid:
      try:
          response = ea.get_person(person, id_type='vanid', expand_fields = ['reported_demographics','custom_fields'])
      except HTTPError as e:
          response = e

      if type(response) == dict:
          result_dict['vanid'].append(response['vanId'])
          result_dict['dob'].append(response['dateOfBirth'])
          race_list = []

          if response['selfReportedRaces'] is not None:
              for race in response['selfReportedRaces']:
                  race_list.append(race['reportedRaceName'])
          else:    
              race_list.append(None)
          result_dict['race'].append(race_list)


          gender_list = []
          if response['selfReportedGenders'] is not None:
              for gender in response['selfReportedGenders']:
                  gender_list.append(gender['reportedGenderName'])
          else:
              gender_list.append(None)
          result_dict['gender'].append(gender_list)

          result_dict['class'].append("N/A")
          result_dict['hub'].append([item for item in response['customFields'] if item["customFieldId"] == 12][0]['assignedValue'])
          result_dict['hub_role'].append([item for item in response['customFields'] if item["customFieldId"] == 7][0]['assignedValue'])  
          result_dict['secondary_hub_role'].append([item for item in response['customFields'] if item["customFieldId"] == 8][0]['assignedValue'])
          result_dict['other_hub_role'].append([item for item in response['customFields'] if item["customFieldId"] == 9][0]['assignedValue'])
          result_dict['active'].append([item for item in response['customFields'] if item["customFieldId"] == 6][0]['assignedValue'])



      else:
          error_messages.append(response)


  # In[7]:


  # clean dataframe 
  result_df = pd.DataFrame(result_dict)
  result_df['dob'] = result_df['dob'].astype(str).str[0:10]
  result_df['race'] = result_df['race'].apply(lambda x: ','.join(map(str, x)))
  result_df['gender'] = result_df['gender'].apply(lambda x: ','.join(map(str, x)))


  # In[9]:


  #get available values for each demographic var
  response = ea.get_person(101904222, id_type='vanid', expand_fields = ['reported_demographics','custom_fields'])
  rlist = response['customFields']

  # create a list of available values for each demogrpahic var
  #class_list = [item for item in rlist if item["customFieldId"] == 19][0]['customField']['availableValues']
  hub_list = [item for item in rlist if item["customFieldId"] == 12][0]['customField']['availableValues']
  hub_role_list = [item for item in rlist if item["customFieldId"] == 7][0]['customField']['availableValues']
  secondary_hub_role_list = [item for item in rlist if item["customFieldId"] == 8][0]['customField']['availableValues']
  active_list = [item for item in rlist if item["customFieldId"] == 6][0]['customField']['availableValues']


  # In[10]:


  # convert list to dictionary to map to dataframe
  hub_dict = {}
  for d in hub_list:
      hub_dict[str(d['id'])] = d['name']

  #class_dict = {}
  #for d in class_list:
      #class_dict[str(d['id'])] = d['name']

  hub_role_dict = {}
  for d in hub_role_list:
      hub_role_dict[str(d['id'])] = d['name']

  secondary_hub_role_dict = {}
  for d in secondary_hub_role_list:
      secondary_hub_role_dict[str(d['id'])] = d['name']


  # In[11]:


  # race and gender summaries for ease of analysis

  # setting race summary
  result_df.loc[result_df['race'] == 'Caucasian or White', 'race_summary'] = 'white'

  result_df.loc[(result_df['race'].notnull() ) &
                 (result_df['race'] != 'Caucasian or White'), 'race_summary'] = 'poc'

  result_df.loc[result_df['race'] == 'None',  'race_summary'] = None



  # cis identities
  result_df.loc[(result_df['gender'].str.contains('Woman')) |
                (result_df['gender'].str.contains('Female')) |
                (result_df['gender'].str.contains('Cisgender Woman')) |
                (result_df['gender'].str.contains('Femme')), 'gender_summary'] = 'female' 

  result_df.loc[(result_df['gender'].str.contains('Male')) |
                 (result_df['gender'].str.contains('Man')) |
                  (result_df['gender'].str.contains('Cisgender Man')), 'gender_summary'] = 'male' 


  # gender nonconforming identities
  result_df.loc[(result_df['gender'].str.contains('Agender')) |
                 (result_df['gender'].str.contains('Androgyne')) |
                (result_df['gender'].str.contains('Androgynous')) |
                (result_df['gender'].str.contains('Bigender')) |
                (result_df['gender'].str.contains('Butch')) |
                (result_df['gender'].str.contains('Female to Male')) |
                (result_df['gender'].str.contains('FTM')) |
                (result_df['gender'].str.contains('Gender Fluid')) |
                (result_df['gender'].str.contains('Gender Questioning')) |
                (result_df['gender'].str.contains('Gender Non-conforming')) |
                (result_df['gender'].str.contains('Gender Variant')) |
                (result_df['gender'].str.contains('Genderless')) |
                (result_df['gender'].str.contains('Genderqueer')) |
                (result_df['gender'].str.contains('Hirja')) |
                (result_df['gender'].str.contains('Intersex')) |
                (result_df['gender'].str.contains('Male to Female')) |
                (result_df['gender'].str.contains('Masc')) |
                (result_df['gender'].str.contains('MTF')) |
                (result_df['gender'].str.contains('Neither')) |
                (result_df['gender'].str.contains('Neutrois')) |
                (result_df['gender'].str.contains('Non-Binary')) |
                (result_df['gender'].str.contains('Non-Op')) |
                (result_df['gender'].str.contains('Other')) |
                (result_df['gender'].str.contains('Pangender')) |
                (result_df['gender'].str.contains('Pansexual')) |
                (result_df['gender'].str.contains('Queer')) |
                (result_df['gender'].str.contains('Questioning')) |
                (result_df['gender'].str.contains('Trans')) |
                (result_df['gender'].str.contains('Transfeminine')) |
                (result_df['gender'].str.contains('Transgender')) |
                (result_df['gender'].str.contains('Transgender Male')) |
                (result_df['gender'].str.contains('Transgender Female')) |
                (result_df['gender'].str.contains('Transgender Man')) |
                (result_df['gender'].str.contains('Transgender Person')) |
                (result_df['gender'].str.contains('Transmasculine')) |
                (result_df['gender'].str.contains('Two Spirit')), 'gender_summary'] = 'gnc' 

  # fill in any other values I might have missed as gnc                
  result_df['gender_summary'] = result_df.loc[result_df['gender'].notnull(), 'gender_summary'].fillna('gnc')

  # set null to null
  result_df.loc[result_df['gender'] == 'None', 'gender_summary'] = None


  # In[12]:


  # map values of class, hub, and hub role to dataframe
  #result_df['class'].replace(class_dict, inplace = True)
  result_df['hub'].replace(hub_dict, inplace = True)
  result_df['hub_role'].replace(hub_role_dict, inplace = True)
  result_df['secondary_hub_role'].replace(secondary_hub_role_dict, inplace = True)
  result_df['date_updated'] = date.today()

  result_df = result_df.where(pd.notnull(result_df), None)
  result_df = result_df.replace({'None': None})
  result_df = result_df.replace({np.nan: None})


  # In[ ]:


  # col order same as civis 
  result_df= result_df[['vanid', 'dob', 'race', 'gender', 'class', 'hub', 'hub_role', 'secondary_hub_role', 'active', 'race_summary', 'gender_summary', 'date_updated', 'other_hub_role']]


  # In[13]:


  # convert data frame to Parsons Table
  result_table = Table.from_dataframe(result_df)
  
  logger.info(f"Result table contains {result_table.num_rows} records to append to sunrise.contacts_extra_fields.")


  # In[14]:


  # copy Table into Redshift, append new rows
  rs.copy(result_table, 'sunrise.contacts_extra_fields' ,if_exists='append', distkey='vanid', sortkey = None, alter_table = True)

else:
  logger.info(f"No records to get extra fields for today!")
