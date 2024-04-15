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
        username = "username"
        password = "password"
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

def get_tweet_parameters(option):
    while True:
        try:
            number_of_tweets = int(input("How many tweets do you want to retrieve? "))
            if 1 <= number_of_tweets <= 20:  # Check if within range (1 to 20)
                break
            else:
                print("Please enter a number between 1 and 20.")
        except ValueError:
            print("Please enter a number.")

    while True:
        try:
            if option == '1':
                count = int(input(f"How many Topic do you want search? (1-10): "))
            elif option == '2':
                count = int(input(f"How many Username do you want search? (1-10): "))
            
            if 1 <= count <= 10:  # Check if within range (1 to 10)
                break
            else:
                print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Please enter a number.")
    if option == '1':
        search_by=[input(f"Enter topic {i + 1} :") for i in range(count)]
    elif option == '2':
        search_by =[input(f"Enter username {i + 1} : ") for i in range(count)]

    return number_of_tweets, search_by

def get_search_filters(option):
    if option == '1':
        from_account = input("Enter the account username from which you would like to retrieve tweets"
                            "\nLeave this field empty to retrieve tweets from all accounts: ")
    else:
        from_account=None
    def get_integer_or_none(prompt):
        while True:
            value = input(prompt)
            try:
                return int(value) if value else None
            except ValueError:
                if value:  # Check if the input is not empty
                    print("Please enter a number or leave empty.")
                continue  # Restart the loop if invalid input found (non-empty and non-numeric)

    minimum_replies = get_integer_or_none("Enter the minimum replies tweets should have (or leave empty): ")
    minimum_likes = get_integer_or_none("Enter the minimum likes tweets should have (or leave empty): ")
    minimum_retweets = get_integer_or_none("Enter the minimum retweets should have (or leave empty): ")
    min_views = get_integer_or_none("Enter the minimum views should have (or leave empty): ")
    
    if option == '1':
        include_replies = input("Do you want to include replies? (Y/n): ")
        include_replies = include_replies.lower() in ['y', 'yes']
        include_links = input("Do you want to include links? (Y/n): ")
        include_links = include_links.lower() in ['y', 'yes']
        
    if option == '2':
        include_links = False
        include_replies = False

    return from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links,min_views

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
            


def search_tweets(driver, search_by, from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links,number_of_tweets, option,min_views):
    wait = WebDriverWait(driver, 20)
    for topic_name in search_by:
        try:

            search_input = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//input[@data-testid="SearchBox_Search_Input"]')
                )
            )
            search_input.send_keys(Keys.CONTROL + "a",Keys.DELETE)

            # Perform search with filter
            if from_account or minimum_replies or minimum_likes or minimum_retweets or not include_replies or not include_links:
                filters = ""
                if type(minimum_replies)==int:
                    filters += f"min_replies:{minimum_replies} "
                if type(minimum_likes)==int:
                    filters += f"min_faves:{minimum_likes} "
                if type(minimum_retweets)==int:
                    filters += f"min_retweets:{minimum_retweets} "
                if not include_replies:
                    filters += "-filter:replies "
                if not include_links:
                    filters += "-filter:links "
                    
                if from_account:
                    search_input.send_keys(f"from:{from_account} {topic_name} {filters}")
                elif option == '2':
                    search_input.send_keys(f'from:{topic_name} {filters}')
                else:
                    search_input.send_keys(f"{topic_name} {filters}")
            else:
                search_input.send_keys(f"{topic_name}")
            search_input.send_keys(Keys.ENTER)
            time.sleep(3)

            tweet_count = 0
            while True:
                
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                time.sleep(4)
                like_elements = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, '[data-testid="like"]')
                    )
                )
                reposts = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, '[data-testid="retweet"]')
                    )
                )
                
                engagement_elements = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, '[aria-label*="views"]')
                    )
                )
                tweets = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, '//div[@data-testid="tweetText"]')
                    )
                )
                usernames = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, '[data-testid="User-Name"]')
                    )
                )
                replies = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, '[data-testid="reply"]')
                    )
                )
                hrefs = wait.until(
                    EC.presence_of_all_elements_located(
                        (
                            By.CSS_SELECTOR,
                            "[data-testid=User-Name] a[role=link][href*=status]",
                        )
                    )
                )
                # print('checking time')
                times = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, 'time[datetime]')
                        )
                    )
                # print(times)
                print("getting tweets ...")
                # Iterate over usernames and tweets and print them
                
                for username, tweet, like_element, engagement_element, href_element, reply, repost,timee in zip(
                    usernames, tweets, like_elements, engagement_elements, hrefs, replies, reposts,times
                ):
                    
                    # Execute JavaScript to retrieve the innerText property of the tweet element
                    # tweet_text = driver.execute_script('return arguments[0].innerText;', tweet)
                    # print(f"javascript:{tweet_text}\ntext::{tweet.text}")
    
    
                    user_full_name = (
                        username.find_element(By.XPATH, "..").text.strip().rstrip(".")
                    )
                    # Extract the number of likes or default to 0 if not found
                    likes = like_element.get_attribute("aria-label")
                    likess=int(likes.split()[0]) if likes else 0
                    # Extract the number of views/engagement or default to 0 if not found
                    view=engagement_element.get_attribute("aria-label")
                    parts = view.split(", ")
                    views_count = int(parts[-1].split()[0])
                    
                    repliess = reply.get_attribute("aria-label")
                    repliesss = int(repliess.split()[0]) if repliess else 0

                    repost_text = repost.get_attribute("aria-label")
                    repost_value = int(repost_text.split()[0]) if repost_text else 0
                    # print(f"repost: {repost_value} \n replies: {repliesss}")
                    href = href_element.get_attribute("href")
                    
                    time_element = timee.get_attribute('datetime')
                    
                    # print(time_element)
                    twitter_handle = re.search(r'@(\w+)', user_full_name).group()
                    post_id = re.search(r'/status/(\d+)', href).group(1)

                    # print(twitter_handle,'\n',post_id)  
                    
                    if views_count >= min_views:
                        tweet_data = format_tweet_data(post_id,twitter_handle, tweet.text, likess, repost_value, repliesss, views_count, href,time_element,topic_name,option)

                        # Save formatted tweet data
                        if option == '1':
                            save_tweet_data(tweet_data, "tweet_data_topic.json")
                        elif option == '2':
                            save_tweet_data(tweet_data, "tweet_data_username.json")
                        print(tweet_count)
                        tweet_count += 1
                        if tweet_count >= number_of_tweets:
                            break
                    else:
                        print(f"skipped view_count( {views_count} ) is less than {min_views}")
                if tweet_count >= number_of_tweets:
                        break
        except Exception as e:
            print("Error:", e)
    
            

