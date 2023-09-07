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

        # Load the credentials from the file
        with open(credentials_path, 'r') as f:
            credentials = json.load(f)

        # Load the directory map from the JSON file
        with open('map.json', 'r') as f:
            directory_map = json.load(f)
            landing_pad_dir = directory_map.get('landing_pad')
            roi_links_dir = directory_map.get('roi_links')

        # Set up the Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # GUI off
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Set the default download directory
        prefs = {"download.default_directory": landing_pad_dir}
        chrome_options.add_experimental_option("prefs", prefs)

        # Set up the WebDriver service
        webdriver_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

        # Navigate to the URL
        driver.get(url)

        # Fill in the form
        driver.find_element(By.ID, 'loginuserid').send_keys(credentials['username'])
        driver.find_element(By.ID, 'loginpassword').send_keys(credentials['password'])
        driver.find_element(By.ID, 'loginclient').send_keys(credentials['client_code'])

        # Submit the form
        driver.find_element(By.CSS_SELECTOR, '#frmlogin2 button[type="submit"].btn.btn-default').click()

        # Wait for the download to start
        time.sleep(5)

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
                # If the file is a CSV file and starts with 'NPCA', rename it
                if file.startswith('NPCA') and file.endswith('.csv'):
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

        # Close the browser
        driver.quit()

    except Exception as e:
        print(f"An error occurred: {e}")


def initialize_directories():
    """Loads the directory paths from the map.json file and initializes global variables."""
    global directory_map, roi_links_dir, landing_pad_dir, credentials_path
    try:
        with open('/Users/dbouquin/Library/CloudStorage/OneDrive-NationalParksConservationAssociation/'
                  'General - Data Vault/hackbot_data_vault/map.json', 'r') as f:
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
        time.sleep(1)  # Wait for 1 second before processing the next file


# Run the process_all_links function
initialize_directories()
process_all_links()


#%%
