# Creation Date: 10/02/2022

from difflib import SequenceMatcher
from googlesearch import search
from bs4 import BeautifulSoup
import urllib.request as lib
from time import sleep
import pandas
import tqdm
import re

# Seeks own reviews seems to break stuff...
seeks_reviews = "https://www.seek.com.au/companies/seek-432600/reviews"

def gen_query(organisation: str):
    ''' Returns: Generated search queries for given name. '''
    indeed = f'{organisation} Indeed employee reviews'
    seek = f'{organisation} Seek employee reviews'
    return [indeed, seek]


def google_search(queries: list, stop_point: int = 5):
    ''' Returns: Resulting Google search findings. '''
    results = []
    for query in queries:
        urls = list(search(query, stop=stop_point))
        results.append(urls)
    print(results)
    return results


def validate_search(results: list, name: str, score_threshold: float = 0.38):
    ''' Returns: Most valid URLs if possible. '''
    valid_result = []
    regex = [r'https:\/\/(www|au)\.indeed\.com\/cmp\/(.*)\/reviews$', 
             r'https:\/\/www\.seek\.com\.au\/companies\/(.*)\/reviews$']
    part = [r'mp\/(.*?)\/', r'es\/(.*?)\/']
    for index, list in enumerate(results):
        scoring = []
        for result in list:
            if re.match(regex[index], result):
                url_name = re.search(part[index], result).group(1)
                scoring.append(SequenceMatcher(None, url_name, name).ratio())
            else:
                scoring.append(0)
        print(scoring)
        max_score = max(scoring)
        if max_score > score_threshold:
            valid_result.append(list[scoring.index(max_score)])
        else:
            valid_result.append(None)
    return valid_result


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


def grab_review_data():
    ''' Returns: '''
    dataframe = pandas.read_csv('AUS_NZ_refined_list.csv', usecols=[
                                'country', 'founded', 'id', 'industry', 
                                'linkedin_url', 'locality', 'name', 
                                'region', 'size', 'website'])
    for index, row in dataframe.iterrows():
        name = row['name']
        print(name)
        try:
            queries = gen_query(name)
            results = google_search(queries)
            links = validate_search(results, name)
            print(links)
            counts = scrape_count(links)
            print(counts)
        except:
            print(str(index) + " skipped: " + name)

grab_review_data()

# Make score based url selection optional relative to first fitting url.