import csv
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
    
    from_account=False
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
        save_cookies_to_csv(username, cookies)
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
            
def save_cookies_to_csv(username, cookies):
    filename = f"{username}_cookies.csv"
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ['name', 'value', 'domain', 'path', 'expiry']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for cookie in cookies:
            # Filter out unwanted fields and handle missing 'expiry' key
            filtered_cookie = {key: cookie.get(key, '') for key in fieldnames}
            writer.writerow(filtered_cookie)

        print(f"Cookies saved to {filename}")


def search_tweets(driver, topic_name, from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links):
    wait = WebDriverWait(driver, 10)
    driver.get("https://twitter.com/home")
    time.sleep(3)
    try:
        search_input = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, '//input[@data-testid="SearchBox_Search_Input"]')
            )
        )
        
    except Exception as e:
        print(f"Error occurred while searching for input element: {e}")
        return

    search_input.send_keys(Keys.CONTROL + "a", Keys.DELETE)

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
    search_input.send_keys(f"from:{topic_name} {filters}")
    search_input.send_keys(Keys.ENTER)

    time.sleep(2)
    find_articles(driver, 10)
    # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    # time.sleep(2.5)
    # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    # time.sleep(3)
    # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    # time.sleep(2.5)
    
def find_articles(driver, number_of_articles):
    wait = WebDriverWait(driver, 10)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(2.5)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(2.5)
    # Wait for the articles to load
    articles = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//article[@data-testid="tweet"]')))
    
    # Ensure the number of articles found does not exceed the required number
    articles = articles[:number_of_articles]
    print(articles)
    for i in articles:
        # print(i.get_attribute("outerHTML"))
        # link = i.find_element(By.CSS_SELECTOR, "a[role=link][href*=status]").get_attribute("href")
        get_tweet_data(driver, i)
    
    return articles

