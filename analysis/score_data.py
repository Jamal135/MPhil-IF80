# Creation Date: 10/02/2022

from tqdm import tqdm
import pandas


def build_dataframe(input_name: str):
    ''' Returns: Built dataframe structure. '''
    return pandas.read_csv(input_name, usecols=[
        'name', 'industry', 'region', 'size', 'founded',
        'linkedin_url', 'indeed_url', 'indeed_reviews',
        'seek_url', 'seek_reviews', 'total_reviews',
        'correct', 'scores', 'valid_urls'])


def total_review_count(input_name: str):
    ''' Returns: Total number of reviews. '''
    dataframe = build_dataframe(input_name)
    return sum(
        int(row['total_reviews'])
        for _, row in dataframe.iterrows()
    )

def conditional_review_count(input_name: str, threshold: int = 50):
    ''' Returns: Conditional total number of reviews. '''
    dataframe = build_dataframe(input_name)
    review_total = 0
    for _, row in dataframe.iterrows():
        row_value = int(row['total_reviews'])
        if row_value >= threshold:
            review_total += row_value
    return review_total


def calculate_counts(input_name: str):
    ''' Returns: Review counts and over 50 review count. '''
    if not input_name.endswith(".csv"):
        input_name += ".csv"
    general_total = total_review_count(input_name)
    print(f'Overall total number reviews: {general_total}')
    threshold_total = conditional_review_count(input_name)
    print(f'Total with over 50 reviews: {threshold_total}')


calculate_counts("links/AUS_501+_Links.csv")