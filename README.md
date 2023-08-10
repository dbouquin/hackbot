# Hackbot 
## If there's a will, there's a way...even if that way is a bit convoluted.

Sometimes the world doesn't want you to have an API, so you have to get creative.   
The Hackbot is here to help you jailbreak ROI files and get them to where you need them to be. It downloads zipped files, unzips them, renames them, and relocates them with the grace you'd expect from a bot built purely out of necessity.

### Setup

#### Before you use the Hackbot, you must do another hacky thing
The Hackbot assumes you have a directory called `/roi_links` containing .txt files populated with download URLs from reports you've scheduled in ROI. To get those .txt files, use Power Automate:   
   
Power Automate extracts your file download URL whenever you receive one in a ROI email – it writes the URL to a .txt file and names the file using the report name (e.g., link_testmachine.txt). Each report needs a separate Power Automate "flow." To make a flow, just copy one of the existing Hackbot flows and update your copy: 

* Rename the flow with your report name (e.g., Hackbot - test machine)
* Change the email subject search to include the name you've given the report (e.g., subject: TESTMACHINE)
	* *Note: do not put spaces in the report name when you schedule it in ROI*
* Change the write file action to name the file with your report name. (e.g., link_testmachine.txt)

More detail about the Power Automate flows used by Hackbot is available here.

Once you've made your edits, turn on the flow (right click it) and you'll be ready to go.  
  
#### Add your report to the map
Now you have your `roi_links/`, but before you can use the Hackbot, you need to *tell the bot where to put your files*. To do this, update the `map.json` file. Use your report name and enter the full path to the directory you want the file to go in. Create a new directory for your files if you need one.  

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

*Note: the .gitignore file in this repo ignores your credenitals file so you won't end up uploading it to GitHub by mistake.*

#### Specify your map.json file's location
The only path that's hardcoded into the main scrip in the path to `map.json`. Open the `main_selenium.py` file and update the `initialize_directories()` function with the file path you're using for your map.

#### Install dependencies

* selenium: This is the main package for web scraping and automation with browser drivers. It provides the webdriver interface, among other tools.
* webdriver_manager: This is a helper utility that can automatically manage browser driver versions for you. 

``````
$ pip install selenium webdriver_manager
``````
The rest of the imports are part of the standard Python library. 

### Run
Now you're ready to roll.   

Open `main_selenium.py` and run it in an IDE or run it via the command line.  

The Hackbot uses Chromium (what the Chrome browser uses) headlessly (no GUI) and enters your credentials in order to initiate a file download from ROI servers. The file downloads faster than you can say "Why isn't there an API for this?" and is placed into the `landing_pad/` where it gets unzipped. Hackbot then renames the file to keep just the "job number" associated with the email you received for that report, plus the report name. The file is then moved to the location you specified. The report name is used to look up the location in the map file.

### Cron job
See `cron_instructions.txt` and use `main_selenium_cron.py`




