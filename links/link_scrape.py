# Creation Date: 10/02/2022

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
from selenium.webdriver.common.by import By
from difflib import SequenceMatcher
from googlesearch import search
from selenium import webdriver
from bs4 import BeautifulSoup
import dask.dataframe as dd
from time import sleep
from tqdm import tqdm
import traceback
import logging
import os.path
import pandas
import csv
import sys
import re
import os


headers = ['index', 'name', 'industry', 'region', 'size', 'founded', 'linkedin_url', 'indeed_url',
           'indeed_reviews', 'seek_url', 'seek_reviews', 'total_reviews', 'correct', 'scores', 'valid_urls']
any_size = ['1-10', '11-50', '51-200', '201-500',
            '501-1000', '1001-5000', '5001-10000', '10001+']

# Seeks own reviews seems to break stuff...
seeks_reviews = "https://www.seek.com.au/companies/seek-432600/reviews"
# Ghost Glassdoor link that breaks stuff...
glassdoor_reviews = ["https://www.glassdoor.com.au/Reviews/index.htm", "https://www.glassdoor.com.au/Reviews/Glassdoor-Reviews-E100431.htm"]

# Disable some logging
logging.getLogger('WDM').setLevel(logging.NOTSET)

def halt():
    print("\nInterrupted")
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)


def dictionary_build():
    return {
        'index': [],
        'name': [],
        'industry': [],
        'region': [],
        'size': [],
        'founded': [],
        'linkedin_url': [],
        'indeed_url': [],
        'indeed_reviews': [],
        'seek_url': [],
        'seek_reviews': [],
        'glassdoor_url': [],
        'glassdoor_reviews': [],
        'total_reviews': [],
        'correct': [],
        'scores': [],
        'valid_urls': []
    }


def end_check(string: str):
    ''' Returns: String with correct ending. '''
    if not string.endswith(".csv"):
        string += ".csv"
    return string


def verify_names(input_name: str, output_name: str):
    ''' Returns: Verified name arguments. '''
    input_name = end_check(input_name)
    output_name = end_check(output_name)
    return input_name, output_name


def build_dataframe(input_name: str):
    ''' Returns: Built dataframe structure. '''
    return pandas.read_csv(input_name, usecols=[
        'index', 'country', 'founded', 'id', 'industry',
        'linkedin_url', 'locality', 'name',
        'region', 'size', 'website'])


def gen_query(organisation: str):
    ''' Returns: Generated search queries for given name. '''
    indeed = f'{organisation} Indeed employee reviews'
    seek = f'{organisation} Seek employee reviews'
    glassdoor = f'{organisation} Glassdoor employee reviews'
    return [indeed, seek, glassdoor]


def google_search(queries: list, stop_point: int = 6):
    ''' Returns: Resulting Google search findings. '''
    results = []
    for query in queries:
        sleep(0.5)
        urls = list(search(query, num_results=stop_point))
        results.append(urls)
    return results


def clean_urls(results: list, scores: list):
    ''' Returns: Dictionary of potentially correct url links. '''
    valid_urls = {"indeed": [], "seek": [], "glassdoor": []}
    for list in range(2):
        for url in range(len(results[list])):
            if scores[list][url] > 0:
                if list == 0:
                    argument = "indeed"
                elif list == 1:
                    argument = "seek"
                else:
                    argument = "glassdoor"
                valid_urls[argument].append(results[list][url])
    return valid_urls


def validate_search(results: list, name: str, score_threshold: float = 0.4):
    ''' Returns: Most valid URLs if possible. '''
    valid_result, valid_scores = [], []
    regex = [r'https:\/\/(www|au)\.indeed\.com\/cmp\/(.*)\/reviews$',
             r'https:\/\/www\.seek\.com\.au\/companies\/(.*)\/reviews$',
             r'https:\/\/www\.glassdoor\.com\.au\/Reviews\/(.*)\.htm']
    part = [r'mp\/(.*?)\/', r'es\/(.*?)\/', r'ws\/(.*?)(\-R|.htm)']
    for index, list in enumerate(results):
        scoring = []
        for i, result in enumerate(list):
            if re.match(regex[index], result):
                url_name = re.search(part[index], result)[1]
                match_score = (SequenceMatcher(
                    None, url_name, name).ratio() / 4) * 3
                place_score = 0.25 - (0.05 * i)
                scoring.append(round(match_score + place_score, 2))
            else:
                scoring.append(0)
        max_score = max(scoring)
        if max_score > score_threshold:
            valid_result.append(list[scoring.index(max_score)])
        else:
            valid_result.append(None)
        valid_scores.append(scoring)
    return valid_result, valid_scores


