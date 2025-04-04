import csv
from gender_guesser.detector import Detector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

USERNAME = 'your_test_username'
PASSWORD = 'your_test_password'

detector = Detector()

def guess_gender(name):
    if not name:
        return 'unknown'
    guess = detector.get_gender(name.split()[0])
    return guess if guess != 'unknown' else 'unknown'

def run_scraper(target_user, gender_filter='all'):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(options=options)

    def login():
        driver.get('https://www.instagram.com/accounts/login/')
        time.sleep(3)
        driver.find_element(By.NAME, 'username').send_keys(USERNAME)
        driver.find_element(By.NAME, 'password').send_keys(PASSWORD)
        driver.find_element(By.NAME, 'password').send_keys(Keys.ENTER)
        time.sleep(5)

    def get_following_usernames():
        driver.get(f'https://www.instagram.com/{target_user}/')
        time.sleep(3)
        driver.find_element(By.PARTIAL_LINK_TEXT, 'following').click()
        time.sleep(3)
        scroll_box = driver.find_element(By.XPATH, "//div[@role='dialog']//ul/div")
        usernames = []
        while len(usernames) < 50:
            links = scroll_box.find_elements(By.TAG_NAME, 'a')
            for link in links:
                user = link.text
                if user and user not in usernames:
                    usernames.append(user)
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)
            time.sleep(1.5)
        return usernames

    def scrape_profile(username):
        driver.get(f'https://www.instagram.com/{username}/')
        time.sleep(3)
        try:
            name = driver.find_element(By.XPATH, '//header//section//h1').text
        except:
            name = ''
        try:
            bio = driver.find_element(By.XPATH, '//header//section/div[2]/span').text
        except:
            bio = ''
        try:
            dm = driver.find_element(By.XPATH, '//header//section//div//button[text()="Message"]')
            can_dm = True
        except:
            can_dm = False
        gender = guess_gender(name)
        return {
            'username': username,
            'name': name,
            'bio': bio,
            'can_dm': can_dm,
            'gender': gender
        }

    login()
    usernames = get_following_usernames()
    results = []

    for user in usernames:
        data = scrape_profile(user)
        if gender_filter != 'all' and data['gender'] != gender_filter:
            continue
        results.append(data)

    with open('output.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['username', 'name', 'bio', 'can_dm', 'gender'])
        writer.writeheader()
        writer.writerows(results)

    driver.quit()
    return results
