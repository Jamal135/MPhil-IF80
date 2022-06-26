# Creation Date: 23/06/2022


import numpy as np
import pandas as pd
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC


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


def start_browser(browser_name: str):
    ''' Returns: Selenium browser session. '''
    browser_name = webdriver.Chrome(ChromeDriverManager().install())
    browser_name.implicitly_wait(5)
    return browser_name


def build_locations(df):
    ''' Purpose: Store index locations for variables. '''
    columns = list(df.columns.values)
    return {name: columns.index(name) + 1 for name in columns}


def update_windows(linkedin, website, links: list):
    ''' Purpose: Update Selenium session with list of new windows. '''
    print(links[0])
    print(links)
    linkedin.get(f"https://www.{links[0]}") # Open LinkedIn
    website.get(links[1]) # Open Selected Website
    sleep(50)


def verify_data(filename: str, website: str):
    ''' Purpose: Facilitates verification of links and stores status. '''
    df = load_CSV(filename)
    column = f'{website}_bool'
    if column not in df:
        df[column] = np.nan
    print(df)
    linkedin = start_browser("linkedin")
    reviews = start_browser("website")
    indexs = build_locations(df)
    print(indexs)
    try:
        for row in df.itertuples():
            #if row[indexs[column]] != None:
                #continue
            links = [row[indexs['linkedin_url']], row[indexs[f'{website}_url']]]
            # may have no reviews
            print(links)
            update_windows(linkedin, reviews, links)
    except KeyboardInterrupt:
        pass
    #save


verify_data('links/New_AUS_1001+_Links', 'indeed')