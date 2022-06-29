# Creation Date: 23/06/2022


import os
import keyboard
import pandas as pd
from time import sleep
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def load_CSV(filename: str, drop_list: list = None):
    ''' Returns: CSV loaded to dataframe with select columns dropped. '''
    if not filename.endswith(".csv"):
        filename += ".csv"
    dataframe = pd.read_csv(filename)
    if drop_list is not None:
        dataframe.drop(drop_list, axis=1, inplace=True)
    return dataframe


def get_secrets():
    ''' Returns: Username and password loaded from ENV. '''
    load_dotenv()
    return os.getenv("USER"), os.getenv("PASS")


def linkedin_login(linkedin, auto_login: bool):
    ''' Purpose: Ensure Linkedin is logged in. '''
    login_point = "https://www.linkedin.com/checkpoint/lg/sign-in-another-account"
    linkedin.get(login_point)
    if auto_login:
        username, password = get_secrets()
        username_input = linkedin.find_element(
            By.CSS_SELECTOR, "input[id='username']")
        username_input.clear()
        username_input.send_keys(username)
        password_input = linkedin.find_element(
            By.CSS_SELECTOR, "input[id='password']")
        password_input.send_keys(password)
        login_button = linkedin.find_element(
            By.XPATH, "//button[@type='submit']")
        login_button.click()
    else:
        input("Press Enter once logged in...")
    sleep(5)


def isNaN(num):
    return num != num


def start_browser(browser_name: str):
    ''' Returns: Selenium browser session. '''
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    browser_name = webdriver.Chrome(ChromeDriverManager().install(),
                                    chrome_options=options)
    browser_name.implicitly_wait(5)
    return browser_name


def build_locations(df):
    ''' Purpose: Store index locations for variables. '''
    columns = list(df.columns.values)
    return {name: columns.index(name) + 1 for name in columns}


def start_session(df):
    ''' Purpose: Bloat code for starting session. '''
    linkedin = start_browser("linkedin")
    reviews = start_browser("website")
    indexs = build_locations(df)
    return [linkedin, reviews], indexs


def update_windows(browsers: list, urls: list):
    ''' Purpose: Update Selenium sessions with new pages. '''
    for index, browser in enumerate(browsers):
        browser.get(urls[index])


def user_input(index: int, column: str):
    ''' Purpose: Collect user input. '''
    while True:
        if keyboard.read_key() == "a":
            print(f"Marked row {index}, {column} false...")
            answer = 0
            break
        if keyboard.read_key() == "d":
            print(f"Marked row {index}, {column}, correct...")
            answer = 1
            break
    return answer


def save_CSV(df, filename: str, drop_list: list = None):
    ''' Purpose: Saves new dataframe to CSV. '''
    if not filename.endswith(".csv"):
        filename += ".csv"
    if drop_list is not None:
        df.drop(drop_list, axis=1, inplace=True)
    df.to_csv(filename, index=False)


def verify_linkedin(filename: str, start: int = None, auto_login: bool = True,
                    show_error: bool = False):
    ''' Purpose: Verifies that the LinkedIn pages are accurate. '''
    df = load_CSV(filename)
    column = 'linkedin_bool'
    if column not in df:
        df[column] = 2
    linkedin = start_browser("linkedin")
    indexs = build_locations(df)
    linkedin_login(linkedin, auto_login)
    print("Checking LinkedIn...")
    print("Press 'a' for incorrect and 'd' for correct...")
    try:
        for row in df.itertuples():
            print("")
            company = row[indexs['name']]
            print(f"Checking {company}, row {row.Index}...")
            if row[indexs[column]] in [0, 1] and row.Index != start:
                print(f"Row {row.Index} already checked...")
                continue
            linkedin_url = f"https://www.{row[indexs['linkedin_url']]}"
            update_windows([linkedin], [linkedin_url])
            user_answer = user_input(row.Index, column)
            df.at[row.Index, column] = user_answer
    except (Exception, KeyboardInterrupt) as e:
        if show_error:
            print(e)
    save_CSV(df, filename)


def verify_website(filename: str, website: str, start: int = None, 
                auto_login: bool = True, show_error: bool = False):
    ''' Purpose: Facilitates verification of links and stores status. '''
    df = load_CSV(filename)
    column = f'{website}_bool'
    if column not in df:
        df[column] = 2
    browsers, indexs = start_session(df)
    linkedin_login(browsers[0], auto_login)
    print(f"Checking {website}...")
    print("Press 'a' for incorrect and 'd' for correct...")
    try:
        for row in df.itertuples():
            print("")
            company = row[indexs['name']]
            print(f"Checking {company}, row {row.Index}...")
            if row[indexs[column]] in [0, 1] and row.Index != start:
                print(f"Row {row.Index} already checked...")
                continue
            reviews_url = row[indexs[f'{website}_url']] # Add code to ensure it loads to Australia specifically
            if isNaN(reviews_url):
                df.at[row.Index, column] = 0
                print(f"No valid {website} url...")
                continue
            linkedin_url = f"https://www.{row[indexs['linkedin_url']]}"
            update_windows(browsers, [linkedin_url, reviews_url])
            user_answer = user_input(row.Index, column)
            df.at[row.Index, column] = user_answer
    except (Exception, KeyboardInterrupt) as e:
        if show_error:
            print(e)
    save_CSV(df, filename)

# Need verification just for LinkedIn
verify_linkedin('verification/AUS_1001+_Checking')
