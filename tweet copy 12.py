import csv
import json
import re
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
        password = "abhinav1708580"
    except Exception as e:
        print(f"Make sure username and password are added to .env file.\nError: {e}")
        return None, None
    return username, password

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
            count = int(input(f"How many tweet do you want search? (1-10): "))
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
    # min_views = get_integer_or_none("Enter the minimum views should have (or leave empty): ")
    
    if option == '1':
        include_replies = input("Do you want to include replies? (Y/n): ")
        include_replies = include_replies.lower() in ['y', 'yes']
        include_links = input("Do you want to include links? (Y/n): ")
        include_links = include_links.lower() in ['y', 'yes']
        
    if option == '2':
        include_links = False
        include_replies = False

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

def scroll_down_until_articles_present(driver, number_of_articles):
    articles = []
    unique_hrefs = set()  # Set to store unique article hrefs
    
    wait = WebDriverWait(driver, 10)
    last_article = None
    while len(articles) < number_of_articles:
        # print(f"Current number of articles: {len(articles)}")
        
        
        new_articles = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//article[@data-testid="tweet"]')))
        
        if new_articles:
            for article in new_articles:
                href = article.find_element(By.CSS_SELECTOR, "[data-testid=User-Name] a[role=link][href*=status]").get_attribute("href")
                print(f"href of articles: {href}")
                if href not in unique_hrefs:
                    articles.append(article)
                    unique_hrefs.add(href)
                    
            last_article = new_articles[-1]  # Update last article reference
            
            
            # print(unique_hrefs)
        else:
            print("No new articles found.")
        
        if len(articles) >= number_of_articles:
            break
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)  # Introduce a delay to allow time for new content to load
    
    return articles,unique_hrefs

