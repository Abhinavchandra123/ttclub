from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = webdriver.ChromeOptions()
options.add_extension('./ublock-origin.crx')
options.add_argument("--disable-popup-blocking")
driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.get("https://www.dice.com/dashboard/login")

wait = WebDriverWait(driver, 20)

email = "larsenm2020@gmail.com"
password = "linet1974"

email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))

email_input.send_keys(email)
password_input.send_keys(password)

login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.btn-lg.btn-block")))
login_button.click()

try:
    # close_button = wait.until(EC.element_to_be_clickable((By.ID, "sms-remind-me")))
    # close_button.click()
    print("SMS pop-up closed successfully")
except NoSuchElementException:
    print("SMS pop-up not found")

if driver.current_url == "https://www.dice.com/home/home-feed":
    print("Login successful")

location_input = wait.until(EC.element_to_be_clickable((By.ID, "google-location-search")))
location_input.clear()
location = "Bangalore"
location_input.send_keys(location)

skill_input = wait.until(EC.element_to_be_clickable((By.ID, "typeaheadInput")))
skill = "Django"
skill_input.send_keys(skill)

search_button = wait.until(EC.element_to_be_clickable((By.ID, "submitSearch-button")))
search_button.click()

wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cy='posted-date-option'][data-cy-index='2']"))).click()
time.sleep(15)

# Iterate through each job post and apply
posts = driver.find_elements(By.CLASS_NAME, "card-title-link")

for post in posts:
    try:
        post.click()
        print("Link clicked")
    except NoSuchElementException as e:
        print("Error clicking on the card title:", e)
        continue

    time.sleep(10)
    driver.switch_to.window(driver.window_handles[1])

    # time.sleep(10)
    try:
        time.sleep(10)
        # easy_apply = driver.find_element(By.CLASS_NAME, "btn-group btn-group--block")
        apply_button_wc = driver.find_element(By.TAG_NAME, 'apply-button-wc')

        # Get the shadow root
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', apply_button_wc)

        button_inside_shadow_root = shadow_root.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary')

        # Click the button using JavaScript
        driver.execute_script("arguments[0].click();", button_inside_shadow_root)
        print("easy apply clicked")
    except NoSuchElementException:
        print("Easy apply button not found for this job post.")
        continue
    # driver.close()
    # driver.switch_to.window(driver.window_handles[0])

    next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.btn-next.btn-block")))
    next_button.click()

    apply_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.btn-next.btn-split")))
    apply_button.click()

    # Add more actions here if needed after applying

    # Go back to the search results page
    driver.close()
    time.sleep(5)  # Add some delay for stability

driver.quit()
