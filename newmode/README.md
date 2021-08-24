# New Mode Analytics
Container script link: https://platform.civisanalytics.com/spa/#/scripts/containers/122180887  

This script:  

* Grabs all the outreaches for the "Call for the Green New Deal" campaign  
* Summarizes the number of calls per day  
* Summarizes the number of calls per office  
* Creates a leaderboard of top callers  
* Pushes the three tables to a [Google Sheet](https://docs.google.com/spreadsheets/u/1/d/1fPlKWVtpDWid06R8oi0bHgch1ShYovYyks2aSZKY6nY/edit#gid=0) for organizers to use during phonebanks  

The container script can be triggered by sending an email to: console-inbound+run.122180887.5dd1799666b1c1325e84abbee95e87c4@civisanalytics.com  


## Container Set Up
1. Clone this Github repository -- you'll need to specify your new url in the civis interface  
2. Create a new Container Script in Civis  
3. The following parameters must be set in the script for this to work:  

| PARAMETER NAME            | DISPLAY NAME     | DEFAULT | TYPE              | MAKE REQUIRED |
|---------------------------|------------------|---------|-------------------|---------------|
| GOOGLE_JSON_CRED_PASSWORD | Google JSON Cred | N/A     | String            | Yes           |
| NEW_MODE                  | New Mode         | N/A     | Custom Credential | Yes           |

4. Connect civis to your github repository and point it appropriately.  
5. Use the `movementcooperative/parsons` image and set Tag to `latest`  
