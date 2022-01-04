import dask.dataframe as dd

# Download dataset CSV: https://www.peopledatalabs.com/company-dataset?creative=526382233178&keyword=company%20dataset&matchtype=p&network=g&device=c&utm_medium=search&utm_term=company%20dataset&utm_campaign=Free%20Datasets%20-%20Itnl&utm_source=google&hsa_tgt=kwd-440039917377&hsa_net=ppc&hsa_src=g&hsa_kw=company%20dataset&hsa_cam=2064790728&hsa_ver=3&hsa_ad=526382233178&hsa_mt=p&hsa_acc=3068533947&hsa_grp=124908126682&gclid=Cj0KCQiA_c-OBhDFARIsAIFg3ex2_yeQAkkNJjAwavKDfHQBtCw7jNp9Hx6S_cAqcyBW9wcU7Oz8gAIaAs2iEALw_wcB
df = dd.read_csv("free_company_dataset.csv", error_bad_lines=False)

# Define which country and size you care about
country_list = ['australia', 'new_zealand', 'united states', 'canada', 'united kingdom']
size_list = ['5001-10000', '10001+']

df_selected = df[(df['country'].isin(country_list)) & (df['size'].isin(size_list))]
df_selected.compute().to_csv('refined_list.csv')