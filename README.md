# Portfolio

Hello! I can't show you everything I've built at Sunrise, but I can show a few snippets of code I've written.   

## [WIP Bringing out Meaning in Messy Data](https://github.com/thebbennett/portfolio/blob/master/wip_movement_engagement.sql)
I'm currently working new infrastructure to bring insight into the absorption, engagement, and retention of our movement. There is no consensus on what is means to be a member of Sunrise. In this project I had to decide what pieces of data across all our systems count as a "member action" and then bring that all together in a workable table that would allow me to explore how people enter and move through our movement. 

This code unions EveryAction online actions, event attendance, digital acquisition, leadership roles, donations, and email subscription history into one table. The actions are then ranked, allowing us to analyze the actions history of our volunteer base. Downstream transformations include analyzing popular first actions and summing the distribution of number of actions taken.  

## [Fun with Refactoring Code with dbt](https://github.com/thebbennett/refactoring_with_dbt)  
Explore this repo to see my work to refactor old work with dbt.   

## [Data Cleaning in SQL Example](https://github.com/thebbennett/portfolio/blob/master/data_cleaning_in_sql_example.sql)  
Data are always messy, and my job is to figure out how and to what degree. Sunrise uses a peer to peer texting platform called Spoke. We create "campaigns" in Spoke and then volunteers text out that initial campaign message (that we craft) to thousands of contacts. Spoke does not have a way to tag or organize your campaigns. I worked with my Texting Director to create our own Spoke tag feature via naming conventions of our campaigns.  

All campaigns from a certain date onwards were meant to be named with the following convention:  

```
designation_tag1,tag2,tag3_YYYY-MM-DD_name-of-campaign-title
```

For example: IE_requestaballot-2020-10-29_Michigan-P1-voters

