# Creation Date: 10/02/2022

from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
from difflib import SequenceMatcher
from googlesearch import search
from bs4 import BeautifulSoup
from time import sleep
from tqdm import tqdm
import traceback
import os.path
import pandas
import csv
import sys
import re
import os

# Seeks own reviews seems to break stuff...
seeks_reviews = "https://www.seek.com.au/companies/seek-432600/reviews"


def halt():
    print("\nInterrupted")
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)


def dictionary_build():
    return {
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
                                'country', 'founded', 'id', 'industry',
                                'linkedin_url', 'locality', 'name',
                                'region', 'size', 'website'])


def gen_query(organisation: str):
    ''' Returns: Generated search queries for given name. '''
    indeed = f'{organisation} Indeed employee reviews'
    seek = f'{organisation} Seek employee reviews'
    return [indeed, seek]


def google_search(queries: list, stop_point: int = 6):
    ''' Returns: Resulting Google search findings. '''
    results = []
    for query in queries:
        sleep(0.5)
        urls = list(search(query, stop=stop_point))
        results.append(urls)
    return results


def clean_urls(results: list, scores: list):
    ''' Returns: Dictionary of potentially correct url links. '''
    valid_urls = {"indeed": [], "seek": []}
    for list in range(2):
        for url in range(len(results[list])):
            if scores[list][url] > 0:
                valid_urls['indeed' if list == 0 else 'seek'].append(
                    results[list][url])
    return valid_urls


def validate_search(results: list, name: str, score_threshold: float = 0.4):
    ''' Returns: Most valid URLs if possible. '''
    valid_result, valid_scores = [], []
    regex = [r'https:\/\/(www|au)\.indeed\.com\/cmp\/(.*)\/reviews$',
             r'https:\/\/www\.seek\.com\.au\/companies\/(.*)\/reviews$']
    part = [r'mp\/(.*?)\/', r'es\/(.*?)\/']
    for index, list in enumerate(results):
        scoring = []
        for i, result in enumerate(list):
            if re.match(regex[index], result):
                url_name = re.search(part[index], result).group(1)
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


def grab_HTML(url: str, start: int):
    ''' Returns: Selected webpage soup. '''
    for _ in range(15):
        try:
            req = Request(f'{url}?start=' + str(start),
                          headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req)
            return BeautifulSoup(webpage, 'html.parser')
        except HTTPError as e:
            print(f'\nHTTP Error: \n{e.code}')
            continue
        except URLError as e:
            print(f'\nURL Error: \n{e.reason}')
            raise Exception(f"Bad URL: {url}") from e
    raise Exception(f"Failed to get HTML: {url}")


def review_volume(soup, website: str):
    ''' Returns: Detected number reviews on website. '''
    if website == "Indeed":
        overview_data = soup.find(
            'div', attrs={'data-testid': 'review-count'})
        try:
            number_reviews = int(overview_data.find(
                'span').find('b').text.replace(',', ''))
        except:
            number_reviews = int(re.findall(
                r'\d+', overview_data.find('span').text)[0])
    elif website == "Seek":
        overview_data = soup.find('div', attrs={'id': 'app'})
        number_reviews = int((overview_data.text.split(
            "ReviewOverviewReviews"))[1].split("JobsTop")[0])
    return number_reviews


def scrape_count(links: list):
    ''' Returns: Number of reviews at link. '''
    indeed_url = links[0]
    if indeed_url is None:
        indeed_count = 0
    else:
        indeed_soup = grab_HTML(indeed_url, 0)
        indeed_count = review_volume(indeed_soup, "Indeed")
    seek_url = links[1]
    if seek_url is None or seek_url == seeks_reviews:
        seek_count = 0
    else:
        seek_soup = grab_HTML(seek_url, 1)
        seek_count = review_volume(seek_soup, "Seek")
    return [indeed_count, seek_count]


def verify_dataframe_data(values):
    ''' Raises exception if wrong values found. '''
    sizes = ['1-10', '11-50', '51-200', '201-500', '501-1000', '1001-5000', '5001-10000', '10001+']
    if values[3] not in sizes:
        raise Exception("Invalid size value")
    try:
        float(values[4])
    except ValueError as e:
        raise Exception("Invalid founded value") from e
    if not values[5].startswith("linkedin.com/company/"):
        raise Exception("Invalid LinkedIn value")


def grab_dataframe_data(dic: dict, row: list):
    ''' Returns: Dictionary with row data and firm name. '''
    columns = ["name", "industry", "region", "size", "founded", "linkedin_url"]
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
    dic['scores'].append(scores)
    dic['indeed_reviews'].append(counts[0])
    dic['seek_reviews'].append(counts[1])
    dic['total_reviews'].append(sum(counts))
    return dic


def append_CSV(filename: str, dic: dict):
    ''' Returns: Built and named CSV file containing data. '''
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', lineterminator='\n')
        headers = list(dic.keys())
        if not file_exists:
            writer.writerow(headers)
        length = len(dic['name'])
        print("Building CSV")
        for i in tqdm(range(length)):
            data = [dic[column][i] for column in headers]
            writer.writerow(data)


def error_handling(filename: str, errors: list, dataframe):
    ''' Returns: Generated csv of all rows which errored. '''
    data = []
    filename = f'{filename[:-4]}_Errors{filename[-4:]}'
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', lineterminator='\n')
        if not file_exists:
            writer.writerow(["index", "data"])
        data.extend([index] + list(dataframe.iloc[index]) for index in errors)
        print("Building Error CSV")
        for row in tqdm(data):
            writer.writerow(row)
    print(f"Error Indexes: \n{errors}")


def grab_review_data(output_name: str, input_name: str):
    ''' Returns: Generated CSV of links and additional data. '''
    output_name, input_name = verify_names(output_name, input_name)
    dataframe = build_dataframe(input_name)
    dic = dictionary_build()
    lines = len(dataframe.index)
    errors = []
    print("Collecting Data")
    for index, row in tqdm(dataframe.iterrows(), total=lines):
        try:
            name = row['name']
            queries = gen_query(name)
            results = google_search(queries)
            links, scores = validate_search(results, name)
            valid_urls = clean_urls(results, scores)
            counts = scrape_count(links)
            dic = grab_dataframe_data(dic, row)
            dic = append_data(dic, valid_urls, links, scores, counts)
        except KeyboardInterrupt:
            halt()
        except:
            print(f"\nRow Failed: {index}")
            traceback.print_exc()
            errors.append(index)
            continue
    append_CSV(output_name, dic)
    if errors:
        print("Errors Detected...")
        error_handling(input_name, errors, dataframe)


grab_review_data("results", "AUS_5001+_Data")
