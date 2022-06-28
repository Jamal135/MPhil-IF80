# Creation Date: 23/06/2022


import os
import sys
import keyboard
import numpy as np
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
    if drop_list is None:
        drop_list = []
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


def start_browser(browser_name: str):
    ''' Returns: Selenium browser session. '''
    browser_name = webdriver.Chrome(ChromeDriverManager().install())
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
    sleep(5)


def user_input(index, website):
    ''' Purpose: Collect user input. '''
    while True:
        if keyboard.read_key() == "a":
            print(f"Marked row {index}, {website} false...")
            answer = 0
            break
        if keyboard.read_key() == "d":
            print(f"Marked row {index}, {website} correct...")
            answer = 1
            break
    return answer
       

def verify_data(filename: str, website: str, auto_login: bool = True):
    ''' Purpose: Facilitates verification of links and stores status. '''
    df = load_CSV(filename)
    column = f'{website}_bool'
    if column not in df:
        df[column] = 0
    browsers, indexs = start_session(df)
    linkedin_login(browsers[0], auto_login)
    print("Press 'a' for correct and 'd' for incorrect.")
    try:
        for row in df.itertuples():
            if row[indexs[column]] == 1:
                continue
            reviews_url =  row[indexs[f'{website}_url']]
            if reviews_url is None:
                row[indexs[column]] == 1
                continue
            linkedin_url = f"https://www.{row[indexs['linkedin_url']]}" 
            update_windows(browsers, [linkedin_url, reviews_url])
            user_answer = user_input(row.Index, website)
            df.at[row.Index, column] = user_answer
            print(df[row.Index, column])
    except KeyboardInterrupt:
        pass
    #save


verify_data('links/New_AUS_1001+_Links', 'indeed')