def grab_HTML(url: str, start: int, website: str, country: str = None):
    ''' Returns: Selected webpage soup. '''
    try:
        if website == "Indeed":
            req = Request(
                f'{url}?start={start}&fcountry={country}',
                headers={'User-Agent': 'Mozilla/5.0'})
        elif website == "Glassdoor":
            req = Request(
                f'{url}',
                headers={'User-Agent': 'Mozilla/5.0'})
        elif website == "Seek":
            req = Request(
                f'{url}?page={start}',
                headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req)
        return BeautifulSoup(webpage, 'html.parser')
    except HTTPError as e:
        raise Exception(f'\nHTTP Error: \n{e.code}\n URL: {url}') from e
    except URLError as e:
        raise Exception(f'Bad URL: {url}') from e


def start_selenium(url: str):
    ''' Returns: Started Selenium based browser. '''
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    browser.implicitly_wait(5)
    browser.maximize_window()
    browser.get(url)
    sleep(5)
    return browser


def review_volume(soup, website: str, url=None):
    ''' Returns: Detected number reviews on website. '''
    if website == "Glassdoor":
        number_reviews = 0
    elif website == "Indeed":
        overview_data = soup.find(
            'div', attrs={'data-testid': 'review-count'})
        try:
            try:
                number_reviews = int(overview_data.find(
                    'span').find('b').text.replace(',', ''))
            except Exception:
                number_reviews = int(re.findall(
                    r'\d+', overview_data.find('span').text)[0])
        except AttributeError:
            number_reviews = 0
    elif website == "Seek":
        overview_data = soup.find('div', attrs={'id': 'app'})
        try:
            number_reviews = int((overview_data.text.split(
                "ReviewOverviewReviews"))[1].split("JobsTop")[0])
        except Exception:
            try:
                number_reviews = int(
                    re.findall(r'total rating from ([0-9]+)', overview_data.text)[0])
            except Exception:
                browser = start_selenium(url)
                reviews_element = browser.find_element(By.CSS_SELECTOR, f"a[href='{url[23:]}']")
                number_reviews = int(reviews_element.text.split()[0])
                browser.quit()
    return number_reviews


def scrape_count(links: list, country: str):
    ''' Returns: Number of reviews at link. '''
    if indeed_url := links[0]:
        indeed_soup = grab_HTML(indeed_url, 0, "Indeed", country)
        indeed_count = review_volume(indeed_soup, "Indeed")
    else:
        indeed_count = 0
    seek_url = links[1]
    if not seek_url or seek_url == seeks_reviews:
        seek_count = 0
    else:
        seek_soup = grab_HTML(seek_url, 1, "Seek")
        seek_count = review_volume(seek_soup, "Seek", seek_url)
    glassdoor_url = links[2]
    if not glassdoor_url or glassdoor_url in glassdoor_reviews:
        glassdoor_count = 0
    else:
        glassdoor_soup = grab_HTML(glassdoor_url, 0, "Glassdoor")
        glassdoor_count = review_volume(glassdoor_soup, "Glassdoor", glassdoor_url)
    return [indeed_count, seek_count, glassdoor_count]


def verify_dataframe_data(values):
    ''' Raises exception if wrong values found. '''
    sizes = ['1-10', '11-50', '51-200', '201-500',
             '501-1000', '1001-5000', '5001-10000', '10001+']
    if values[4] not in sizes:
        raise Exception("Invalid size value")
    try:
        float(values[5])
    except ValueError as e:
        raise Exception("Invalid founded value") from e
    if not values[6].startswith("linkedin.com/company/"):
        raise Exception("Invalid LinkedIn value")


def grab_dataframe_data(dic: dict, row: list):
    ''' Returns: Dictionary with row data and firm name. '''
    columns = ["index", "name", "industry",
               "region", "size", "founded", "linkedin_url"]
    values = [str(row[column]) for column in columns]
    verify_dataframe_data(values)
    for index, value in enumerate(values):
        dic[columns[index]].append(value)
    dic['correct'].append("Unknown")
    return dic


def append_data(dic: dict, valid_urls: dict, links: list, scores: list, counts: list):
    ''' Returns: Dictionary with all collected data appended. '''
    dic['valid_urls'].append(valid_urls)
    dic['indeed_url'].append(links[0])
    dic['seek_url'].append(links[1])
    dic['glassdoor_url'].append(links[2])
    dic['scores'].append(scores)
    dic['indeed_reviews'].append(counts[0])
    dic['seek_reviews'].append(counts[1])
    dic['glassdoor_reviews'].append(counts[2])
    dic['total_reviews'].append(sum(counts))
    return dic


