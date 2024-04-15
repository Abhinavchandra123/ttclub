import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException,TimeoutException
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
        
    def save_cookies(self,cookies, filename):
        with open(self,filename, 'w') as f:
            json.dump(cookies, f)
    def load_cookies(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    def login_with_cookies(self,cookies):
        self.driver.get("https://www.dice.com/")
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh
        
    def login(self, email, password):
        self.driver.get("https://www.dice.com/dashboard/login")
        email_input = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
        password_input = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
        email_input.send_keys(email)
        password_input.send_keys(password)
        login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.btn-lg.btn-block")))
        login_button.click()
        time.sleep(10)
        cookies = self.driver.get_cookies()
        self.save_cookies(cookies, "cookies.json")

    def close_sms_popup(self):
        try:
            close_button = self.wait.until(EC.element_to_be_clickable((By.ID, "sms-remind-me")))
            close_button.click()
            print("SMS pop-up closed successfully")
        except TimeoutException:
            print("Timeout while waiting for SMS pop-up close button")
        except NoSuchElementException:
            print("SMS pop-up not found")

    def search_jobs(self, location, skill):
        location_input = self.wait.until(EC.element_to_be_clickable((By.ID, "google-location-search")))
        location_input.clear()
        location_input.send_keys(location)
        skill_input = self.wait.until(EC.element_to_be_clickable((By.ID, "typeaheadInput")))
        skill_input.send_keys(skill)
        search_button = self.wait.until(EC.element_to_be_clickable((By.ID, "submitSearch-button")))
        search_button.click()

    def get_link_with_easy_apply(self):
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cy='posted-date-option'][data-cy-index='2']"))).click()
        time.sleep(8)
        search_cards = self.driver.find_elements(By.TAG_NAME, "dhi-search-card")
        for card in search_cards:
            
            easy_apply_div = card.find_elements(By.CSS_SELECTOR, "div[data-cy='card-easy-apply']")
            
           
            if easy_apply_div:
                card_title = card.find_element(By.CSS_SELECTOR, "a[data-cy='card-title-link']")
                job_id = card_title.get_attribute("id")
                if job_id:
                    link = f"https://www.dice.com/job-detail/{job_id}"
                    print("Easy Apply found for post:", link)
                if link not in self.post_links:
                    self.post_links.append(link)
        print(self.post_links)
    
    def apply_to_jobs(self):
        for post in self.post_links:
            self.driver.get(post)
            # time.sleep(10)
            try:
                apply_button_wc = self.wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'apply-button-wc')))
                shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', apply_button_wc)
                button_inside_shadow_root = shadow_root.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary')
                if "Easy Apply" in button_inside_shadow_root.text:
                    self.driver.execute_script("arguments[0].click();", button_inside_shadow_root)
                    print("easy apply clicked")
                else:
                    print("Button does not contain 'Easy Apply' text")
                    continue
            except NoSuchElementException as e:
                print("Error clicking on the easy apply button:", e)
                continue
            except TimeoutException as e:
                print("Timeout while waiting for easy apply button: ",e)
                continue
            
            try:
                next_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.btn-next.btn-block")))
                next_button.click()

                apply_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.btn-next.btn-split")))
                apply_button.click()
            except NoSuchElementException:
                print("clicked next button")
                continue
            self.driver.close()
            time.sleep(5)  

    def quit(self):
        self.driver.quit()

if __name__ == "__main__":
    bot = DiceJobSearchBot()
    email = "larsenm2020@gmail.com"
    password = "linet1974"
    location = "Bangalore"
    skill = "Django"
    cookies_filename = "cookies.json"
    try:
        cookies = bot.load_cookies(cookies_filename)
        if cookies:
           bot.login_with_cookies(cookies)
        else:
            print("No cookies found.")
            bot.login(email, password)
    except Exception as e:
        print(f"Error logging in : {e}")
    
    
    bot.close_sms_popup()
    bot.search_jobs(location, skill)
    bot.get_link_with_easy_apply()
    bot.apply_to_jobs()
    bot.quit()
