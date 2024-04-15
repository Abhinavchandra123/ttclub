import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class DiceJobSearchBot:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_extension('./ublock-origin.crx')
        self.options.add_argument("--disable-popup-blocking")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 20)
        self.post_links=[]
        
    def save_cookies(self, cookies, filename):
        with open(filename, 'w') as f:
            json.dump(cookies, f)
            
    def load_cookies(self, filename):
        with open(filename, 'r') as f:
            return json.load(f)
    
    def login_with_cookies(self, cookies):
        self.driver.get("https://www.dice.com/home/home-feed")
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()
        try:
            self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "personal-info-section")))
            print("Login successful. Personal info section is visible.")
            return True
        except TimeoutException:
            print("Login failed. Personal info section is not visible.")
            return False

        
    def login(self, email, password):
        self.driver.get("https://www.dice.com/dashboard/login")
        email_input = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
        password_input = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
        email_input.send_keys(email)
        password_input.send_keys(password)
        login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.btn-lg.btn-block")))
        login_button.click()
        try:
            personal_info_section = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "personal-info-section")))
            print("Login successful. Personal info section is visible.")
            if personal_info_section:
                cookies = self.driver.get_cookies()
                self.save_cookies(cookies, "cookies.json")
        except TimeoutException:
            print("Login failed. Personal info section is not visible.")
            self.quit()
            exit()
        

    def close_sms_popup(self):
        wait = WebDriverWait(self.driver, 5)
        try:
            close_button = wait.until(EC.element_to_be_clickable((By.ID, "sms-remind-me")))
            close_button.click()
            print("SMS pop-up closed successfully")
        except TimeoutException:
            print("Timeout while waiting for SMS pop-up close button")
        except NoSuchElementException:
            print("SMS pop-up not found")

    def search_jobs(self, location, skill):
        # self.driver.get("https://www.dice.com/jobs?q=&l=")
        location_input = self.wait.until(EC.element_to_be_clickable((By.ID, "google-location-search")))
        location_input.clear()
        location_input.send_keys(location)
        skill_input = self.wait.until(EC.element_to_be_clickable((By.ID, "typeaheadInput")))
        # skill_input.send_keys(skill)
        search_button = self.wait.until(EC.element_to_be_clickable((By.ID, "submitSearch-button")))
        search_button.click()

    def get_link_with_easy_apply(self):
        print('getting link of job post')
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cy='posted-date-option'][data-cy-index='3']"))).click()
        time.sleep(10)
        self.driver.execute_script("window.scrollTo(0, 100)")
        time.sleep(4)

        while True:
            search_cards = self.driver.find_elements(By.TAG_NAME, "dhi-search-card")
            print(search_cards)
            for card in search_cards:
                easy_apply_div = card.find_elements(By.CSS_SELECTOR, "div[data-cy='card-easy-apply']")
                if easy_apply_div:
                    card_title = card.find_element(By.CSS_SELECTOR, "a[data-cy='card-title-link']")
                    job_id = card_title.get_attribute("id")
                    if job_id:
                        link = f"https://www.dice.com/job-detail/{job_id}"
                        print("Easy Apply found for post:", link)
                        if link not in self.post_links:
                            print(link)
                            self.post_links.append(link)

            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, "li.pagination-next.page-item")

                if not next_button.get_attribute("class").endswith("disabled"):
                    next_button.click()
                    print("Next button clicked successfully")
                    # Wait for the page to load after clicking Next
                    time.sleep(5)  # Adjust as needed
                else:
                    print("Next button is disabled, exiting loop")
                    break  # Exit the loop if the Next button is disabled
            except NoSuchElementException:
                print("Next button element is not present on the webpage, exiting loop")
                break  # Exit the loop if the Next button element is not found

        print(self.post_links)
    
    def apply_to_jobs(self):
        approved_link=[]
        for post in self.post_links:
            self.driver.get(post)
            
            try:
                time.sleep(6)
                apply_button_wc = self.wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'apply-button-wc')))
                shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', apply_button_wc)
                button_inside_shadow_root = shadow_root.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary')

                self.driver.execute_script("arguments[0].click();", button_inside_shadow_root)
                print("easy apply clicked")

            except Exception as e:
                print("Error clicking on the easy apply button:", e)
                continue
            
            try:
                time.sleep(2)
                next_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-next') and .//span[text()='Next']]")))
                next_button.click()
                time.sleep(2)
                apply_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.btn-next.btn-split")))
                apply_button.click()
                time.sleep(2)
                approved = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "header.post-apply-banner")))
                if approved:
                    approved_link.append(post)
            except Exception as e:
                print("error : ", e)
                continue
        print(f'applied in {approved_link} ')

    def quit(self):
        self.driver.quit()

if __name__ == "__main__":
    bot = DiceJobSearchBot()
    email = "larsenm2020@gmail.com"
    password = "linet1974"
    location = "Bangor"
    skill = "php"
    cookies_filename = "cookies.json"
    try:
        cookies = bot.load_cookies(cookies_filename)
        login=bot.login_with_cookies(cookies)
        if not login:
            print("No cookies found.\n login failed")
           
    except:
        print(f"Error logging in")
        bot.login(email, password)
    
    bot.close_sms_popup()
    bot.search_jobs(location, skill)
    bot.get_link_with_easy_apply()
    bot.apply_to_jobs()
    bot.quit()
