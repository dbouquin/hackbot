#!/opt/anaconda3/envs/hackbot/bin/python

from selenium import webdriver
import json
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pickle

#/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --allow-pre-commit-input --disable-background-networking --disable-blink-features=AutomationControlled --disable-client-side-phishing-detection --disable-default-apps --disable-dev-shm-usage --disable-gpu --disable-hang-monitor --disable-popup-blocking --disable-prompt-on-repost --disable-sync --enable-logging --log-level=0 --no-first-run --no-sandbox --no-service-autorun --password-store=basic --remote-debugging-port=9222 --test-type=webdriver --use-mock-keychain --user-data-dir=/Users/dbouquin/Documents/ChromeProfileForSelenium --flag-switches-begin --flag-switches-end

#%%
def initialize_directories():
    """Loads the directory paths from the map.json file and initializes global variables."""
    global directory_map, roi_links_dir, landing_pad_dir, credentials_path
    try:
        with open('/Users/dbouquin/Library/CloudStorage/OneDrive-NationalParksConservationAssociation/Data_Vault/hackbot_data_vault/map.json', 'r') as f:
            directory_map = json.load(f)
            landing_pad_dir = directory_map.get('landing_pad')
            roi_links_dir = directory_map.get('roi_links')
            credentials_path = directory_map.get('credentials')
    except Exception as e:
        raise RuntimeError(f"Failed to initialize directories from map.json: {e}")

#%%
# Web driver
def setup_driver():
    """Sets up and returns a configured Chrome webdriver."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
    return webdriver.Chrome(options=chrome_options)

#%%
# Initial login
def login_once(driver):
    """Perform the login operation once before processing the downloads."""
    try:
        with open(credentials_path, 'r') as f:
            credentials = json.load(f)

        driver.get("https://app.roicrm.net/live")  # Specify the initial login URL
        time.sleep(5)

        # If there is a username field, enter the username and click submit
        if driver.find_elements(By.ID, 'username'):
            driver.find_element(By.ID, 'username').send_keys(credentials['username'])
            driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(5)
        # If there is a password field, enter the password and click submit
        if driver.find_elements(By.NAME, 'passwd'):
            driver.find_element(By.NAME, 'passwd').send_keys(credentials['password'])
            driver.find_element(By.ID, 'idSIButton9').click()
        time.sleep(20)  # Wait for manual interactions if necessary

    except Exception as e:
        print(f"Login error occurred: {e}")

# Save cookies
def save_cookies(driver, location):
    pickle.dump(driver.get_cookies(), open(location, "wb"))

#%%
if __name__ == "__main__":
    initialize_directories()
    driver = setup_driver()
    login_once(driver)
    
