#!/opt/anaconda3/envs/hackbot/bin/python

import os

# Set the current working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import zipfile
import os
import time
import shutil
from datetime import datetime

# Function to get the latest file in a directory
def get_latest_file_in_directory(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)))
    return files[-1] if files else None


# Function to unzip a file
def unzip_file(zip_filepath, dest_dir):
    with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)

# Main function
def main(link_file_path):
    try:
        # Load the URL from the file
        with open(link_file_path, 'r') as f:
            url = f.read().strip()

        # Replace old url start with "app.roicrm.net/live"
        url = url.replace("secure2.roisolutions.net/enterprise", "app.roicrm.net/live")

        # Load the credentials from the file
        with open(credentials_path, 'r') as f:
            credentials = json.load(f)

        # Load the directory map from the JSON file
        with open('map.json', 'r') as f:
            directory_map = json.load(f)
            landing_pad_dir = directory_map.get('landing_pad')
            roi_links_dir = directory_map.get('roi_links')

        # Set up the Chrome options
        chrome_options = webdriver.ChromeOptions()
        # This will save the cookies
        chrome_options.add_argument("user-data-dir=/Users/dbouquin/Library/Application Support/Google/Chrome/Profile 7") 
        #chrome_options.add_argument("--headless")  # GUI off
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument('--disable-gpu') 
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # Set the default download directory
        prefs = {"download.default_directory": landing_pad_dir,
                 "download.prompt_for_download": False,
                 "useAutomationExtension": False}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # Set up the WebDriver service
        webdriver_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

        # Navigate to the URL
        driver.get(url)

        # Sleep 
        time.sleep(10)

        # Click continue when shown notice about new login screen - only be required once if cookies are saved
        #driver.find_element(By.CSS_SELECTOR, '#frmlogin2 button[onclick="persistskip();auth0login();"].btn.btn-default').click()
        
        # Enter the email 
        driver.find_element(By.ID, 'username').send_keys(credentials['username'])

        # Click "continue" where button type is submit
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Wait for the page to load
        time.sleep(10)

        # Enter the password 
        driver.find_element(By.NAME, 'passwd').send_keys(credentials['password'])

        # Click to submit
        driver.find_element(By.ID, 'idSIButton9').click()

        # Wait for the page to load and allow user to manually enter code
        time.sleep(60)

        # Wait for the download to finish
        # If downloaded file is associated with a text file in dop_files wait 20 seconds, else wait 5 seconds
        large_files = ['link_allaccountsandinfo.txt', 'link_alltransactions.txt', 'link_transactionswsolicitors.txt', 'link_accountflagssincefy18.txt']

        if any(large_file in link_file_path for large_file in large_files):
            time.sleep(10)
        else:
            time.sleep(5)

        # Check for '.crdownload' files and wait until download completes
        while any('.crdownload' in f for f in os.listdir(landing_pad_dir)):
            #print("Download in progress, waiting for 10 more seconds...")
            time.sleep(10)

        # Get the name of the latest file in the download directory
        downloaded_file = get_latest_file_in_directory(landing_pad_dir)

        # If the downloaded file is a ZIP file, unzip it
        if downloaded_file and downloaded_file.lower().endswith('.zip'):
            unzip_file(
                os.path.join(landing_pad_dir, downloaded_file),
                landing_pad_dir
            )

            # Loop through all the files in the download directory
            for file in os.listdir(landing_pad_dir):
                # Initialize new_filename as None
                new_filename = None

                # check for dop_files
                dop_files = ['HTACTIVITIES', 'MGRATINGS', 'PLANNEDGIFTS', 'EVENTSANDATTENDEESSINCEFY19',
                             'PLEDGES', 'PLEDGE_SCHEDULE', 'PROPOSALS',
                             'ACCOUNTFLAGSSINCEFY18', 'RELATIONSHIPMANAGERASSIGNMENTS', 'TRANSACTIONSWSOLICITORS',
                             'ALLTRANSACTIONS', 'ALLACCOUNTSANDINFO', 'FIRSTGIFTSALL']

                if any(dop_file in file for dop_file in dop_files) and file.endswith('.csv'):
                    today_date = datetime.now().strftime("%Y%m%d")
                    new_filename = f"{today_date}_{file}"
                    # strip "NPCA_JOB" from filename
                    new_filename = new_filename.replace('NPCA_JOB', '')

                # If the file is a CSV file and starts with 'NPCA', rename it
                elif file.startswith('NPCA') and file.endswith('.csv'):
                    prefix, rest_of_filename = file.split('NPCA_JOB', 1)
                    new_filename = rest_of_filename

                # Check if file contains "QTool" and ends with .csv
                elif "QTool" in file and file.endswith('.csv'):
                    today_date = datetime.now().strftime("%Y%m%d")
                    new_filename = f"{today_date}_WEALTHSCREENING.csv"

                else:
                    continue

                # Rename the file
                os.rename(
                    os.path.join(landing_pad_dir, file),
                    os.path.join(landing_pad_dir, new_filename)
                )

                # Move the file to the correct directory based on its name
                for keyword, directory in directory_map.items():
                    if keyword in new_filename.upper():
                        shutil.move(
                            os.path.join(landing_pad_dir, new_filename),
                            os.path.join(directory, new_filename)
                        )
                        break

            # Remove the original ZIP file
            os.remove(
                os.path.join(
                    landing_pad_dir, downloaded_file
                )
            )

            # Remove all .txt files
            for file in os.listdir(landing_pad_dir):
                if file.endswith('.TXT'):
                    os.remove(os.path.join(landing_pad_dir, file))

        elif "FoundationsReport" in downloaded_file:
            today_date = datetime.now().strftime("%Y%m%d")
            new_filename = f"{today_date}_FOUNDATIONSREPORT.csv"
            
            # Rename the file
            os.rename(
                os.path.join(landing_pad_dir, downloaded_file),
                os.path.join(landing_pad_dir, new_filename)
            )

            # Move the file to the correct directory based on its name
            for keyword, directory in directory_map.items():
                if keyword in new_filename.upper():
                    shutil.move(
                        os.path.join(landing_pad_dir, new_filename),
                        os.path.join(directory, new_filename)
                    )
                    break
            # Make a copy of the file with a static name
            static_name = "FOUNDATIONSREPORT_CURRENT.csv"
            shutil.copy2(
                os.path.join(directory, new_filename),
                os.path.join(directory, static_name)
            )

        # Close the browser
        driver.quit()

    except Exception as e:
        print(f"An error occurred: {e}")


def initialize_directories():
    """Loads the directory paths from the map.json file and initializes global variables."""
    global directory_map, roi_links_dir, landing_pad_dir, credentials_path
    try:
        with open('/Users/dbouquin/Library/CloudStorage/OneDrive-NationalParksConservationAssociation/'
                  'Data_Vault/hackbot_data_vault/map.json', 'r') as f:
            directory_map = json.load(f)
            landing_pad_dir = directory_map.get('landing_pad')
            roi_links_dir = directory_map.get('roi_links')
            credentials_path = directory_map.get('credentials')
    except Exception as e:
        raise RuntimeError(f"Failed to initialize directories from map.json: {e}")


# Process all the files in the roi_links directory
def process_all_links():
    # Get a list of all .txt files in the roi_links/ directory
    link_files = [f for f in os.listdir(roi_links_dir) if f.endswith('.txt')]

    # Loop through each link file and call the main() function
    for link_file in link_files:
        main(os.path.join(roi_links_dir, link_file))
        time.sleep(60)  # Wait 60 seconds before processing the next file - let OneDrive sync


# Run the process_all_links function
initialize_directories()
process_all_links()


#%%
