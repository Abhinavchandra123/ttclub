import csv
import json
import re
import time
from decouple import config
# from spellchecker import SpellChecker

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_credentials():
    try:
        username = "aa30424@gmail.com"
        password = "abhinav1708580"
    except Exception as e:
        print(f"Make sure username and password are added to .env file.\nError: {e}")
        return None, None
    return username, password

# Save cookies to a JSON file
def save_cookies(cookies, filename):
    with open(filename, 'w') as f:
        json.dump(cookies, f)

# Load cookies from a JSON file
def load_cookies(filename):
    with open(filename, 'r') as f:
        return json.load(f)


def login(driver, username, password):
    driver.get("https://twitter.com/login")
    driver.maximize_window()

    wait = WebDriverWait(driver, 10)

    username_input = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, '//input[@autocomplete="username"]')
        )
    )
    username_input.send_keys(username)
    username_input.send_keys(Keys.ENTER)
    print("username entered")
    try:
        phone_or_username_element = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, '//span[contains(text(), "Enter your phone number or username")]')
            )
        )
        print("Login failed. Please enter your phone number or username.")
        if phone_or_username_element:
            # Find input field and enter username
            username_input_field = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//input[@data-testid="ocfEnterTextTextInput"]')
                )
            )
            user=input("enter username or phone number")
            username_input_field.send_keys(user)
            username_input_field.send_keys(Keys.ENTER)
            print("Username entered again")
            
    except:
        print("CHECKING FOR PASSWORD FIELD")
            

    password_input = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, '//input[@autocomplete="current-password"]')
        )
    )
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    print("password entered")
    time.sleep(3)

    if "https://twitter.com/home" in driver.current_url:
        print("Login successful!")

        
    else:
        try:
            phone_or_username_element = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//span[contains(text(), "Enter your phone number or username")]')
                )
            )
            print("Login failed. Please enter your phone number or username.")
            if phone_or_username_element:
                # Find input field and enter username
                username_input_field = wait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//input[@data-testid="ocfEnterTextTextInput"]')
                    )
                )
                user=input("enter username or phone number")
                username_input_field.send_keys(user)
                username_input_field.send_keys(Keys.ENTER)
                print("Username entered again")
                
        except:
            print("Login failed.")
            
username, password = get_credentials()       
while True:
    print("OPTIONS")
    print("1. search by topic")
    print("2. search by people")
    print("3. quit")
    option = input("Enter your choice: ")

    if option == "1":
        if not username or not password:
            break
        driver = webdriver.Chrome()
        login(driver, username, password)
        cookies = driver.get_cookies()
        save_cookies(cookies, "cookies.json")
        driver.quit()
    elif option == "2":
        driver = webdriver.Chrome()
        # Load Twitter with stored cookies
        cookies = load_cookies("cookies.json")
        driver.get("https://twitter.com/")
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.get("https://twitter.com/home")
    elif option == "3":
        import datetime
        expiry_timestamp = 1746607860
        expiry_date = datetime.datetime.utcfromtimestamp(expiry_timestamp)
        print("Expiry Date:", expiry_date)
        # driver.quit()
        break


