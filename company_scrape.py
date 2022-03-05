# Creation Date: 10/02/2022

import dask.dataframe as dd
# Download dataset CSV: https://www.peopledatalabs.com/company-dataset?creative=526382233178&keyword=company%20dataset&matchtype=p&network=g&device=c&utm_medium=search&utm_term=company%20dataset&utm_campaign=Free%20Datasets%20-%20Itnl&utm_source=google&hsa_tgt=kwd-440039917377&hsa_net=ppc&hsa_src=g&hsa_kw=company%20dataset&hsa_cam=2064790728&hsa_ver=3&hsa_ad=526382233178&hsa_mt=p&hsa_acc=3068533947&hsa_grp=124908126682&gclid=Cj0KCQiA_c-OBhDFARIsAIFg3ex2_yeQAkkNJjAwavKDfHQBtCw7jNp9Hx6S_cAqcyBW9wcU7Oz8gAIaAs2iEALw_wcB


def pull_company_data(output_name, country_list, size_list):
    ''' Returns: CSV of organisations of listed size from listed country. '''
    if not output_name.endswith(".csv"):
        output_name += ".csv"
    df = dd.read_csv("free_company_dataset.csv", error_bad_lines=False)
    df_selected = df[(df['country'].isin(country_list))
                     & (df['size'].isin(size_list))]
    df_selected.compute().to_csv(output_name)


pull_company_data("AUS_51+_Data",
                  ['australia'], ['51-200', '201-500', '501-1000', '1001-5000', '5001-10000', '10001+'])