Now, I never assumed that all our Spoke campaigns were named exactly in this way. If I had more time (ie, we weren't in the middle of GOTV), I would have written and built in a test in SQL that checked for the format of this campaign title.  

Instead, I inserted this script in a workflow immediately after my 2x daily Spoke import to clean and parse the campaign title into separate designations, tags, dates, and titles. 

**This code**:
* Renames by hand campaigns with slightly off campaign name formats 
* Parses the designation, tags, dates, and title
* Renames by hand some dates that had typos 
* Excludes some campaigns that did not use the naming convention altogether 
* grants access to the table to Periscope

## [EveryAction form responses to Google Sheets](https://github.com/thebbennett/portfolio/blob/master/EA-form-responses-to-google-sheets.SQL)  
In early 2020 I led a CRM transition away from ActionNetwork to EveryAction. Before this point, Sunrise staff were not bound to use rigorous data systems. Even though EveryAction is a powerful tool that could seriously scale the impact of our work, organizers were hesitant to adopt a new system. One pain point was EveryAction's limited functionality with their online forms. 

Organizers were very comfortable using Google Forms. But there were many benefits to using EveryAction online forms as opposed to Google Forms (having all our data in one place, analyzing new contacts brought in via organizing programs, funneling  people into our email list, etc).  

Unfortunately, EveryAction has 2 separate reports for their forms: one for basic information and a second for any custom questions you add. Organizers wanted to see all their data in one place, and have it populate automatically with new data (as opposed to exporting the data manually each day).   

In response to this need, I developed a workflow that took raw EveryAction form response data, gathered the various custom questions responses in various tables, pivoted the table, and pushed the data automatically every day to a Google Sheet.    

With this workflow, organizers became more likely to use our data systems, meaning that Sunrise was able to grow our movement.   

**This code**:
* Gathers all the form responses for a given onlineformid  
* One by one, gets the responses for boolean, integer, date, short text, long text, single, and multi responses in the respective tables, depending on the type of custom questions chosen for that form  
* Denotes which response is the most recent response, since some users fill out forms more than once (and we want to retain all responses and let our organizers decide which row to keep)  
* Joins in demographic data from a separate workflow  
* Joins together all the data along with a date_updated   

We adapted this code into a dbt workflow so that instead of writing out all this code manually, we feed a macro an onlineformid and it spits out the SQL. This code is part of a larger workflow that pushes responses every day to a Google Sheet. 


## [Python Example: Get Extra Fields Container Script](https://github.com/thebbennett/portfolio/blob/master/python_example_get_extra_fields.py)  
Sunrise's top priority is to build a multi racial, multi class movement. So it came as a big shock when we learned our new CRM, EveryAction, would not provide us with race or gender data in our sync. In addition, EveryAction did not have a built in way to collect socio-economic class data.  

First, I led a cross-rank working group to determine how Sunrise should collect class. I knew that class was a difficult thing to measure, and that no matter what there would be error in our data collection methods. In forming a working group, key stakeholders at Sunrise were able to decide what kind of inaccuracy they were willing to accept in exchange for some understanding about the socio-economic class of our base.  

Once we settled on a custom question for class that met our standards, we then had to get the data out of EveryAction along with the race and gender data of our contacts. Since we could not access the race and gender data in the sync to our data warehouse, we decided to use the EveryAction API. 

I wrote a Python script that was set up as a "container script" in Civis. A container script runs off a container in Docker, and in this case allows us to run Python scripts in Civis that take advantage of Parsons.

**This code**
* Reads in the parameters set in Civis for API keys and other passwords
* Connects to Redshift to grab all new contacts and contacts with updated demographic data
* For those vanids, connects to the EveryAction API to grab with the get_person method to grab their demographic data 
* Build a dictionary of lists for each person with the information needed from the API call 
* Does some light data cleaning on the race and gender results
* Create gender and race summaries columns for easy data manipulation
* Map the values of class, hub, and hub role to the dataframe
* Push the resulting dataframe as a Parsons Table to Redshift as a table, appending new rows 


## [Basic SQL Data Wrangling](https://github.com/thebbennett/portfolio/blob/master/sql_data_wrangling.sql)  
I built out a comprehensive dashboard to monitor progress towards our electoral goals for our IE Presidential GOTV work. One of our main tactics was peer to peer texting. We needed to be able to quickly see the results of our campaigns, including the response rate (filtering out responses that were opt out requests), opt out rates, and the number of people who responded positively to our survey question).  
  
This code create the following table with our Spoke texting data:  
![Image of resulting table](https://static.wixstatic.com/media/fc8483_0befe24c735f4bd9ac3b950d0359af4b~mv2.png)  

**This code**:
* Wrangles the data such that my base CTE has the number of texts sent and the num of texts received per person. This is needed for excluding opt out replies from our response rate
* Calculates basic stats for each campaign for our GOTV IE work only 

## [Intermediate SQL Data Wrangling](https://github.com/thebbennett/portfolio/blob/master/Intermediate-SQL-data-wrangling.sql)
Our organizers working on downballot campaigns were running a massive volunteer phonebanking operation. They needed to be able to see the current week's and the next week's phonebanking events' shift sign ups relative to the goal for that event.  

**This code**:  
* Grabs only the downballot phonebanking events for 2020 General slate of candidates in Mobilize America
* Converts the start date of the timeslot to the timezone of the event
* Assigns a shift goal based on the candidates name (shift goal came from lead organizer)
* Grabs only centralized events based on the event creator's email address, assuming events created with Sunrise Movement emails were centralized events. The script eventually included bypasses for events created by specific volunteers (those emails have been anonymized) 
* Selects events for the current week 
* De dupes the list (duplicates are due to a bad sync/import job, we chose to continue de duping instead of fixing in the middle of GOTV)
* Groups the shift sign ups by event, renaming the event title to include a readable date and time
* Calculates the number of remaining shifts 
* finally, selects the relevant columns for plotting in Periscope

![Image of the output of this SQL in Periscope, in a bar chart](https://static.wixstatic.com/media/fc8483_3c411c32bd9a4705a24691b8842c188e~mv2.png)
