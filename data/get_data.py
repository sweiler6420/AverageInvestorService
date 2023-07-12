
from configparser import ConfigParser
from datetime import datetime
import os
import requests
import pandas as pd
import time

def getConfigVars():
    """Used to retrieve config credentials from config.ini in AWS.
    Overview:
    ----
    Have multiple config vars saved in a config.ini file
    Returns:
    ----
    {config} -- Returns a config obj from the ConfigParser library
    """
    config = ConfigParser()
    folder = os.path.dirname(os.path.abspath(__file__))
    configFile = os.path.join(folder, 'config.ini')

    config.read(configFile)

    return config

def getData(stock, month):
    """Used to get dataframe of specific month for a specific ticker symbol from alphavantage
    Overview:
    ----
    calls url with request library and set the return data to a df
    Arguments:
    ----
    stock {str} -- stock ticker symbol to be searched for
    month {str} -- yyyy-mm str used in the alphavantage url query parameter for a specific month in time to return values for
    Returns:
    ----
    {pandas.DataFrame} -- holds HLOCV of data
    """
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={stock}&interval=5min&month={month}&outputsize=full&apikey={config.get('ec2', 'ALPHAVANTAGE_API_KEY')}"
    r = requests.get(url)
    data = r.json()

    df = pd.DataFrame.from_dict(data['Time Series (5min)'], orient='index')

    return df

def updateProgressBar(progress):
    """Used to iterate the progress bar
    Overview:
    ----
    updates the next index to a "-" to show progress
    Arguments:
    ----
    progress {list} -- The current progress list that needs to be iterated to the next progress step
    Returns:
    ----
    {list} -- holds a representational list of char that has "step" amount of empty space to be "updated" per loop execution
        ex. |                |
        ex. |-               |
        ex. |--              |
    """
    index = progress.index(' ')
    progress[index] = '-'
    return progress


def initProgress(date_list):
    """Used to create the progress list
    Overview:
    ----
    creates a list of chars that represent the progress of the URL requests
    Arguments:
    ----
    date_list {list} -- The list of yyyy-mm dates that need to be interated through to receive all the data from alphavantage
    Returns:
    ----
    {list} -- holds a representational list of char that has "step" amount of empty space to be "updated" per loop execution
        ex. |                |
        ex. |-               |
        ex. |--              |
    """
    length = len(date_list)

    progress = ['|']
    for i in range(length):
        progress.append(' ')

    progress.append('|')

    return progress


def getLatestData(stock_id, ticker, date_list):
    """Used to retrieve the newest data that needs to be added to the db
    Overview:
    ----
    Using the requests library, grab the latest data using a free api key from alpha vantage. Convert it to a json, then to a dataframe.
    This causes the datetime to be index so we swap that to a column and reset the index. Next we normalize the column names to our table column
    names in the db. From here i convert the datetime column to a datetime object. This allows us to split the column into a date and time columns.
    Next we get all the columns but the datetime column in a list, and use that list to convert all the data to a numeric value so that i can
    enforce the rounding to match the db. Next we split that datetime into a date and time column. Then drop the datetime column. Lastly we
    grab all the data that is greater than or equal our max date. Then remove all the times that we already have in our db for that max date. 
    This leaves us with only new data. We add the stock id column. But since we are only giving a time range from 8 to 5 pm we have to remove
    the times that lie outside that rule.
    Arguments:
    ----
    max_date {datetime.date} -- The max date that exists for that stock id in the db.
    max_time {datetime.time} -- The max time that exists for the max date for that stock id in the db.
    stock_id {str} -- The stock_id for that stock id in the db. This is a str but gets converted to a uuid when inserting
    Returns:
    ----
    {pandas.DataFrame} -- This holds all the new data, normalized, that need to be inserted into the db
    """
    
    df = pd.DataFrame()

    # init progress bar list for displaying progress of calls remaining
    progress = initProgress(date_list)

    for date in date_list:
        # Progress Display
        progress = updateProgressBar(progress)
        print(''.join(progress))
        # Get Data and append to dataframe
        temp_df = getData(ticker, date)
        df = df.append(temp_df)

        # Sleep to throttle api calls to less than 5 per minute
        time.sleep(10)

    df['datetime'] = df.index
    df = df.reset_index(drop=True)

    df = df.rename(columns={"1. open": "open_price", "2. high": "high_price", "3. low": "low_price", "4. close": "close_price", "5. volume": "volume"})

    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
    cols = df.columns.drop('datetime')
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

    # Normalize columns
    df = df.round({'open_price': 2, 'high_price': 2, 'low_price': 2, 'close_price': 2})

    df['date'] = [d.date() for d in df['datetime']]
    df['time'] = [d.time() for d in df['datetime']]

    df = df.drop(['datetime'], axis=1)

    df['stock_id'] = stock_id

    df = df[((df.time >= datetime.strptime('08:05:00', '%H:%M:%S').time()) & (df.time <= datetime.strptime('17:00:00', '%H:%M:%S').time()))]

    return df



if __name__ == "__main__":
    # Create list of yyyy-mm months between dates for all the URLs
    date_list = pd.date_range('2020-01-01','2023-07-01', freq='MS').strftime("%Y-%m").tolist()

    # Creating config in order to grab api key
    global config
    config = getConfigVars()

    # Ticker symbol we want data for
    ticker = 'msft'
    stock_id = '50f5fac4-1712-49a4-a43a-d01e92ff66d7'

    # Getting the full dataframe for all the dates in the date list
    data = getLatestData(stock_id, ticker, date_list=date_list)
    
    # Getting abs path of current dir
    output_folder = os.path.dirname(os.path.abspath(__file__))
    # Add the file name to the folder path
    output_file = os.path.join(output_folder, f'{ticker}_export.csv')

    # Save the data to a csv for easy importing and inserting into db
    data.to_csv(output_file, encoding='utf-8', index=False)
