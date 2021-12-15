
# Sync Demographic Data from EveryAction

EveryAction does not include race and gender in their commercial Pipeline sync. Sunrise engineered a custom sync to bring in demographic data to our Redshift warehouse. Our sync brings in gender, race, as well as some other custom fields. You can modify this script to bring in any custom fields you desire. 

## Requirements
This project assumes that:

* You're using EveryAction
* You're using Redshift
* You have a Parsons VAN API key
* You are able to modify the script in this repo to suit your needs. Namely, the schema of your choice and the addition of any other custom fields.
* You're using the modified race terms as defined [here](https://github.com/sunrisedatadept/code_library/blob/main/everyaction/change_gender_and_race_terms.js)

## Scripts

[Get Extra Fields Container](https://github.com/sunrisedatadept/sync-everyaction-demographic-data/blob/main/get_extra_fields_container.py)  
This is the container version of the script. This is what you want to point your Civic Container script to. It will not run locally. 

## Usage

1. Clone this Github repository -- you'll need to specify your new url in the civis interface
2. Create `{schema}.get_extra_fields` table in your warehouse. 

```
CREATE TABLE {schema}.get_extra_fields 
(
  vanid         INTEGER,
  dob           VARCHAR,
  race          VARCHAR,
  active        VARCHAR ,
  date_updated  VARCHAR
);

```
4. Edit the following lines:

Replace `sunrise_ea.tsm_tmc_contacts_sm` with your table for EveryAction contacts. 

```
table = rs.query("""
                with max_date as (
                  select contacts.vanid
                  , max(datemodified) as max_datemod
                  , max(date_updated) as max_dateup
                  from sunrise_ea.tsm_tmc_contacts_sm contacts
                  left join sunrise.contacts_extra_fields fields
                  ON contacts.vanid = fields.vanid
                  group by 1
                  )
              select vanid
              from max_date
              where max_datemod > max_dateup
              or max_dateup is null
              limit 10000
                """)

```

Replace `sunrise` here with your schema

```
rs.copy(result_table, 'sunrise.contacts_extra_fields' ,if_exists='append', distkey='vanid', sortkey = None, alter_table = True)
```

4. Create a new Container Script in Civis
5. The following parameters must be set in the script for this to work:

| PARAMETER NAME | DISPLAY NAME | DEFAULT | TYPE              | MAKE REQUIRED |
|----------------|--------------|---------|-------------------|---------------|
| VAN            | VAN          | N/A     | Custom Credential | Yes           |
| REDSHIFT       | REDSHIFT     | N/A     | Database          | Yes           |
| AWS            | AWS          | N/A     | AWS Credential    | Yes           |

4. Connect civis to your github repository and point it appropriately.

5. Put the following in the command lines COMMAND section:

```
pip install pandas
python get_extra_fields_container.py

```


