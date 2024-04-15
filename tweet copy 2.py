import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

try:
    username = "aa30424@gmail.com"
    password = "/qfWk6PZEa#bQqy"
except Exception as e:
    print(f"Make sure username and password are added to .env file.\nError: {e}")
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
            topic_count = int(input(f"How many topics do you want to search? (1-10): "))
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

    # Maximize the browser window
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
        print("Login failed.")

    # Prepare CSV file
    csv_filename = "twitter_data.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Username", "Tweet", "Likes", "Replies", "Views", "Link"])

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
                if type(minimum_replies) == int:
                    filters += f" min_replies:{minimum_replies}"
                if type(minimum_likes) == int:
                    filters += f" min_faves:{minimum_likes}"
                if type(minimum_retweets) == int:
                    filters += f" min_retweets:{minimum_retweets}"
                if not include_replies:
                    filters += " -filter:replies"
                if not include_links:
                    filters += " -filter:links"
                search_input.send_keys(f"{topic_name} {filters}")
            else:
                search_input.send_keys(topic_name)
            search_input.send_keys(Keys.ENTER)

            # Wait for the tweets to load
            time.sleep(2)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(2.5)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(3)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(2.5)
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
            views_elements = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".css-175oi2r[aria-label*='views']")
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
            # Iterate over usernames and tweets and save them to CSV
            tweet_count = 0
            for username, viewelement, tweet, like_element, engagement_element, href_element in zip(
                    usernames, views_elements, tweets, like_elements, engagement_elements, hrefs
            ):
                user_full_name = username.find_element(By.XPATH, "..").text.strip().rstrip(".")
                likes = like_element.text.split()[0] if like_element.text else "0"
                engagement = engagement_element.text.split()[0] if engagement_element.text else "0"

                # Extract views from the view_element
                views_text = viewelement.get_attribute("aria-label")
                views_number = views_text.split(" views")[0] if views_text else "0"

                href = href_element.get_attribute("href")

                # Write data to CSV
                writer.writerow([user_full_name, tweet.text, likes, engagement, views_number, href])

                # Print tweet details
                print(f"Username: {user_full_name}")
                print(f"Tweet: {tweet.text}")
                print(f"Likes: {likes}")
                print(f"Replies: {engagement}")
                print(f"Views: {views_number}")
                print(f"Link: {href}")
                print("---")

                time.sleep(0.3)

                # Increment counter and break after dynamic tweets count
                tweet_count += 1
                if tweet_count >= number_of_tweets:
                    break

    print(f"Data saved to {csv_filename}")
    driver.quit()
