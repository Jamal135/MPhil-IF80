# Creation Date: 07/06/2022

import pandas as pd

def load_CSV(filename: str, drop_list: list = None):
    ''' Returns: CSV loaded to dataframe with select columns dropped. '''
    if drop_list is None:
        drop_list = []
    dataframe = pd.read_csv(f"{filename}.csv")
    if drop_list is not None:
        dataframe.drop(drop_list, axis=1, inplace=True)
    return dataframe


def length(filename: str, number: int, column: str, drop_list: list = None):
    ''' Returns: CSV of the top 100 longest values in selected column. '''
    df = load_CSV(filename, drop_list)
    df['length'] = df[column].str.len()
    df.sort_values('length', ascending=False, inplace=True)
    data = df[column][:number]
    data.to_csv(f"{filename}-{column}-{number}.csv", sep='\t')


length("analysis/Large-Reviews-Data", 100, "Review")