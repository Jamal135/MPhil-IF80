# Creation Date: 10/02/2022

from difflib import SequenceMatcher
from googlesearch import search
from bs4 import BeautifulSoup
import urllib.request as lib
from time import sleep
from tqdm import tqdm
import os.path
import pandas
import csv
import re

# Seeks own reviews seems to break stuff...
seeks_reviews = "https://www.seek.com.au/companies/seek-432600/reviews"


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
        'urls': []
    }


def gen_query(organisation: str, specific_site: bool = False):
    ''' Returns: Generated search queries for given name. '''
    if specific_site:
        indeed = f'site:indeed.com {organisation} Indeed employee reviews'
        seek = f'site:seek.com.au {organisation} Seek employee reviews'
    else:
        indeed = f'{organisation} Indeed employee reviews'
        seek = f'{organisation} Seek employee reviews'
    return [indeed, seek]


def google_search(queries: list, stop_point: int = 5):
    ''' Returns: Resulting Google search findings. '''
    results = []
    for query in queries:
        sleep(0.5)
        urls = list(search(query, stop=stop_point))
        results.append(urls)
    return results


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


def grab_HTML(url, start):
    ''' Returns: Selected webpage soup. '''
    for _ in range(15):
        try:
            req = lib.Request(f'{url}?start=' + str(start),
                              headers={'User-Agent': 'Mozilla/5.0'})
            webpage = lib.urlopen(req)
            return BeautifulSoup(webpage, 'html.parser')
        except:
            sleep(5)
            continue
    print("Failed to grab HTML")
    exit(0)


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


def append_CSV(filename, dic):
    ''' Returns: Built and named CSV file containing data. '''
    if not filename.endswith(".csv"):
        filename += ".csv"
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


def grab_dataframe_data(dic, row):
    ''' Returns: Dictionary with row data and firm name. '''
    columns = ["name", "industry", "region", "size", "founded", "linkedin_url"]
    for column in columns:
        dic[column].append(row[column])
    dic['correct'].append("Unknown")
    return dic, row['name']


def grab_review_data(output_name, input_name):
    ''' Returns: '''
    if not input_name.endswith(".csv"):
        input_name += ".csv"
    dataframe = pandas.read_csv(input_name, usecols=[
                                'country', 'founded', 'id', 'industry',
                                'linkedin_url', 'locality', 'name',
                                'region', 'size', 'website'])
    dic = dictionary_build()
    lines = len(dataframe.index)
    print("Collecting Data")
    for _, row in tqdm(dataframe.iterrows(), total=lines):
        sleep(0.5)
        dic, name = grab_dataframe_data(dic, row)
        queries = gen_query(name)
        results = google_search(queries)
        dic['urls'].append(results)
        links, scores = validate_search(results, name)
        dic['indeed_url'].append(links[0])
        dic['seek_url'].append(links[1])
        dic['scores'].append(scores)
        counts = scrape_count(links)
        dic['indeed_reviews'].append(counts[0])
        dic['seek_reviews'].append(counts[1])
        dic['total_reviews'].append(sum(counts))
    append_CSV(output_name, dic)


grab_review_data("results", "test")

# Make score based url selection optional relative to first fitting url.
