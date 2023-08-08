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
def main():
    try:
        # Load the URL from the file
        with open('link.txt', 'r') as f:
            url = f.read().strip()

        # Load the credentials from the file
        with open('credentials.json', 'r') as f:
            credentials = json.load(f)

        # Load the job number from the file
        with open('job.txt', 'r') as f:
            job_number = f.read().strip()

        # Load the directory map from the JSON file
        with open('map.json', 'r') as f:
            directory_map = json.load(f)

        # Set up the Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # GUI off
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Set the default download directory
        prefs = {"download.default_directory": "/Users/dbouquin/OneDrive/Documents_Daina/hackbot/landing_pad"}
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
        downloaded_file = get_latest_file_in_directory('/Users/dbouquin/OneDrive/Documents_Daina/hackbot/landing_pad')

        # If the downloaded file is a ZIP file and contains the job number, unzip it
        if downloaded_file and downloaded_file.endswith('.ZIP') and job_number in downloaded_file:
            unzip_file(
                os.path.join('/Users/dbouquin/OneDrive/Documents_Daina/hackbot/landing_pad', downloaded_file),
                '/Users/dbouquin/OneDrive/Documents_Daina/hackbot/landing_pad'
            )

            # Loop through all the files in the download directory
            for file in os.listdir('/Users/dbouquin/OneDrive/Documents_Daina/hackbot/landing_pad'):
                # If the file is a CSV file and starts with 'NPCA', rename it
                if file.startswith('NPCA') and file.endswith('.csv'):
                    # Split the filename into the prefix and the rest
                    prefix, rest_of_filename = file.split('NPCA_JOB', 1)

                    # Only rename files where the job number in the file matches the job number we're looking for
                    job_number_in_file = rest_of_filename.split('_', 1)[0]
                    if job_number_in_file == job_number:
                        new_filename = rest_of_filename
                        os.rename(
                            os.path.join('/Users/dbouquin/OneDrive/Documents_Daina/hackbot/landing_pad', file),
                            os.path.join('/Users/dbouquin/OneDrive/Documents_Daina/hackbot/landing_pad', new_filename)
                        )

                        # Move the file to the correct directory based on its name
                        for keyword, directory in directory_map.items():
                            if keyword in new_filename.upper():
                                shutil.move(
                                    os.path.join('/Users/dbouquin/OneDrive/Documents_Daina/hackbot/landing_pad', new_filename),
                                    os.path.join(directory, new_filename)
                                )
                                break

            # Remove the original ZIP file
            os.remove(
                os.path.join(
                    '/Users/dbouquin/OneDrive/Documents_Daina/hackbot/landing_pad', downloaded_file
                )
            )

            # Remove all .txt files
            for file in os.listdir('/Users/dbouquin/OneDrive/Documents_Daina/hackbot/landing_pad'):
                if file.endswith('.TXT'):
                    os.remove(os.path.join('/Users/dbouquin/OneDrive/Documents_Daina/hackbot/landing_pad', file))

        # Close the browser
        driver.quit()

    except Exception as e:
        print(f"An error occurred: {e}")

# Run the main function
main()

#%%
