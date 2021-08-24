
# Civis container: https://platform.civisanalytics.com/spa/#/scripts/containers/76144120

#!/usr/bin/env python
# coding: utf-8


# load the necessary packages
from parsons import Redshift, Table, VAN, S3, utilities
from datetime import date, datetime
from requests.exceptions import HTTPError
import os
import json 
import pytest
from parsons.utilities import json_format
import logging

#If running on container, load this env
try:
    os.environ['REDSHIFT_PORT']
    os.environ['REDSHIFT_DB'] = os.environ['REDSHIFT_DATABASE']
    os.environ['REDSHIFT_HOST']
    os.environ['REDSHIFT_USERNAME'] = os.environ['REDSHIFT_CREDENTIAL_USERNAME']
    os.environ['REDSHIFT_PASSWORD'] = os.environ['REDSHIFT_CREDENTIAL_PASSWORD']
    os.environ['S3_TEMP_BUCKET'] = 'parsons-tmc'
    os.environ['AWS_ACCESS_KEY_ID']
    os.environ['AWS_SECRET_ACCESS_KEY']
    van_key = os.environ['VAN_PASSWORD']

#If running locally, load this env
except KeyError:
    os.environ['REDSHIFT_PORT']
    os.environ['REDSHIFT_DB']
    os.environ['REDSHIFT_HOST']
    os.environ['REDSHIFT_USERNAME']
    os.environ['REDSHIFT_PASSWORD']
    os.environ['S3_TEMP_BUCKET']
    os.environ['AWS_ACCESS_KEY_ID']
    os.environ['AWS_SECRET_ACCESS_KEY']
    van_key = os.environ['VAN_API_KEY']

# Set up logger
logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(levelname)s %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel('INFO')



class SunriseRedshift(Redshift):

    def get_contact_vanids(self, query):
        """
        Query Sunrise Redshift and return a list of contacts
        """
        table = self.query(query)
        contact_vanids = table["vanid"]
        return contact_vanids

class SunriseVAN(VAN):
    def get_person(self, id, id_type='vanid', expand_fields=[
                   'contribution_history', 'addresses', 'phones', 'emails',
                   'codes', 'custom_fields', 'external_ids', 'preferences',
                   'recorded_addresses', 'reported_demographics', 'suppressions',
                   'cases', 'custom_properties', 'districts', 'election_records',
                   'membership_statuses', 'notes', 'organization_roles',
                   'disclosure_field_values']):
        """
        Returns a single person record using their VANID or external id.

        `Args:`
            id: str
                A valid id
            id_type: str
                A known person identifier type available on this VAN instance
                such as ``dwid``. Defaults to ``vanid``.
            expand_fields: list
                A list of fields for which to include data. If a field is omitted,
                ``None`` will be returned for that field. Can be ``contribution_history``,
                ``addresses``, ``phones``, ``emails``, ``codes``, ``custom_fields``,
                ``external_ids``, ``preferences``, ``recorded_addresses``,
                ``reported_demographics``, ``suppressions``, ``cases``, ``custom_properties``,
                ``districts``, ``election_records``, ``membership_statuses``, ``notes``,
                ``organization_roles``, ``scores``, ``disclosure_field_values``.
        `Returns:`
            A person dict
        """

        # Change end point based on id type
        url = 'people/'

        id_type = '' if id_type in ('vanid', None) else f"{id_type}:"
        url += id_type + str(id)

        expand_fields = ','.join([json_format.arg_format(f) for f in expand_fields])

        # Removing the fields that are not returned in MyVoters
        NOT_IN_MYVOTERS = ['codes', 'contribution_history', 'organization_roles']

        if self.connection.db_code == 0:
            expand_fields = [v for v in expand_fields if v not in NOT_IN_MYVOTERS]

        # logger.info(f'GETTING person with {id_type} of {id} at url {url}')
        return self.connection.get_request(url, params={'$expand': expand_fields})

def extract_custom_field_values(custom_fields, custom_field_id):
    """
    For a given array of custom fields, return the human-readable value of the custom field
    """
    try:
        for custom_field in custom_fields:
            if custom_field.get("customFieldId") == custom_field_id:
                available_values = custom_field['customField']['availableValues']
                assigned_value = int(custom_field['assignedValue'])
                for value in available_values:
                    if value['id'] == assigned_value:
                        custom_field_name = value['name']
    except:
        custom_field_name = None

    return custom_field_name


