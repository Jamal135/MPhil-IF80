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
    if not input_name.endswith(".csv"):
        input_name += ".csv"
    dataframe = build_dataframe(input_name)
    lines = len(dataframe.index)
    return sum(
        int(row['total_reviews'])
        for _, row in tqdm(dataframe.iterrows(), total=lines)
    )

print(total_review_count('results'))