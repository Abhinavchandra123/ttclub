import csv
import json
import time
from decouple import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_credentials():
    try:
        username = "aa30424@gmail.com"
        password = "/qfWk6PZEa#bQqy"
    except Exception as e:
        print(f"Make sure username and password are added to .env file.\nError: {e}")
        return None, None
    return username, password

def get_tweet_parameters():
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

    return number_of_tweets, topic_names

def get_search_filters():
    # from_account = input("Enter the account username from which you would like to retrieve tweets"
    #                      "\nLeave this field empty to retrieve tweets from all accounts: ")
    def get_integer_or_none(prompt):
        while True:
            value = input(prompt)
            try:
                return int(value) if value else None
            except ValueError:
                if value:  # Check if the input is not empty
                    print("Please enter a number or leave empty.")
                continue  # Restart the loop if invalid input found (non-empty and non-numeric)

    # minimum_replies = get_integer_or_none("Enter the minimum replies tweets should have (or leave empty): ")
    # minimum_likes = get_integer_or_none("Enter the minimum likes tweets should have (or leave empty): ")
    # minimum_retweets = get_integer_or_none("Enter the minimum retweets should have (or leave empty): ")
    # include_replies = input("Do you want to include replies? (Y/n): ")
    # include_replies = include_replies.lower() in ['y', 'yes']
    # include_links = input("Do you want to include links? (Y/n): ")
    # include_links = include_links.lower() in ['y', 'yes']
    
    from_account='narendramodi'
    minimum_replies = 1
    minimum_likes = 1
    minimum_retweets = 1
    include_replies = 'y'
    include_links = 'y'
    
    return from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links

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

        # Get cookies
        cookies = driver.get_cookies()

        # Save cookies to CSV file
        # save_cookies_to_csv(username, cookies)
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
                # user=input("enter username or phone number")
                username_input_field.send_keys("abhi_26_04")
                username_input_field.send_keys(Keys.ENTER)
                print("Username entered again")
                
        except:
            print("Login failed.")

         
# def save_cookies_to_csv(username, cookies):
#     filename = f"{username}_cookies.csv"
#     with open(filename, "w", newline="") as csvfile:
#         fieldnames = ['name', 'value', 'domain', 'path', 'expiry']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#         writer.writeheader()
#         for cookie in cookies:
#             # Filter out unwanted fields and handle missing 'expiry' key
#             filtered_cookie = {key: cookie.get(key, '') for key in fieldnames}
#             writer.writerow(filtered_cookie)

#         print(f"Cookies saved to {filename}")


def scroll_down_until_articles_present(driver, number_of_articles):
    articles = []
    
    wait = WebDriverWait(driver, 10)
    last_article = None
    while len(articles) < number_of_articles:
        print(f"Current number of articles: {len(articles)}")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Introduce a delay to allow time for new content to load
        
        new_articles = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//article[@data-testid="tweet"]')))
        
        if new_articles:
            # Filter out already collected articles
            new_articles = [article for article in new_articles if article not in articles]
            articles.extend(new_articles)
            last_article = new_articles[-1] if new_articles else last_article  # Update last article reference
            print(f"Total articles: {len(articles)}")
            print(articles)
        else:
            print("No new articles found.")
        
        if len(articles) >= number_of_articles:
            break
    
    return articles

def search_tweets(driver, topic_names, from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links,number_of_tweets):
    wait = WebDriverWait(driver, 10)
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
            else:
                search_input.send_keys(f"from:{topic_name} {filters}")
        else:
            search_input.send_keys(f"from:+{topic_name}")
        search_input.send_keys(Keys.ENTER)

        # Wait for the tweets to load
        like_elements = []
        engagement_elements = []
        views_elements = []
        tweets = []
        usernames = []
        hrefs = []
        time.sleep(4)
        articles=scroll_down_until_articles_present(driver, number_of_tweets)
        
        for article in articles:
            try:
                username = article.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
                view_element = article.find_element(By.CSS_SELECTOR, 'div[aria-label*="replies"][aria-label*="reposts"][aria-label*="likes"][aria-label*="bookmarks"][aria-label*="views"]')
                tweet = article.find_element(By.XPATH, '//div[@data-testid="tweetText"]')
                like_element = article.find_element(By.CSS_SELECTOR, '[data-testid="like"]')
                engagement_element = article.find_element(By.CSS_SELECTOR, '[aria-label*="views"]')
                href_element = article.find_element(By.CSS_SELECTOR, "[data-testid=User-Name] a[role=link][href*=status]")

                # Extract data from each element
                user_full_name = username.find_element(By.XPATH, "..").text.strip().rstrip(".")
                likes = like_element.text.split()[0] if like_element.text else "0"
                engagement = engagement_element.text.split()[0] if engagement_element.text else "0"
                views_text = view_element.get_attribute("aria-label")
                views_count = int(views_text.split("views")[0].strip().replace(",", "")) if views_text else 0
                href = href_element.get_attribute("href")

                # Print or store the extracted data
                tweet_data = {
                    "Username": user_full_name,
                    "Tweet": tweet.text,
                    "Likes": likes,
                    "Replies": engagement,
                    "Views": views_count,
                    "Link": href
                }
                print(tweet_data)

                with open("tweet_data.json", "a", encoding="utf-8") as jsonfile:
                    json.dump(tweet_data, jsonfile)
                    jsonfile.write('\n')

            except Exception as e:
                print(f"Error occurred while retrieving tweet data: {e}")
                # Handle stale element reference exception by re-fetching the elements
                pass

            time.sleep(0.3)
            
            # Increment counter and break after dynamic tweets count
            # tweet_count += 1
            # print(tweet_count)
            # if tweet_count >= number_of_tweets:
            #     break
            






def main():
    driver = webdriver.Chrome()
    username, password = get_credentials()
    if not username or not password:
        return
    login(driver, username, password)
    # number_of_tweets,topic_names=get_tweet_parameters()
    number_of_tweets=20
    topic_names=['india']
    from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links = get_search_filters()

    print("searching tweets")
    search_tweets(driver, topic_names, from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links,number_of_tweets)

    driver.quit()

if __name__ == "__main__":
    main()
