#!/home/mkultra/miniconda3.7/bin/python

import os
import requests
from lxml.html import fromstring

import datetime
import numpy as np
import pandas as pd


# Check if we are in the jupyter "notebooks" directory
## If so then we must change the current working directory 1 level higher
if os.getcwd().split("/")[-1] == "notebooks":
    os.chdir("../")

# Create path to save final data
if not os.path.exists(os.getcwd()+"/bitinfocharts-data/"):
    os.makedirs(os.getcwd()+"/bitinfocharts-data/")

# save path to var data_path
data_path = os.getcwd()+"/bitinfocharts-data"



def chart_data_to_pickled_dataframe(url_endpoint, coin_ticker, path):
    
    
    start_str = 'Dygraph(document.getElementById("container"),'
    end_str = ', {labels: ["Date",'
    
    value_column_name = url_endpoint.split("-")[0]

    # Make the request to bitinfo server
    root = fromstring(requests.get("https://bitinfocharts.com/comparison/{}".format(url_endpoint), allow_redirects=True).content)

    # Scrape using Xpath
    data = [i.text for i in root.xpath("//*") if start_str in str(i.text)][0]

    # Determine the positions to cut the resulting xpath string
    start_str_position = data.find(start_str) + len(start_str)
    end_str_position = data.find(end_str)

    # Clean up the data string & then evaluate the string into list of lists
    series_data_str = data[start_str_position:end_str_position].replace("new Date(","").replace(")","").replace("null","np.nan")
    series_data = eval(series_data_str)

    # Convert Date Strings to Datetime Objects & store resulting lists into a dict
    series_dict = dict()
    series_dict["Date"] = [datetime.datetime.strptime(i[0],"%Y/%m/%d") for i in series_data]
    series_dict[value_column_name] = [float(i[1]) for i in series_data]

    # Create Pandas DataFrame from dict
    df = pd.DataFrame(series_dict)
    
    df.set_index("Date",inplace=True)
    
    # If a directory for a coin does not exist then create it
    if not os.path.exists(path):
        os.mkdir(path)
    
    # Save the pandas dataframe to pickled file
    pd.to_pickle(df, path+"/{}_pandasDF.pickle".format(value_column_name))
    
    del df
    
def curate_feature_set(dataframe):    
    dataframe["coin_per_terahash"] = dataframe['mining_profitability'].values / dataframe['price'].values
    dataframe["coin_total_supply"] = dataframe['marketcap'].values / dataframe['price'].values
    dataframe["difficulty_change"] = dataframe['difficulty'].pct_change()
    dataframe["hashrate_change"] = dataframe['hashrate'].pct_change()
    dataframe["top100cap_change"] = dataframe['top100cap'].pct_change()
    dataframe["transactions_change"] =dataframe['transactions'].pct_change()
    
    # Remove unwanted features
    dataframe.drop(columns=['mining_profitability','marketcap','difficulty'],inplace=True)
    
    return dataframe
    

    
    
def create_master_dataframe(coin_ticker):
    
    # create path to save temporary processing data
    os.makedirs(os.getcwd()+"/tmp/{}/".format(coin_ticker))
    tmp_path = os.getcwd()+"/tmp/{}".format(coin_ticker)
    
    
    bitinfocharts_url_endpoints_list = [
    'transactions-',
    'size-',
    'sentbyaddress-',
    'difficulty-',
    'hashrate-',
    'price-',
    'mining_profitability-',
    'sentinusd-',
    'transactionfees-',
    'median_transaction_fee-',
    'confirmationtime-',
    'marketcap-',
    'transactionvalue-',
    'tweets-',
    'google_trends-',
    'activeaddresses-',
    'top100cap-']
    
    bitinfocharts_url_endpoints_list = [endpoint+coin_ticker+".html" for endpoint in bitinfocharts_url_endpoints_list]
    
    
    for url in bitinfocharts_url_endpoints_list:
        chart_data_to_pickled_dataframe(url_endpoint=url, coin_ticker=coin_ticker, path=tmp_path)
    
    # List the current tmp dataframes that we use to build master
    chart_files = os.listdir(tmp_path)
    
    #Load first DataFrame
    chart_files.remove("size_pandasDF.pickle")
    master_df = pd.read_pickle(tmp_path+"/size_pandasDF.pickle")

    # Concat Remaining Chartfiles
    for filename in chart_files:
        df_temp = pd.read_pickle(tmp_path+"/"+filename)
        master_df = pd.concat([master_df, df_temp], axis=1)

        del df_temp

    # Custom Create-Add and then Remove Features    
    master_df = curate_feature_set(dataframe=master_df)
    
    
    # Save the pandas dataframe to pickled file
    pd.to_pickle(master_df[:-2], data_path+"/{}.pickle".format(coin_ticker))

    # Remove all supporting files and the supporting folder
    # we have saved the master and thats all we need
    for i in os.listdir(path=tmp_path):
        os.remove(tmp_path+"/{}".format(i))
    os.rmdir(tmp_path)
    
    # remove the temp directory as well
    os.rmdir(os.getcwd()+"/tmp/")
        

def load_bitinfocharts_dataframe(coin_ticker):
    
    if os.path.exists(data_path+"/{}.pickle".format(coin_ticker)):
        master_df = pd.read_pickle(data_path+"/{}.pickle".format(coin_ticker))
        return master_df
    
    else:
        raise('This data frame has not been been created.\nPlease try: create_master_dataframe(coin_ticker="{}")'.format(coin_ticker))


def update_all():
    
    coin_list=["btc","eth","ltc","xrp","bch","etc","zec","dash","bsv","xmr","doge","btg","vtc","ppc","rdd","nmc","blk","ftc","nvc"]
    
    for coin in coin_list:
        create_master_dataframe(coin_ticker=coin)
