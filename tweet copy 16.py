import json
import time

from decouple import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

try:
    username = "aa30424@gmail.com"
    password = "abhinav1708580"
except Exception as e:
    print(
        f"Make sure username and password are added to .env file.\nError: {e}"
    )

else:
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
             topic_count = int(input(f"How many topics do you want search? (1-10): "))
             if 1 <= topic_count <= 10:  # Check if within range (1 to 10)
                break
             else:
                print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Please enter a number.")

    print("Please enter the topic names you want me to search for")
    topic_names = [input(f"Enter topic {i + 1}: ") for i in range(topic_count)]

    # Inputs for search filter
    from_account = input("Enter the account username from which you would like to retrieve tweets"
                         "\nLeave this field empty to retrieve tweets from all accounts: ")
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
    include_replies = input("Do you want to include replies? (Y/n): ")
    include_replies = include_replies.lower() in ['y', 'yes']
    include_links = input("Do you want to include links? (Y/n): ")
    include_links = include_links.lower() in ['y', 'yes']

    driver = webdriver.Chrome()

    driver.get("https://twitter.com/login")

    wait = WebDriverWait(driver, 10)

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
            # user=input("enter username or phone number")
            username_input_field.send_keys("abhi_26_04")
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

    print("searching tweets")
    for topic_name in topic_names:

        search_input = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, '//input[@data-testid="SearchBox_Search_Input"]')
            )
        )
        search_input.send_keys(Keys.CONTROL + "a",Keys.DELETE)

        # Perform search with filter
        if from_account or minimum_replies or minimum_likes or minimum_retweets or not include_replies or not include_links:
            filters = ""
            if from_account:
                filters += f"(from:{from_account})"
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
            search_input.send_keys(f"{topic_name} {filters}")
        else:
            search_input.send_keys(topic_name)
        search_input.send_keys(Keys.ENTER)

        # Wait for the tweets to load
        tweet_count = 0
        while True:
            
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(6)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(3)
            # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            # time.sleep(3)
            # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            # time.sleep(3)
            # Wait for the like and engagement elements to load
            like_elements = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, '[data-testid="like"]')
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
            hrefs = wait.until(
                EC.presence_of_all_elements_located(
                    (
                        By.CSS_SELECTOR,
                        "[data-testid=User-Name] a[role=link][href*=status]",
                    )
                )
            )
            print("getting tweets ...")
            # Iterate over usernames and tweets and print them
            
            for username, tweet, like_element, engagement_element, href_element in zip(
                usernames, tweets, like_elements, engagement_elements, hrefs
            ):
                user_full_name = (
                    username.find_element(By.XPATH, "..").text.strip().rstrip(".")
                )
                # Extract the number of likes or default to 0 if not found
                likes = like_element.text.split()[0] if like_element.text else "0"
                # Extract the number of views/engagement or default to 0 if not found
                engagement = (
                    engagement_element.text.split()[0]
                    if engagement_element.text
                    else "0"
                )

                href = href_element.get_attribute("href")
                tweet_data = {
                    "Username": user_full_name,
                    "Tweet": tweet.text,
                    "Likes": likes,
                    "Replies": engagement,
                    # "Views": views_count,
                    "Link": href
                }
                        
                with open("tweet_data.json", "a", encoding="utf-8") as jsonfile:
                    json.dump(tweet_data, jsonfile)
                    jsonfile.write('\n')
                time.sleep(0.3)
                print(f"Username: {user_full_name}")
                print(f"Tweet: {tweet.text}")
                print(f"Likes: {likes}")
                print(f"Engagement: {engagement}")
                print("Link", href)
                print("---")
                time.sleep(5)
                
                # Increment counter and break after dynamic tweets count
                tweet_count += 1
                if tweet_count >= number_of_tweets:
                    break
            if tweet_count >= number_of_tweets:
                    break


    driver.quit()