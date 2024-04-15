import csv
import json
import os
import random
import re
import time
from decouple import config
# from spellchecker import SpellChecker

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from itertools import zip_longest

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
        json.dump(existing_cookies, f, indent=4) 

def load_cookies(filename):
    try:
        with open(filename, 'r') as f:
            cookies_list = json.load(f)
        if cookies_list:  # Check if the list is not empty
            return random.choice(cookies_list)
        else:
            return None  # Return None if the list is empty
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None

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
                return int(value) if value else 0
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
        include_links = True
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
            
def wait_for_elements(driver, selector, strategy=By.CSS_SELECTOR):
    
    wait = WebDriverWait(driver, 10)
    

    return wait.until(EC.presence_of_all_elements_located((strategy, selector)))
  

def perform_search(driver, option, topic_name, search_by, from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links):
    wait = WebDriverWait(driver, 10)
    search_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@data-testid="SearchBox_Search_Input"]')))
    search_input.send_keys(Keys.CONTROL + "a",Keys.DELETE)

    # Perform search with filter
    if search_by or from_account or minimum_replies or minimum_likes or minimum_retweets or not include_replies or not include_links:
        filters = ""
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

    latest_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Latest")]'))
    )
    latest_button.click()
    time.sleep(2.5)   
    
def search_tweets(driver, search_by, from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links,number_of_tweets, option,min_views):
    wait = WebDriverWait(driver, 20)
    formatted_tweets = []
    for topic_name in search_by:
        try:
            perform_search(driver, option, topic_name, search_by, from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links)
            tweet_count = 0
            list_tweet=[]
            max_attempts = 6
            attempt_count = 0
            total_height = int(driver.execute_script("return document.body.scrollHeight"))
            
            # driver.execute_script("window.scrollTo(0, " + str(total_height//8) + ")")
            # time.sleep(1)
            try:
                while attempt_count < max_attempts:
                    try:
                        new_articles = wait_for_elements(driver, '//article[@data-testid="tweet"]', By.XPATH)
                        like_elements = wait_for_elements(driver, '[data-testid="like"]')
                        reposts = wait_for_elements(driver, '[data-testid="retweet"]')
                        engagement_elements = wait_for_elements(driver, 'a[role="link"][aria-label*="views"], a[role="link"][aria-label*="View"]')
                        # try:
                        #     tweets = wait_for_elements(driver, '//div[@data-testid="tweetText"]', By.XPATH)
                        # except:
                        #     print('error')
                        usernames = wait_for_elements(driver, '[data-testid="User-Name"]')
                        replies = wait_for_elements(driver, '[data-testid="reply"]')
                        hrefs = wait_for_elements(driver, "[data-testid=User-Name] a[role=link][href*=status]")
                        times = wait_for_elements(driver, 'time[datetime]', By.CSS_SELECTOR)
                    except Exception as e:
                        print(f"cant find element error :{e}")
                    print(len(new_articles),len(like_elements),len(reposts),len(engagement_elements),len(usernames),len(replies),len(hrefs),len(times))
                    print("getting tweets ...")
    
                    for username, like_element, engagement_element, href_element, reply, repost,timee in zip(
                        usernames, like_elements, engagement_elements, hrefs, replies, reposts,times):
                        
                        user_full_name = (username.find_element(By.XPATH, "..").text.strip().rstrip("."))
                        twitter_handle = re.search(r'@(\w+)', user_full_name).group()

                        likes = like_element.get_attribute("aria-label")
                        likess=int(likes.split()[0]) if likes else 0

                        try:
                            view=engagement_element.get_attribute("aria-label")
                            parts = view.split(", ")
                            views_count = int(parts[-1].split()[0])
                            # print(view)
                        except:
                            views_count = 0
                        
                        
                        repliess = reply.get_attribute("aria-label")
                        repliesss = int(repliess.split()[0]) if repliess else 0

                        repost_text = repost.get_attribute("aria-label")
                        repost_value = int(repost_text.split()[0]) if repost_text else 0

                        href = href_element.get_attribute("href")
                        
                        time_element = timee.get_attribute('datetime')
                        
                        post_id = re.search(r'/status/(\d+)', href).group(1)
                        for article in new_articles:
                            # print(article)
                            article_url = article.find_element(By.CSS_SELECTOR, "[data-testid=User-Name] a[role=link][href*=status]")
                            article_href = article_url.get_attribute("href")
                            if href == article_href:
                                # print(href,article_href)
                                try:
                                    # print(article.get_attribute("outerHTML"))
                                    tweet_article=article.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                                    tweet_text = tweet_article.text
                                    
                                except:
                                    tweet_text= " "#edit what you want to print when there is no tweet text
                        print(f"find_element : {tweet_text}")
                        # tweettext = tweet.text
                        # print(f"elements_present : {tweettext}") 
                        # if tweet != "no_element":
                        #     try:
                        #         new_article.find_element(By.XPATH, '//div[@data-testid="tweetText"]')
                        #         tweet_text = tweet.text
                        #         print(f"find_element : {tweet_text}")
                        #     except:
                        #         tweet_text= "No Text"
                        #     tweettext = tweet.text
                        #     print(f"elements_present : {tweettext}")
                        # else:
                        #     tweet_text = "No Text"
                        # print(views_count,href)
                        post_ids = [tweet['post_id'] for tweet in list_tweet]
                        if post_id in post_ids:
                            print(f"Post with ID {post_id} already exists. Skipping...")
                            continue

                        # print(min_views)
                        if views_count >= min_views and likess >= minimum_likes and repliesss >= minimum_replies:
                            tweet = {
                                    "post_id":post_id,
                                    "Link": href,
                                    "Tweet": tweet_text,
                                    "Username": twitter_handle,
                                    "date_of_post":time_element,
                                    "Likes": likess,
                                    "Reposts": repost_value,
                                    "Replies": repliesss,
                                    "Views": views_count,
                                }
                            list_tweet.append(tweet)
                            print(tweet_count)
                            tweet_count += 1
                            if tweet_count >= number_of_tweets:
                                break
                        
                        else:
                            print(f"skipped: views({views_count}) less than {min_views} or likes({likess}) less than {minimum_likes} or replies({repliesss}) less than {minimum_replies}")
                            
                    if tweet_count >= number_of_tweets:
                        break
                    newheight = int(driver.execute_script("return document.body.scrollHeight"))
            
                    driver.execute_script("window.scrollTo(0, " + str(newheight//2) + ")")
                    
                    if attempt_count >= 3 and attempt_count <= 6:
                        newheight = int(driver.execute_script("return document.body.scrollHeight"))
                        driver.execute_script("window.scrollTo(0, " + str(newheight * 3//4) + ")")
                    elif attempt_count == 7 or attempt_count == 8:
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                    elif attempt_count==2:
                        newheight = int(driver.execute_script("return document.body.scrollHeight"))
                        driver.execute_script("window.scrollTo(0, " + str(newheight * 2//3) + ")")

                    time.sleep(4)
                    attempt_count+=1
                    print(f"attempting to scroll ({attempt_count})")
            except:
                print("error while fetching data")   
            if attempt_count == max_attempts:
                print("Reached maximum number of attempts.")
                
            if option =='1':
                formatted_tweet = {
                    "type": "Topic",
                    "keyword": topic_name,
                    "tweets":list_tweet
                    
                }
            elif option == '2':
                formatted_tweet = {
                    "type": "Profile",
                    "keyword": topic_name,
                    "tweets":list_tweet
                    
                }
            formatted_tweets.append(formatted_tweet)
                
            
        except Exception as e:
            print("Error:", e)
    if option == '1':
        save_tweet_data(formatted_tweets, "tweet_data_topic.json")
    elif option == '2':
        save_tweet_data(formatted_tweets, "tweet_data_username.json")
    
            

def save_tweet_data(tweet_data, filename):
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as jsonfile:
                existing_data = json.load(jsonfile)
        else:
            existing_data = []
    except json.decoder.JSONDecodeError:
        # If there's an error decoding JSON (e.g., file is empty or invalid), initialize existing_data as an empty list
        existing_data = []

    for data in tweet_data:
        existing_data.append(data)
    with open(filename, "w", encoding="utf-8") as jsonfile:
        json.dump(existing_data, jsonfile, indent=4, ensure_ascii=False)
        jsonfile.write('\n')

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
    formatted_tweets = []
    x=datetime.now()
    
    main()
    y=datetime.now()
    print(y-x)