def relabel_race(race):
    """
    Overwrite EA backend terms with Sunrise's preferred front end terms

    Key:
    Asian -> Asian/Asian American
    Black or African American -> Black/African American
    Caucasian or White -> Caucasian/White
    Hispanic -> Latino/Latina/Latinx
    Middle Eastern -> Middle Eastern
    Native American -> Native American/First Nations/Alaska Native
    Native Hawaiian -> Native Hawaiian
    Pacific Islander -> Pacific Islander
    Other -> Other
    """
    race = race.replace("Asian", "Asian/Asian American")
    race = race.replace("Black or African American", "Black/African American")
    race = race.replace("Caucasian or White", "Caucasian/White")
    race = race.replace("Hispanic", "Latino/Latina/Latinx")
    race = race.replace("Native American", "Native American/First Nations/Alaska Native")

    return race


def transform_person_for_redshift(person):
    """
    Transform the result returned by VAN into the shape we need to upload to Redshift
    """

    # init dict with variables for final table| create
    result_dict = {}

    # TODO: map each field as we transform it (rather than as a separate step)
    result_dict["vanid"] = person["vanId"]

    try:
        result_dict["dob"] = person["dateOfBirth"][0:10]
    except TypeError:
        result_dict["dob"] = None
    
    result_dict["race"] = ",".join([
        relabel_race(race.get("reportedRaceName")) 
        for race in person.get("selfReportedRaces", []) or []
    ])

    result_dict["gender"] = ",".join([
        gender.get("reportedGenderName")
        for gender in person.get("selfReportedGenders", []) or []
    ])

    result_dict["class"] = extract_custom_field_values(person.get("customFields"), 19)

    result_dict["hub"] = extract_custom_field_values(person.get("customFields"), 12)

    result_dict["hub_role"] = extract_custom_field_values(person.get("customFields"), 7)
    result_dict["secondary_hub_role"] = extract_custom_field_values(
        person.get("customFields"), 8
    )

    # this one looks different because it's a boolean result. Should we make the extract_custom_field_values function handle booleans?
    result_dict["active"] = [
        custom_field["assignedValue"]
        for custom_field in person.get("customFields")
        if custom_field["customFieldId"] == 6
    ][0]

    result_dict["date_updated"] = date.today().strftime("%m/%d/%Y")

    result_dict["other_hub_role"] = extract_custom_field_values(
        person.get("customFields"), 9
    )

    return result_dict


if __name__ == "__main__":
    # Initiate Redshift instance
    rs = SunriseRedshift()

    # Initiate EveryAction (NGP side) instance
    ea = SunriseVAN(db="EveryAction", api_key=van_key)

    # Query most recently modified contacts from Everyaction where the
    # modified date is more recent than the updated date
    query = """
            with max_date as (
              select
                contacts.vanid,
                max(datemodified) as max_datemod,
                max(date_updated) as max_dateup
              from sunrise_ea.tsm_tmc_contacts_sm contacts
              left join sunrise.contacts_extra_fields fields
                on contacts.vanid = fields.vanid
              where contacts.vanid not in (select vanid from sunrise.get_extra_fields_errors)
              group by 1
              )
          select vanid
          from max_date
          where max_datemod > max_dateup
          or max_dateup is null
          limit 10000
            """

    contact_vanids = rs.get_contact_vanids(query)

    extra_fields = []
    errors = []
    # contact_vanids = [101572625, 101706044, 101754035, 101967590]
    for contact_vanid in contact_vanids:
        
        try:
            person = ea.get_person(
                contact_vanid,
                id_type="vanid",
                expand_fields=["reported_demographics", "custom_fields"]
            )
            transformed_person = transform_person_for_redshift(person)
            extra_fields.append(transformed_person)
        except HTTPError as e:
            print(e)
            error = {
                "vanid": contact_vanid,
                "error": str(e)[:999]
                }   
            errors.append(error)   
        
    logger.info(f'Found {len(extra_fields)} new contacts to add to contacts_extra_fields')
    logger.info(f'Identified {len(errors)} errors. Appending to errors table.')

    # convert to Parsons table
    tbl = Table(extra_fields)
    errors_tbl = Table(errors)

    # copy Table into Redshift, append new rows
    rs.copy(tbl, 'sunrise.contacts_extra_fields' ,if_exists='append', distkey='vanid', sortkey = None, alter_table = True)
    rs.copy(errors_tbl, 'sunrise.get_extra_fields_errors' ,if_exists='append', distkey='vanid', sortkey = None, alter_table = True)
