# Creation Date: 07/06/2022

import pandas as pd

def load_CSV(filename: str, drop_list: list = None, skip: bool = False):
    ''' Returns: CSV loaded to dataframe with select columns dropped. '''
    if drop_list is None:
        drop_list = []
    if skip:
        dataframe = pd.read_csv(f"{filename}.csv", on_bad_lines="skip")
    else:
        dataframe = pd.read_csv(f'{filename}.csv')
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

def number(filename: str, column: str, value: str = None, drop_list: list = None):
    ''' Returns: Data on the number of each or a specific value in column. '''
    df = load_CSV(filename, drop_list, True)
    if value != None:
        print(df[column].value_counts()[value])
    else:
        print(df[column].value_counts())

number("companies/PDL_Company_Dataset", "country", "australia")