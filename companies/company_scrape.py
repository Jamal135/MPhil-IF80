# Creation Date: 10/02/2022

import dask.dataframe as dd
import pandas as pd
import contextlib
import csv
import os
import re


# Download dataset CSV: https://www.peopledatalabs.com/company-dataset?creative=526382233178&keyword=company%20dataset&matchtype=p&network=g&device=c&utm_medium=search&utm_term=company%20dataset&utm_campaign=Free%20Datasets%20-%20Itnl&utm_source=google&hsa_tgt=kwd-440039917377&hsa_net=ppc&hsa_src=g&hsa_kw=company%20dataset&hsa_cam=2064790728&hsa_ver=3&hsa_ad=526382233178&hsa_mt=p&hsa_acc=3068533947&hsa_grp=124908126682&gclid=Cj0KCQiA_c-OBhDFARIsAIFg3ex2_yeQAkkNJjAwavKDfHQBtCw7jNp9Hx6S_cAqcyBW9wcU7Oz8gAIaAs2iEALw_wcB
log_location = "companies/error_log.txt"
any_size = ['1-10', '11-50', '51-200', '201-500',
            '501-1000', '1001-5000', '5001-10000', '10001+']
main_countries = ['australia', 'canada',
                  'new zealand', 'united kingdom', 'united states']


def log_errors(output_name: str, country_list: list, size_list: list):
    ''' Purpose: Enables checking of all lines which errored. '''
    with open(log_location, 'r') as file:
        data = file.read().replace('\n', '')
    error_lines = re.findall(r'Skipping line ([0-9]+):', data)
    print(f"Found {len(error_lines)} lines that can't load.")
    print(error_lines)
    with open("companies/free_company_dataset.csv", encoding='utf8') as sample:
        csv_reader = csv.reader(sample)
        rows = list(csv_reader)
        error_list = []
        for index in error_lines:
            row_data = rows[int(index)]
            if any(country in row_data for country in country_list) and any(
                size in row_data for size in size_list):
                error_list.append(row_data)
    with open(f'companies/{output_name[:-4]}_Errors.csv', 'w', encoding='utf8', newline='') as errors:
        writer = csv.writer(errors)
        writer.writerows(error_list)


def build_company_data(output_name: str, country_list: list, size_list: list):
    ''' Returns: CSV of organisations of listed size from listed country. '''
    if not output_name.endswith(".csv"):
        output_name += ".csv"
    if os.path.exists(log_location):
        os.remove(log_location)
    with open(log_location, 'x') as log:
        with contextlib.redirect_stderr(log):
            df = dd.read_csv("companies/free_company_dataset.csv", low_memory=False,
                             on_bad_lines='warn', encoding='utf8', lineterminator='\n')
            df_selected = df[(df['country'].isin(country_list))
                             & (df['size'].isin(size_list))]
            df_selected.compute().to_csv(f'companies/{output_name}')
    log_errors(output_name, country_list, size_list)


build_company_data("Focus_Company_List", main_countries, any_size[4:])


def pull_specific_data(output_name: str, country_list: list, size_list: list):
    ''' Returns: CSV of organisations of listed size from listed country. '''
    if not output_name.endswith(".csv"):
        output_name += ".csv"
    df = dd.read_csv("companies/free_company_dataset.csv",
                     on_bad_lines='error', encoding='utf8')
    df_selected = df[(df['country'].isin(country_list))
                     & (df['size'].isin(size_list))]
    df_selected.compute().to_csv(f'companies/{output_name}')


# pull_specific_data("Australia_1001+_Data",
#                   ["australia"], ['1001-5000', '5001-10000', '10001+'])
