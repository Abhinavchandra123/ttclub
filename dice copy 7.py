import json
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class DiceJobSearchBot:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.post_links=[]
        self.skills=[]
        self.location=None
    def start_driver(self):
        options = webdriver.ChromeOptions()
        options.add_extension('./ublock-origin.crx')
        options.add_argument("--disable-popup-blocking")
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 20)
        
    def take_input(self):
        while True:
            try:
                count = int(input(f"How many job do you want search? (1-10): "))
                if 1 <= count <= 10:  # Check if within range (1 to 10)
                    break
                else:
                    print("Please enter a number between 1 and 10.")
            except ValueError:
                print("Please enter a number.")
                
        for i in range(count):
            self.skills.append(input(f"Enter topic {i + 1}: "))
        self.location=input("Enter the location where you want to work")
        return self.skills
    
    def save_cookies(self, cookies, filename):
        
        existing_cookies = []

        if os.path.exists(filename):
            with open(filename, 'r') as f:
                try:
                    existing_cookies = json.load(f)
                except json.decoder.JSONDecodeError:
                    print('cookies file exist with empty')
                    pass

        existing_cookies.append(cookies)

        with open(filename, 'w') as f:
            print(existing_cookies)
            json.dump(existing_cookies, f)
            
    def load_cookies(self, filename):
        with open(filename, 'r') as f:
            return json.load(f)
    
    def login_with_cookies(self, cookies):
        try:
            self.driver.get("https://www.dice.com/home/home-feed")
            # time.sleep(2)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.driver.refresh()
        except Exception as e:
            print('error: ',e )
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
                # cookies_list=[cookies]
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

    def search_jobs(self,skill):
        # self.driver.get("https://www.dice.com/jobs?q=&l=")
        skill_input = self.wait.until(EC.element_to_be_clickable((By.ID, "typeaheadInput")))
        skill_input.clear()
        skill_input.send_keys(skill)
        location_input = self.wait.until(EC.element_to_be_clickable((By.ID, "google-location-search")))
        location_input.clear()
        location_input.send_keys(self.location)
        
        search_button = self.wait.until(EC.element_to_be_clickable((By.ID, "submitSearch-button")))
        search_button.click()

    def get_link_with_easy_apply(self):
        print('getting link of job post')
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cy='posted-date-option'][data-cy-index='3']"))).click()
        time.sleep(10)
        # self.driver.execute_script("window.scrollTo(0, 100)")
        # time.sleep(4)

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
                        # print("Easy Apply found for post:", link)
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
    
    def handle_alert_popup(self):
        try:
            alert = WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert.accept()
            self.driver.switch_to.default_content()
            print('Alert leave button clicked')
        except Exception as e:
            print("No alert pop up:", e)
    
    def click_easy_apply_button(self):
        try:
            apply_button_wc = self.wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'apply-button-wc')))
            shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', apply_button_wc)
            button_inside_shadow_root = shadow_root.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary')
            self.driver.execute_script("arguments[0].click();", button_inside_shadow_root)
            print("Easy apply clicked")
        except Exception as e:
            print("Error clicking on the easy apply button:", e)
            
    def extract_question_info(self, questions_wrapper):
        question_text = questions_wrapper.find_element(By.TAG_NAME, "h4").text
        print("Question:", question_text)
        
        question_type = "None"
        input_elements = questions_wrapper.find_elements(By.CSS_SELECTOR, "input[type='radio'][value='Yes'], input[type='radio'][value='No']")
        if input_elements:
            print("This question has yes or no inputs")
            if len(input_elements) == 2:
                print("This question is a yes or no radio button question")
                question_type = 'radio button y/n'
        else:
            print("This question does not have yes or no inputs")
        
        return question_text, question_type
    
    def update_question_answer_file(self, question_text, question_type):
        filename = 'question_answer.json'
        question_answer = []
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                try:
                    question_answer = json.load(f)
                    # Check if a question with the same type exists
                    question_exists = any(qa['question'] == question_text and qa['type'] == question_type for qa in question_answer)
                    if not question_exists:
                        question_answer.append({"question": question_text, "answer": "None", 'type': question_type})
                except json.decoder.JSONDecodeError:
                    print(f'{filename} exist with empty')
                    pass
        else:
            question_answer = [{"question": question_text, "answer": "None", 'type': question_type}]

        with open(filename, 'w') as f:
            print(question_answer)
            json.dump(question_answer, f, indent=4)


    def process_questions(self):
        try:
            time.sleep(2)
            next_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-next') and .//span[text()='Next']]")))
            next_button.click()
            time.sleep(2)
            questions_wrapper = self.driver.find_element(By.CSS_SELECTOR, "div.questions-wrapper")
            if questions_wrapper:
                question_text, question_type = self.extract_question_info(questions_wrapper)
                
                self.update_question_answer_file(question_text, question_type)
                
                self.process_question(question_text, question_type)
                
                # answer = "None"
                # question_type= "None"
                # filename='question_answer.json'
                # question = questions_wrapper.find_element(By.TAG_NAME, "h4").text
                # print("Question:", question)
                # try:
                    # input_elements = questions_wrapper.find_elements(By.CSS_SELECTOR, "input[type='radio'][value='Yes'], input[type='radio'][value='No']")
                    # print('input radio found')
                    # if input_elements:
                        # print("This question has yes or no inputs")
                        # if len(input_elements) == 2:
                            # print("This question is a yes or no radio button question")
                            # question_type = 'radio button y/n'
                    # else:
                        # print("This question does not have yes or no inputs")
                # except:
                    # print('no input found')
                if os.path.exists(filename):
                    with open(filename, 'r') as f:
                        try:
                            question_answer = json.load(f)
                            # Check if a question with the same type exists
                            question_exists = any(qa['question'] == question and qa['type'] == question_type for qa in question_answer)
                            if not question_exists:
                                question_answer.append({"question": question, "answer": answer, 'type':question_type})
                        except json.decoder.JSONDecodeError:
                            print('cookies file exist with empty')
                            pass
                else:
                    question_answer = [{"question": question, "answer": answer, 'type':question_type}]

                with open(filename, 'w') as f:
                    print(question_answer)
                    json.dump(question_answer, f, indent=4)
                    
                    
                if os.path.exists(filename):
                    with open(filename, 'r') as f:
                        try:
                            question_answer = json.load(f)
                            for qa in question_answer:
                                if qa['question'] == question and qa['answer'] != "None" and qa['type'] != "None":
                                    answer = qa['answer']
                                    break
                                
                                if answer != "None":
                                    if question_type == 'radio button y/n':
                                        if answer == 'yes':
                                            input_yes_radio = questions_wrapper.find_elements(By.CSS_SELECTOR, "input[type='radio'][value='Yes']")
                                            input_yes_radio.click()
                                        if answer == 'no':
                                            input_no_radio = questions_wrapper.find_elements(By.CSS_SELECTOR, "input[type='radio'][value='No']")
                                            input_no_radio.click()
                                
                        except json.decoder.JSONDecodeError:
                            print('cookies file exist with empty')
                            pass
                
                # Process question based on question type
                
                # Load and update question_answer file
                
        except Exception as e:
            print("Error processing questions:", e)
    
    def apply_to_individual_job(self, post):
        try:
            self.driver.get(post)
            self.handle_alert_popup()
            self.click_easy_apply_button()
            self.process_questions()
            # Continue with the remaining steps for applying to the job
            
        except Exception as e:
            print("Error applying to individual job:", e)
        
    def apply_to_jobs(self):
        approved_link=[]
        for post in self.post_links:
            self.apply_to_individual_job(post)
            
            # self.driver.get(post)
            # try:
            #     alert = WebDriverWait(self.driver, 5).until(EC.alert_is_present())

            #     # Switch to the alert
            #     alert = self.driver.switch_to.alert

            #     # Accept the alert (click leave button)
            #     alert.accept()
            #     self.driver.switch_to.default_content()
            #     print('alert leave button clicked')
            # except Exception as e:
            #     print("No alert pop up:", e)
            #     continue    
            
            # try:
            #     time.sleep(6)
            #     apply_button_wc = self.wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'apply-button-wc')))
            #     shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', apply_button_wc)
            #     button_inside_shadow_root = shadow_root.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary')

            #     self.driver.execute_script("arguments[0].click();", button_inside_shadow_root)
            #     print("easy apply clicked")

            # except Exception as e:
            #     print("Error clicking on the easy apply button:", e)
            #     continue
            question_answer=[]
            try:
                time.sleep(2)
                next_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-next') and .//span[text()='Next']]")))
                next_button.click()
                time.sleep(2)
                questions_wrapper = self.driver.find_element(By.CSS_SELECTOR, "div.questions-wrapper")
    
                if questions_wrapper:
                    answer = "None"
                    question_type= "None"
                    filename='question_answer.json'
                    # Extract the question from the h4 tag inside the questions wrapper
                    question = questions_wrapper.find_element(By.TAG_NAME, "h4").text
                    print("Question:", question)
                    input_elements = questions_wrapper.find_elements(By.CSS_SELECTOR, "input[type='radio'][value='Yes'], input[type='radio'][value='No']")
                    if input_elements:
                        print("This question has yes or no inputs")
                        # Determine if the question is a yes or no radio button question
                        if len(input_elements) == 2:
                            print("This question is a yes or no radio button question")
                            question_type = 'radio button y/n'
                            # Process further as needed
                        else:
                            print("This question does not have exactly two radio button inputs (Yes and No)")
                    else:
                        print("This question does not have yes or no inputs")

                    if os.path.exists(filename):
                        with open(filename, 'r') as f:
                            try:
                                question_answer = json.load(f)
                                for qa in question_answer:
                                    if qa['question'] == question and qa['answer'] != answer and qa['type'] != question_type:
                                        answer = qa['answer']
                                        break
                                    
                                    if answer != "None":
                                        if question_type == 'radio button y/n':
                                            if answer == 'yes':
                                                input_yes_radio = questions_wrapper.find_elements(By.CSS_SELECTOR, "input[type='radio'][value='Yes']")
                                                input_yes_radio.click()
                                            if answer == 'no':
                                                input_no_radio = questions_wrapper.find_elements(By.CSS_SELECTOR, "input[type='radio'][value='No']")
                                                input_no_radio.click()
                                    
                            except json.decoder.JSONDecodeError:
                                print('cookies file exist with empty')
                                pass

                    question_answer.append({"question": question, "answer": answer, 'type':question_type})

                    with open(filename, 'w') as f:
                        print(question_answer)
                        json.dump(question_answer, f, indent=4) 
                    
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
    location = "Bangalore"
    skill = "php"
    cookies_filename = "cookies.json"
    
    skills=bot.take_input()
    print(skills)
    bot.start_driver()
    try:
        cookies_list = bot.load_cookies(cookies_filename)
        if len(cookies_list) <= 4:
            bot.login(email, password)
        # print('list',cookies_list)
        cookies=random.choice(cookies_list)
        print(cookies)
        login=bot.login_with_cookies(cookies)
        if not login:
            print("No cookies found.\n login failed")
           
    except:
        print(f"Error logging in")
        bot.login(email, password)
    
    bot.close_sms_popup()
    for skill in skills:
        print(skill)
        bot.search_jobs(skill)
        bot.get_link_with_easy_apply()
    bot.apply_to_jobs()
    bot.quit()
