# Portfolio

Hello! I can't show you everything I've built at Sunrise, but I can show a few snippets of code I've written.   

## [SQL Analytics Infrastructure: Building a Metrics Layer](https://github.com/thebbennett/portfolio/tree/master/metrics_layer)
As I worked to bring the modern data stack to Sunrise, I quickly became obsessed with the concept of the [metrics layer](https://benn.substack.com/p/metrics-layer). It was a complete lightbulb moment for me as I realized I needed to standardize our metrics in our data warehouse so everyone on my team would report the same numbers. Sunrise's most prized metric is our membrship size and accompanying demographic stats. Therefore, I built out an idempotent model to track Sunrise's membership size and demographics retroactively to when we first started collecting data.     

**[Metrics Members](https://github.com/thebbennett/portfolio/blob/master/metrics_layer/metrics_members.sql)**. 
* Uses a dbt package to generate a table of all weeks starting from March 2020 (when Sunrise started collecting data via EveryAction). 
* Indiciates whether a member took action on a given week. 
* Fills in the missing weeks from the temp table above so there is a row for every member and every week after the date of their membership.  
* Uses a window function to assess if a member has taken action in the last week or last 6 months. 

**[Metrics Members Over Time](https://github.com/thebbennett/portfolio/blob/master/metrics_layer/metrics_members_over_time.sql)**. 
* Aggregates the Metrics Members table to active members per week   

## [SQL Jinja: Demographics Metrics Macro](https://github.com/thebbennett/portfolio/blob/master/generate_demographics.sql)
My analysts often need to report the same demographic metrics for our analyses. There was a need to standardize our defitions of our demographic metrics, including definitions for BIPOC, white person, and working-class. I decided to build a macro with all of our definitions for every race, class, and gender metrics we could possibly report. If we ever need to update our demographic definitions, we only need to update our macro and the logic will be reflected in every table, every report, and every dashboard.  

The macro was built using dbt and Jinja. 

## [SQL Intermediate: EveryAction form responses to Google Sheets](https://github.com/thebbennett/portfolio/blob/master/EA-form-responses-to-google-sheets.SQL)  
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


## [Python Data Engineering: Get Extra Fields Container Script](https://github.com/thebbennett/portfolio/tree/master/get_extra_fields)  
Sunrise's top priority is to build a multi racial, multi class movement. So it came as a big shock when we learned our new CRM, EveryAction, would not provide us with race or gender data in our sync. In addition, EveryAction did not have a built in way to collect socio-economic class data.  

First, I led a cross-rank working group to determine how Sunrise should collect class. I knew that class was a difficult thing to measure, and that no matter what there would be error in our data collection methods. In forming a working group, key stakeholders at Sunrise were able to decide what kind of inaccuracy they were willing to accept in exchange for some understanding about the socio-economic class of our base.  

Once we settled on a custom question for class that met our standards, we then had to get the data out of EveryAction along with the race and gender data of our contacts. Since we could not access the race and gender data in the sync to our data warehouse, we decided to build out own custom sync. This project includes a `reuirements.txt` file, a `dev-requirements.txt` file, and unit testing. 

**The Get Extra Fields script:**
* Reads in the parameters set in Civis for API keys and other passwords
* Connects to Redshift to grab all new contacts and contacts with updated demographic data
* For those vanids, connects to the EveryAction API to grab with the get_person method to grab their demographic data 
* Build a dictionary of lists for each person with the information needed from the API call 
* Does some light data cleaning on the race and gender results
* Map the values of class, hub, and hub role to the dataframe
* Push the resulting dataframe as a Parsons Table to Redshift as a table, appending new rows 