def data_attach(dic: dict, row: list, country: str, manual: bool = False):
    ''' Returns: Collected data attached to dictionary. '''
    name = row['name']
    if not manual:
        queries = gen_query(name)
        results = google_search(queries)
        links, scores = validate_search(results, name)
        valid_urls = clean_urls(results, scores)
    else:
        print(f'Organisation: {name}')
        print(f'LinkedIn: https://{row["linkedin_url"]}')
        indeed_url = input("Indeed URL: ")
        seek_url = input("Seek URL: ")
        glassdoor_url = input("Glassdoor URL: ")
        links = [indeed_url, seek_url, glassdoor_url]
        valid_urls = {"indeed": [], "seek": [], "glassdoor": []}
        scores = [[], [], []]
    counts = scrape_count(links, country)
    dic = grab_dataframe_data(dic, row)
    return append_data(dic, valid_urls, links, scores, counts)


def append_CSV(filename: str, dic: dict):
    ''' Returns: Built and named CSV file containing data. '''
    file_exists = os.path.isfile(f'links/{filename}')
    with open(f'links/{filename}', 'a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', lineterminator='\n')
        headers = list(dic.keys())
        if not file_exists:
            writer.writerow(headers)
        length = len(dic['name'])
        for i in range(length):
            data = [dic[column][i] for column in headers]
            writer.writerow(data)


def error_handling(filename: str, errors: list, dataframe):
    ''' Returns: Generated csv of all rows which errored. '''
    data = []
    with open(f'links/{filename[:-4]}_Error_Log.txt', 'a') as log:
        log.write(f'\n\n{errors}')
    filename = f'{filename[:-4]}_Error_Rows.csv'
    with open(f'links/{filename}', 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', lineterminator='\n')
        writer.writerow(['error', 'index', 'country', 'founded', 'id', 'industry',
                        'linkedin_url', 'locality', 'name', 'region', 'size', 'website'])
        data.extend([index] + list(dataframe.iloc[index]) for index in errors)
        print("Building Error CSV")
        for row in tqdm(data):
            writer.writerow(row)
    print(f"Error Indexes: \n{errors}")


def grab_review_data(output_name: str, input_name: str, country: str = "AU", start: int = 0):
    ''' Returns: Generated CSV of links and additional data. '''
    output_name, input_name = verify_names(output_name, input_name)
    dataframe = build_dataframe(input_name)
    dic = dictionary_build()
    lines = len(dataframe.index)
    errors = []
    print("Collecting Data")
    if os.path.exists(f'links/{output_name[:-4]}_Error_Log.txt'):
        os.remove(f'links/{output_name[:-4]}_Error_Log.txt')
    for index, row in tqdm(dataframe.iterrows(), total=lines):
        if index < start:
            continue
        try:
            dic = data_attach(dic, row, country)
            if index % 100 == 0:
                append_CSV(output_name, dic)
                dic = dictionary_build()
        except KeyboardInterrupt:
            halt()
        except Exception as e:
            with open(f'links/{output_name[:-4]}_Error_Log.txt', 'a') as log:
                print(f"\nRow Failed: {index}")
                log.write(f'Row Failed: {index}\n')
                log.write(str(e))
                log.write(f'{traceback.format_exc()}\n\n')
                errors.append(index)
                continue
    append_CSV(output_name, dic)
    if errors:
        print("Errors Detected...")
        error_handling(output_name, errors, dataframe)


#grab_review_data("New_AUS_1001+_Links", "companies/AUS_1001+_Data")


def manual_error_handling(filename: str, country: str = "AU"):
    ''' Returns: Same file with manually handled errors appended. '''
    if not filename.endswith('.csv'):
        filename += '.csv'
    dataframe = build_dataframe(f'links/{filename[:-4]}_Error_Rows.csv')
    lines = len(dataframe.index)
    print(f"Found {lines} to correct")
    dic = dictionary_build()
    for _, row in dataframe.iterrows():
        dic = data_attach(dic, row, country, manual=True)
    append_CSV(filename, dic)


manual_error_handling("New_AUS_1001+_Links")


def pull_specific_data(output_name: str, input_name: str, size_list: list):
    ''' Returns: CSV of organisations of listed size from listed country. '''
    if not output_name.endswith(".csv"):
        output_name += ".csv"
    if not input_name.endswith(".csv"):
        input_name += ".csv"
    df = dd.read_csv(f'links/{input_name}', low_memory=False,
                     on_bad_lines='error', encoding='utf8')
    df_selected = df[(df['size'].isin(size_list))]
    df_selected.compute().to_csv(f'links/{output_name}', index=False,
                                 header=headers)


# pull_specific_data("AUS_1001+_Links", "AUS_501+_Links", any_size[5:])
