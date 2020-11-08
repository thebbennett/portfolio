# Portfolio

Hello! I can't show you everything I've built at Sunrise, but I can show a few snippets of code I've written.   

# [Data Cleaning in SQL Example](https://github.com/thebbennett/portfolio/blob/master/data_cleaning_in_sql_example.sql)  
Data are always messy, and my job is to figure out how and to what degree. Sunrise uses a peer to peer texting platform called Spoke. We create "campaigns" in Spoke and then volunteers text out that initial campaign message (that we craft) to thousands of contacts. Spoke does not have a way to tag or organize your campaigns. I worked with my Texting Director to create our own Spoke tag feature via naming conventions of our campaigns.  

All campaigns from a certain date onwards were meant to be named with the following convention:  

```
designation_tag1,tag2,tag3_YYYY-MM-DD_name-of-campaign-title
```

For example: IE_requestaballot-2020-10-29_Michigan-P1-voters

Now, I never assumed that all our Spoke campaigns were named exactly in this way. If I had more time (ie, we weren't in the middle of GOTV), I would have written and built in a test in SQL that checked for the format of this campaign title.  

Instead, I inserted this script in a workflow immediately after my 2x daily Spoke import to clean and parse the campaign title into separate designations, tags, dates, and titles. 
