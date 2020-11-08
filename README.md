# Portfolio

Hello! I can't show you everything I've built at Sunrise, but I can show a few snippets of code I've written.   

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

Organizers were very comfortable using Google Forms. But there were many benefits to using EveryAction online forms as opposed to Google Forms (having all our data in one place, analyzing new contacts brought in via organizing programs, funnelling people into our email list, etc).  

Unfortuantely, EveryAction has 2 spearate reports for their forms: one for basic information and a second for any custom questions you add. Organizers wanted to see all their data in one place, and have it populate automatically with new data (as opposed to exporting the data manually each day).   

In response to this need, I developed a workflow that took raw EveryAction form response data, gathered the various custom questions responses in various tables, pivoted the table, and pushed the data automatically every day to a Google Sheet.    

With this workflow, organizers became more likely to use our data systems, meaning that Sunrise was able to grow our movement.   

**This code**:
* Gathers all the form responses for a given onlineformid  
* One by one, gets the responses for boolean, integer, date, short text, long text, single, and multi responses in the respective tables, depending on the type of custom questions chosen for that form  
* Denotes which response is the most recent response, since some users fill out forms more than once (and we want to retain all responses and let our organizers decide which row to keep)  
* Joins in demographic data from a separate workflow  
* Joins together all the data along with a date_updated   

We adpated this code into a dbt workflow so that instead of writing out all this code manually, we feed a macro an onlineformid and it spits out the SQL. This code is part of a larger workflow that pushes responses every day to a Google Sheet. 