def search_tweets(driver, search_by, from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links,number_of_tweets, option):
    wait = WebDriverWait(driver, 20)
    for topic_name in search_by:

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
                search_input.send_keys(f"{topic_name} {filters}")
                
        else:
            search_input.send_keys(f"{topic_name}")
        search_input.send_keys(Keys.ENTER)
        time.sleep(3)

        # Wait for the tweets to load
        articles,unique_hrefs = scroll_down_until_articles_present(driver, number_of_tweets)
        wait = WebDriverWait(driver, 20)
        tweet_count=0
        for href in unique_hrefs:
            
            print(href)
            driver.get(href)
            first_article = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "article[data-testid='tweet']")
                )
            )
            outer_html = first_article.get_attribute("outerHTML")
            # print(outer_html)
            time.sleep(4)
            viewcounts=0
            while True:
                viewcounts+=1
                print(viewcounts)
                
                try:
                    views_elements = first_article.find_element(
                            By.XPATH, ".//div[contains(@aria-label, 'replies')][contains(@aria-label, 'reposts')][contains(@aria-label, 'likes')][contains(@aria-label, 'views')]"
                        )
                    break
                except:
                    y_coord = first_article.location['y'] + first_article.size['height']

                    # Calculate the height of the viewport
                    viewport_height = driver.execute_script("return window.innerHeight")

                    # Calculate the y-coordinate to scroll to (center the bottom of the first_article)
                    scroll_to_y = y_coord - (viewport_height / 2)

                    # Scroll to the calculated y-coordinate
                    driver.execute_script("window.scrollTo(0, arguments[0]);", scroll_to_y)
                    time.sleep(2)
                    if viewcounts > 8:
                        print("cant find like,views,repplies,repost")
                        break
                
            print(views_elements.get_attribute("aria-label"))
            # Locate elements within the first article
            # like_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="like"]')), first_article)
            # print(like_elements)
            # engagement_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[aria-label*="views"]')), first_article)
            # print(engagement_elements)
            # views_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[aria-label*="replies"][aria-label*="reposts"][aria-label*="likes"][aria-label*="bookmarks"][aria-label*="views"]')), first_article)
            # tweets = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-testid="tweetText"]')), first_article)
            # usernames = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="User-Name"]')), first_article)
            # hrefs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid=User-Name] a[role=link][href*=status]")), first_article)
            # like_element = first_article.find_element(By.CSS_SELECTOR, '[data-testid="like"]')
            # engagement_element = first_article.find_element(By.CSS_SELECTOR, '[aria-label*="views"]')
            time.sleep(1)
            tweet = first_article.find_element(By.XPATH, '//div[@data-testid="tweetText"]')
            time.sleep(1)
            username = first_article.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
            # href = first_article.find_element(By.CSS_SELECTOR, "[data-testid=User-Name] a[role=link][href*=status]")

            # Print each object with its name
            # print("Like:", like_element.text)
            # print("Engagement:", engagement_element.get_attribute("aria-label"))
            print("Tweet:", tweet.text)
            print("Username:", username.text)
            # print("Href:", href.get_attribute("href"))
            

            # driver.implicitly_wait(10)

            # # Extract HTML source of the page
            # html = driver.page_source
        
        # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        # time.sleep(2.5)
        # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        # time.sleep(3)
        # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        # time.sleep(2.5)
        # time.sleep(5)
            # like_elements = wait.until(
            #     EC.presence_of_all_elements_located(
            #         (By.CSS_SELECTOR, '[data-testid="like"]')
            #     )
            # )
            # engagement_elements = wait.until(
            #     EC.presence_of_all_elements_located(
            #         (By.CSS_SELECTOR, '[aria-label*="views"]')
            #     )
            # )
            # views_elements = wait.until(
            #     EC.presence_of_all_elements_located(
            #         (By.CSS_SELECTOR, 'div[aria-label*="replies"][aria-label*="reposts"][aria-label*="likes"][aria-label*="bookmarks"][aria-label*="views"]')
            #     )
            # )      
            # tweets = wait.until(
            #     EC.presence_of_all_elements_located(
            #         (By.XPATH, '//div[@data-testid="tweetText"]')
            #     )
            # )
            # usernames = wait.until(
            #     EC.presence_of_all_elements_located(
            #         (By.CSS_SELECTOR, '[data-testid="User-Name"]')
            #     )
            # )
            # hrefs = wait.until(
            #     EC.presence_of_all_elements_located(
            #         (
            #             By.CSS_SELECTOR,
            #             "[data-testid=User-Name] a[role=link][href*=status]",
            #         )
            #     )
            # )
            # print("getting tweets ...")
            # Iterate over usernames and tweets and print them
            # tweet_count = 0     
            # for username,viewelement, tweet, like_element, engagement_element, href_element in zip(
            #     usernames,views_elements, tweets, like_elements, engagement_elements, hrefs
            # ):
            # print(usernames)
            # g=0
            try:
                user_full_name = username.find_element(By.XPATH, "..").text.strip().rstrip(".")
                print(user_full_name)
            except:
                a=username.get_attribute("outerHTML")
                print(a)
            print(username)
            # for i in username:
            #     print(i)
            #     g+=1
            #     try:
            #         user_full_name = i.find_element(By.XPATH, "..").text.strip().rstrip(".")
            #     except:
            #         a=i.get_attribute("outerHTML")
            #         print(a)
            # likes = like_elements.text.split()[0] if like_elements.text else "0"
            # engagement = engagement_elements.text.split()[0] if engagement_elements.text else "0"

            # Extract views from the view_element
            views_text = views_elements.get_attribute("aria-label")
            values = re.findall(r'\d+', views_text)

            # Print the extracted values
            print("Replies:", values[0])
            print("Reposts:", values[1])
            print("Likes:", values[2])
            # print("Bookmarks:", values[3])
            # print("Views:", values[4])
            # views_number = views_text.split("views")[0] if views_text else "0"
            # print(views_text)
            parts = views_text.split(", ")
            views_count = int(parts[-1].split()[0])
            # print(views_count)
            # href = hrefs.get_attribute("href")
            # for i in tweet:
            print(tweet.get_attribute(outer_html))

            tweet_data = {
                "Username": user_full_name,
                "Tweet": tweet.text,
                "Likes": values[2],
                "Replies": values[0],
                "Views": views_count,
                "Link": href
            }
            
            with open("tweet_data.json", "a", encoding="utf-8") as jsonfile:
                json.dump(tweet_data, jsonfile)
                jsonfile.write('\n')
            time.sleep(0.3)
            
            print(tweet_count)
            tweet_count += 1
            if tweet_count > number_of_tweets:
                break
            


def main():
    
    username, password = get_credentials()
    while True:
        print("OPTIONS")
        print("1. search by topic")
        print("2. search by people")
        print("3. quit")
        option = input("Enter your choice: ")

        if option == "1":
            if not username or not password:
                return
            
            number_of_tweets, search_by=get_tweet_parameters(option)
            from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links = get_search_filters(option)
            driver = webdriver.Chrome()
            login(driver, username, password)
            print("searching tweets")
            search_tweets(driver, search_by, from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links,number_of_tweets, option)
        elif option == "2":
            
            if not username or not password:
                return
            
            number_of_tweets, search_by=get_tweet_parameters(option)
            from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links = get_search_filters(option)
            driver = webdriver.Chrome()
            login(driver, username, password)
            print("searching tweets")
            search_tweets(driver, search_by, from_account, minimum_replies, minimum_likes, minimum_retweets, include_replies, include_links,number_of_tweets, option)

        elif option == "3":
            break

        elif option.lower() == "quit":
            break
       
        break

    driver.quit()

if __name__ == "__main__":
    main()
