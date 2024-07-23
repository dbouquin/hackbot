# Hackbot 
## If there's a will, there's a way...even if that way is a bit convoluted.

Sometimes the world doesn't want you to have an API, so you have to get creative.   
The Hackbot is here to help you jailbreak ROI CRM files and get them to where you need them to be. It downloads zipped files, unzips them, renames them, and relocates them with the grace you'd expect from a bot built purely out of necessity.

### Setup

#### Before you use the Hackbot, you must do another hacky thing
The Hackbot assumes you have a directory called `/roi_links` containing .txt files populated with download URLs from reports you've scheduled in ROI. To get those .txt files, use Power Automate:   
   
Power Automate extracts your file download URL whenever you receive one in a ROI email – it writes the URL to a .txt file and names the file using the report name (e.g., link_testmachine.txt). Each report needs a separate Power Automate "flow." To make a flow, just copy one of the existing Hackbot flows and update your copy: 

* Rename the flow with your report name (e.g., Hackbot - test machine)
* Change the email subject search to include the name you've given the report (e.g., subject: TESTMACHINE)
	* *Note: do not put spaces in the report name when you schedule it in ROI*
* Change the write file action to name the file with your report name. (e.g., link_testmachine.txt)

More detail about the Power Automate flows used by Hackbot is available [here](https://npcaweb.sharepoint.com/:fl:/r/contentstorage/CSP_74a50e21-42fe-4099-b810-9dae767be62f/Document%20Library/LoopAppData/Hackbot.loop?d=w12797ddf754d4de79c6c34b087644b49&csf=1&web=1&e=SeBy5v&nav=cz0lMkZjb250ZW50c3RvcmFnZSUyRkNTUF83NGE1MGUyMS00MmZlLTQwOTktYjgxMC05ZGFlNzY3YmU2MmYmZD1iJTIxSVE2bGRQNUNtVUM0RUoydWRudm1MOTN6eFpRTHhxcEFsaV9IckRFdk1PTVlUQ3RqbzByTlRvTE90WWJIU1pxUyZmPTAxTUU3NDQzNjdQVjRSRVRMVjQ1R1pZM0JVV0NEV0lTMkomYz0lMkYmYT1Mb29wQXBwJnA9JTQwZmx1aWR4JTJGbG9vcC1wYWdlLWNvbnRhaW5lciZ4PSU3QiUyMnclMjIlM0ElMjJUMFJUVUh4dWNHTmhkMlZpTG5Ob1lYSmxjRzlwYm5RdVkyOXRmR0loU1ZFMmJHUlFOVU50VlVNMFJVb3lkV1J1ZG0xTU9UTjZlRnBSVEhoeGNFRnNhVjlJY2tSRmRrMVBUVmxVUTNScWJ6QnlUbFJ2VEU5MFdXSklVMXB4VTN3d01VMUZOelEwTXpKVVZrOUdOMFpQTlZkTFFraEpUMFpJTlU5UFQxVXlOVEpJJTIyJTJDJTIyaSUyMiUzQSUyMjMxNzdhNzc2LTIyNTctNDUzYS04YjM3LWUyNGZiMGE1ZTljZSUyMiU3RA%3D%3D).

Once you've made your edits, turn on the flow (right click it) and you'll be ready to go.  
  
#### Add your report to the map
Now you have your `roi_links/`, but before you can use the Hackbot, you need to *tell the bot where to put your files*. To do this, update the [`map.json`](https://github.com/dbouquin/hackbot/blob/main/map.json) file. Use your report name and enter the full path to the directory you want the file to go in. Create a new directory for your files if you need one.  

````
{
    "TESTMACHINE": "/Users/dbouquin/OneDrive/Documents_Daina/hackbot/files_test_machine",
    "OTHERMACHINE": "/Users/dbouquin/OneDrive/Documents_Daina/hackbot/files_other_machine",
    "landing_pad": "/Users/dbouquin/OneDrive/Documents_Daina/hackbot/landing_pad",
    "roi_links": "/Users/dbouquin/OneDrive/Documents_Daina/hackbot/roi_links",
    "credentials": "/Users/dbouquin/OneDrive/Documents_Daina/hackbot/credentials.json"
}
````

#### Add your ROI credentials
Create a file called `credentials.json`. In this file, create a JSON array and fill in your ROI credentials:

`````
{
"username": "<username here>",
"password": "<password here>",
"client_code": "NPCA"
}

`````
Once you have saved your credentials file, **update the credentials path specified in the `map.json` file**.  

*Note: the [.gitignore](https://github.com/dbouquin/hackbot/blob/main/.gitignore) file in this repo ignores your credenitals file so you won't end up uploading it to GitHub by mistake.*

Alternatively, you can use the [1Password CLI](https://developer.1password.com/docs/cli/).

#### Specify your map.json file's location
The only path that's hardcoded into the main script is the path to `map.json`. Open the `mfa_cronjob_open_window.py` file and update the `initialize_directories()` function with the file path you're using for your map.

#### Install dependencies

* selenium: This is the main package for web scraping and automation with browser drivers. It provides the webdriver interface, among other tools.
* webdriver_manager: This is a helper utility that can automatically manage browser driver versions for you. 

``````
$ pip install selenium webdriver_manager
``````
The rest of the imports are part of the standard Python library. 

### Update due to MFA requirements - using a specific Chrome profile
Create a directory where you want to store preferences for a Hackbot-specific Chrome profile (e.g., `/Users/your_username/Documents/ChromeProfileForSelenium`)

Run this in the terminal to set up the Chrome profile:
`/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --user-data-dir=/Users/your_username/Documents/ChromeProfileForSelenium`

Once the new browser window launches, go to Chrome > Settings and update the download directory to be the `landing_pad` directory.

Then run this in the terminal:

`/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --allow-pre-commit-input --disable-background-networking --disable-blink-features=AutomationControlled --disable-client-side-phishing-detection --disable-default-apps --disable-dev-shm-usage --disable-gpu --disable-hang-monitor --disable-popup-blocking --disable-prompt-on-repost --disable-sync --enable-logging --log-level=0 --no-first-run --no-sandbox --no-service-autorun --password-store=basic --remote-debugging-port=9222 --test-type=webdriver --use-mock-keychain --user-data-dir=/Users/dbouquin/Documents/ChromeProfileForSelenium --flag-switches-begin --flag-switches-end`

Leave this window open.

### Run
Now you're ready to roll.   

Run `mfa_cronjob_open_window.py` in an IDE, via the command line, or use cron.  

The Hackbot uses Chrome and enters your credentials in order to initiate a file download from ROI servers. The file downloads faster than you can say "Why isn't there an API for this?" and is placed into the `landing_pad/` where it gets unzipped. Hackbot then renames the file to keep just the "job number" associated with the email you received for that report (or the date if needed), plus the report name. The file is then moved to the location you specified. The report name is used to look up the location in the map file.

The first time the script runs you will be prompted for your MFA code.