def save_tweet_data(tweet_data, filename):
    with open(filename, "a", encoding="utf-8") as jsonfile:
        json.dump(tweet_data, jsonfile, indent=4, ensure_ascii=False)
        jsonfile.write('\n')

def format_tweet_data(post_id,username, tweet_text, likes, reposts, replies, views, link,time_element,topic_name,option):
    if option == '1':
        search_by="Topic"
    elif option == '2':
        search_by="Username"
    formatted_tweet = {
        "type": search_by,
        "keyword": topic_name,  
        "tweets": [
            {
                "post_id":post_id,
                "Link": link,
                "Tweet": tweet_text,
                "Username": username,
                "date_of_post":time_element,
                "Likes": likes,
                "Reposts": reposts,
                "Replies": replies,
                "Views": views,
                
            }
        ]
    }
    return formatted_tweet

def main():
    
    username, password = get_credentials()
    while True:
        print("\nOPTIONS")
        print("1. Login with credential")
        print("2. Login with cookies")
        print("3. quit")
        log_option = input("Enter your choice: ")
        if log_option == '1':
            break
        elif log_option == '2':
            break
        else:
            return
    while True:
        print("\nOPTIONS")
        print("1. search by topic")
        print("2. search by people")
        print("3. quit")
        option = input("Enter your choice: ")
        
        if option == "1":
            if not username or not password:
                return
            number_of_tweets, search_by=get_tweet_parameters(option)
            from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links,min_views = get_search_filters(option)
            driver = webdriver.Chrome()
            driver.maximize_window()
            if log_option == '1':
                login(driver, username, password)
                cookies = driver.get_cookies()
                save_cookies(cookies, "cookies.json")
            if log_option == '2':
                cookies_filename = "cookies.json"
                try:
                    cookies = load_cookies(cookies_filename)
                    if cookies:
                        driver.get("https://twitter.com/")
                        for cookie in cookies:
                            driver.add_cookie(cookie)
                        driver.get("https://twitter.com/home")
                    else:
                        print("No cookies found.")
                except Exception as e:
                    print(f"Error loading cookies: {e}")
            
            print("searching tweets")
            search_tweets(driver, search_by, from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links,number_of_tweets, option,min_views)
            driver.quit()
        elif option == "2":
            
            if not username or not password:
                return
            
            number_of_tweets, search_by=get_tweet_parameters(option)
            from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links,min_views = get_search_filters(option)
            driver = webdriver.Chrome()
            driver.maximize_window()
            if log_option == '1':
                login(driver, username, password)
                cookies = driver.get_cookies()
                save_cookies(cookies, "cookies.json")
            if log_option == '2':
                cookies_filename = "cookies.json"
                try:
                    cookies = load_cookies(cookies_filename)
                    if cookies:
                        driver.get("https://twitter.com/")
                        for cookie in cookies:
                            driver.add_cookie(cookie)
                        driver.get("https://twitter.com/home")
                    else:
                        print("No cookies found.")
                except Exception as e:
                    print(f"Error loading cookies: {e}")
            
            print("searching tweets")
            search_tweets(driver, search_by, from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links,number_of_tweets, option,min_views)
            driver.quit()
        elif option == "3":
            break

        elif option.lower() == "quit":
            break
       
        break

    driver.quit()

if __name__ == "__main__":
    main()
