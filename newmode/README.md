# New Mode Analytics

This script:  

* Grabs all the outreaches for the "Call for the Green New Deal" campaign  
* Summarizes the number of calls per day  
* Summarizes the number of calls per office  
* Creates a leaderboard of top callers  
* Pushes the three tables to a Google Sheet for organizers to use during phonebanks  

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
