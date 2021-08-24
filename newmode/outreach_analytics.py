# import packages
from parsons import Newmode, GoogleSheets, Table
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import logging
import requests
from datetime import datetime
import time
import petl
import collections
import ipdb

startTime = datetime.now()

# If running on container, load this env
try:
    creds = json.loads(os.environ["GOOGLE_JSON_CRED_PASSWORD"])
    new_mode_username = os.environ["NEW_MODE_USERNAME"]
# If running locally, load this env
except KeyError:
    creds_file = "service_account.json"  # File path to OAuth2.0 JSON Credentials
    creds = json.load(open(creds_file))  # Load JSON credentials
    new_mode_username = "brittany@sunrisemovement.org"

new_mode_password = os.environ["NEW_MODE_PASSWORD"]

# -------------------------------------------------------------------------------
# Set up logger
# -------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter("{levelname} {message}", style="{")
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel("INFO")

TOOL_ID = 39195
# Instantiate parsons New Mode class
newmode = Newmode(
    api_user=new_mode_username, api_password=new_mode_password
)
# Instantiate parsons GSheets class
parsons_sheets = GoogleSheets(google_keyfile_dict=creds)


def get_target_with_sleep(target_id_list, sleep=5):
    target_names_list = []
    for target_id in target_id_list:
        try:
            target = newmode.get_target(target_id)
            target_name = target["full_name"]
            target_names_list.append(target_name)
        except:
            logger.info(f"API being rate limited, sleeping for {sleep} and trying again")
            time.sleep(sleep)
    return target_names_list

def transform_outreaches(outreaches):
    transformed_outreaches = []
    items_to_remove = [
        "modified_date",
        "action_date",
        "type",
        "subject",
        "person",
        "message",
        "duration",
        "metadata",
        "formdata",
    ]

    for outreach in outreaches:
        # Convert created_date from seconds since epoch to readable datetime
        outreach["created_date"] = datetime.fromtimestamp(
            int(outreach["created_date"])
        ).strftime("%Y-%m-%d")
        # Convert outreach_id to integer
        outreach["outreach_id"] = int(outreach["outreach_id"])
        # Replace target_id with human readable target name
        target_id_list = outreach["targets"]

        outreach["target_names"] = get_target_with_sleep(target_id_list)
        outreach.pop("targets")
        # Unnest important PII
        outreach["name"] = (
            outreach.get("person", "Freind").get("given_name", "Unknown")
            + " "
            + outreach.get("person", "Freind").get("family_name", "Unknown")
        )
        outreach["phone"] = outreach.get("person").get("phone")[0]
        # Remove unecessary data
        [outreach.pop(key, None) for key in items_to_remove]
        transformed_outreaches.append(outreach)

    # conver to Parsons Table
    transformed_outreaches = Table(transformed_outreaches)
    return transformed_outreaches

def get_calls_per_office(parsons_table):
    target_list = []
    for targets in petl.values(parsons_table.table, "target_names"):
        for target in targets:
            target_list.append(target)

    counter = collections.Counter(target_list)
    calls_counter = dict(counter)
    calls_per_office = [{"name" : key, "num_calls": value} for key, value in calls_counter.items()]
    return Table(calls_per_office)

if __name__ == "__main__":
    # Get all outreaches for given tool id
    outreaches = newmode.get_outreaches(TOOL_ID)
    # Tranform raw outreach data for spreadsheet
    transformed_outreaches = transform_outreaches(outreaches)
    # Set up tables for Google Sheets
    calls_per_day = Table(
        petl.aggregate(
            transformed_outreaches.table, key="created_date", aggregation=len
        )
    )
    leaderboard = petl.aggregate(
        transformed_outreaches.table, key="name", aggregation=len
    )

    calls_per_office = get_calls_per_office(transformed_outreaches)

    # rename columns for spreadsheet
    calls_per_day.rename_column('value', 'num_calls')
    calls_per_day=calls_per_day.rename_column('created_date', 'day')

    calls_per_office=calls_per_office.rename_column('name', 'office')
    # Sort leaderboard by num calls per person
    leaderboard_ranked = Table(petl.sort(leaderboard, 'value', reverse=True))
    leaderboard_ranked=leaderboard_ranked.rename_column('value', 'num_calls')
    # Get set up spreadsheet and errors spreadsheet
    spreadsheet_id = "1fPlKWVtpDWid06R8oi0bHgch1ShYovYyks2aSZKY6nY"
    # Push to Google Sheets
    parsons_sheets.overwrite_sheet(
        spreadsheet_id,
        calls_per_day,
        worksheet="calls per day",
        user_entered_value=False,
    )
    parsons_sheets.overwrite_sheet(
        spreadsheet_id,
        leaderboard_ranked,
        worksheet="leaderboard",
        user_entered_value=False,
    )
    parsons_sheets.overwrite_sheet(
        spreadsheet_id,
        calls_per_office,
        worksheet="calls per office",
        user_entered_value=False,
    )
    # Print script timing
    time_to_complete = datetime.now() - startTime
    logger.info("This script took %s", time_to_complete)