def get_tweet_data(driver, article):
    # driver.get(link)
    # print(link)
    time.sleep(5)

    try:
        driver.execute_script("window.scrollTo(0, 0);")
        article.location_once_scrolled_into_view

        # Extract tweet data from the provided article
        username = article.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]').text
        tweet_text = article.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
        like_element = article.find_element(By.CSS_SELECTOR, '[data-testid="like"]')
        likes = like_element.text.split()[0] if like_element.text else "0"
        engagement_element = article.find_element(By.CSS_SELECTOR, '[aria-label*="views"]')
        engagement = engagement_element.text.split()[0] if engagement_element.text else "0"
        view_element = article.find_element(By.XPATH, '//div[contains(@aria-label, "replies") and contains(@aria-label, "reposts") and contains(@aria-label, "likes") and contains(@aria-label, "bookmarks") and contains(@aria-label, "views")]')
        views_text = view_element.get_attribute("aria-label")
        parts = views_text.split(", ")
        views_count = int(parts[-1].split()[0])
        href_element = article.find_element(By.CSS_SELECTOR, "[data-testid=User-Name] a[role=link][href*=status]")
        href = href_element.get_attribute("href")
        
        # Write tweet data to CSV
        with open("tweet_data.csv", "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([username, tweet_text, likes, engagement, views_count, href])

    except Exception as e:
        print(f"Error occurred while retrieving tweet data: {e}")

# def get_tweet_data(driver, i):
#     wait = WebDriverWait(i, 10)

#     try:
#         like_elements = wait.until(
#             EC.presence_of_all_elements_located(
#                 (By.CSS_SELECTOR, '[data-testid="like"]')
#             )
#         )
#         engagement_elements = wait.until(
#             EC.presence_of_all_elements_located(
#                 (By.CSS_SELECTOR, '[aria-label*="views"]')
#             )
#         )
#         views_elements = wait.until(
#             EC.presence_of_all_elements_located(
#                 (By.CSS_SELECTOR, 'div[aria-label*="replies"][aria-label*="reposts"][aria-label*="likes"][aria-label*="bookmarks"][aria-label*="views"]')
#             )
#         )      
#         tweets = wait.until(
#             EC.presence_of_all_elements_located(
#                 (By.XPATH, '//div[@data-testid="tweetText"]')
#             )
#         )
#         usernames = wait.until(
#             EC.presence_of_all_elements_located(
#                 (By.CSS_SELECTOR, '[data-testid="User-Name"]')
#             )
#         )
#         hrefs = wait.until(
#             EC.presence_of_all_elements_located(
#                 (
#                     By.CSS_SELECTOR,
#                     "[data-testid=User-Name] a[role=link][href*=status]",
#                 )
#             )
#         )

#     except Exception as e:
#         print(f"Error occurred while retrieving tweet data: {e}")
#         return

#     headers = ["Username", "Tweet", "Likes", "Replies", "Views", "Link"]

#     # Specify the name of the CSV file
#     csv_file = "tweet_data.csv"

#     # Writing data to CSV file
#     with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=headers)
        
#         # Write headers
#         writer.writeheader()
        
#         # Iterate over the data
#         tweet_count = 0
#         for username, viewelement, tweet, like_element, engagement_element, href_element in zip(
#             usernames, views_elements, tweets, like_elements, engagement_elements, hrefs
#         ):
#             try:
#                 user_full_name = username.find_element(By.XPATH, "..").text.strip().rstrip(".")
#                 likes = like_element.text.split()[0] if like_element.text else "0"
#                 engagement = engagement_element.text.split()[0] if engagement_element.text else "0"
#                 views_text = viewelement.get_attribute("aria-label")
#                 # print(views_text)
#                 parts = views_text.split(", ")
#                 views_count = int(parts[-1].split()[0])
#                 # print(views_count)
#                 # views_number = views_text.split("views")[0] if views_text else "0"
#                 href = href_element.get_attribute("href")
                
#                 # Write row to CSV
#                 writer.writerow({
#                     "Username": user_full_name,
#                     "Tweet": tweet.text,
#                     "Likes": likes,
#                     "Replies": engagement,
#                     "Views": views_count,
#                     "Link": href
#                 })

#                 tweet_count += 1
#                 if tweet_count >= number_of_tweets:
#                     break
#             except Exception as e:
#                 print(f"Error occurred while processing tweet: {e}")

#     print(f"Data written to {csv_file} successfully!")


def main():
    driver = webdriver.Chrome()
    while True:
        print("OPTIONS")
        print("1. Login with username and password")
        print("2. Login with saved cookies")
        print("3. Search tweets")
        # option = input("Enter your choice: ")

    # if option == "1":
        username, password = get_credentials()
        if not username or not password:
            return
        login(driver, username, password)

        # elif option == "2":
        #     driver.get("https://twitter.com/home")
        #     time.sleep(5)
        #     username = input("Enter your username: ")
        #     cookies_file = f"{username}_cookies.csv"
        #     try:
        #         with open(cookies_file, "r") as csvfile:
        #             reader = csv.DictReader(csvfile)
        #             cookies = []
        #             for row in reader:
        #                 print(row)
        #                 if row["expiry"]:
                            
        #                     # Convert expiry timestamp to integer
        #                     row["expiry"] = int(row["expiry"])
        #                 cookies.append(row)
        #         # Adding cookies to the browser session
        #         for cookie in cookies:
        #             driver.add_cookie(cookie)
        #         print("Login with saved cookies successful!")
        #     except FileNotFoundError:
        #         print(f"Error: Cookies file '{cookies_file}' not found.")

        #     driver.get("https://twitter.com/home")  # Open the page again to apply cookies
        #     # Now you can interact with Twitter as a logged-in user

    # elif option == "3":
        # number_of_tweets, topic_names = get_tweet_parameters()
        number_of_tweets=1
        topic_names=['intel']
        from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links = get_search_filters()

        print("searching tweets")
        for topic_name in topic_names:
            search_tweets(driver, topic_name, from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links)
            # get_tweet_data(driver, number_of_tweets)

        # elif option.lower() == "quit":
        break

    driver.quit()

if __name__ == "__main__":
    main()
