from configparser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from datetime import datetime
import pandas as pd
# import yfinance as yf
import requests
import psycopg2
import boto3
import json
import os

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

    
def getDbCreds():
    """Used to retrieve database credentials from secrets manager in AWS.
    Overview:
    ----
    Secrets Manager data can be accessed using the Boto3 library
    Returns:
    ----
    {dict} -- Returns a dictionary that holds the key and value pairs saved for that secret.
    """
    secret_key = config.get('ec2', 'SM_SECRET_KEY')
    client = boto3.client('secretsmanager', region_name = config.get('ec2', 'SM_REGION'))
    get_secret_value_response = client.get_secret_value(SecretId=secret_key)
    secret = get_secret_value_response['SecretString']
    secret = json.loads(secret)
    return secret

def getDbConnection():
    """Used to connect to the DB to retrieve the most recent data that lives in the db.
    Overview:
    ----
    Use pyscopg2 to create a connection to the database.
    Returns:
    ----
    {psycopg2 connection object} -- Returns the connection object used to query the DB.
    """

    conn = None

    try:

        conn = psycopg2.connect(
            host=config.get('ec2', 'DB_HOST'),
            port=config.get('ec2', 'DB_PORT'),
            user=getDbCreds()['username'],
            password=getDbCreds()['password']
        )

        conn.autocommit = True

        print("----------------------------------------------------")
        print("Connected to DB")
        print("----------------------------------------------------")
    except Exception as e:
        print("----------------------------------------------------")
        print("----------------------------------------------------")
        print("----------------------------------------------------")
        print(f"Connection failed!")
        print("----------------------------------------------------")

    return conn

def getLatestTime():
    """Used to get the most recent data that lives in the db.
    Overview:
    ----
    creates new connection to db. Then retrieves all data for a particular stock_id
    that has a date between today-4 and today. This is a buffer so that if the script fails 
    it can still catch up on its self. The data is converted to a pandas DataFrame. This DF
    does not have the column names, so we then add the column names from the cursor.description.
    from here we grab the max date, the max time after isolating a single day (max date), and
    then it grabs the stock id. 
    Returns:
    ----
    {datetime.date} -- The max date that exists for that stock id in the db.
    {datetime.time} -- The max time that exists for the max date for that stock id in the db.
    {str} -- The stock_id for that stock id in the db. This is a str but gets converted to a uuid when inserting
    """
    conn = getDbConnection()

    if not conn:
        exit(0)

    db_query = """
        select * 
        from avg_inv.stock_data 
        where 1=1
        and date between current_date - 14 and current_date"""

    cursor = conn.cursor()
    cursor.execute(db_query)

    column_names = [desc[0] for desc in cursor.description]

    df = pd.DataFrame(cursor.fetchall())
    df.columns = column_names

    conn.close()

    max_date = max(df['date'])

    df = df[df.date == max_date]

    max_time = max(df['time'])

    stock_id = df.iloc[0]['stock_id']

    return (max_date, max_time, stock_id)

# This was first iteration, using yfinance instead of alphavantage data
# def getLatestData(max_date, max_time, stock_id):

#     df = yf.download(
#         tickers = "AMZN",
#         period = "3d",
#         interval = "5m"
#     )

#     df['Datetime'] = df.index
#     df = df.reset_index(drop=True)

#     df['date'] = [d.date() for d in df['Datetime']]
#     df['time'] = [d.time() for d in df['Datetime']]

#     df = df.drop(['Datetime','Adj Close'], axis=1)

#     # Normalize columns
#     df = df.rename(columns={"Open": "open_price", "High": "high_price", "Low": "low_price", "Close": "close_price", "Volume": "volume"})
#     df = df.round({'open_price': 2, 'high_price': 2, 'low_price': 2, 'close_price': 2})

#     df = df[(df.date >= max_date)]
#     df = df[~((df.date == max_date) & (df.time <= max_time))]

#     df['stock_id'] = stock_id

#     print(df)


def getLatestData(max_date, max_time, stock_id):
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
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AMZN&interval=5min&outputsize=full&apikey={config.get('ec2', 'ALPHAVANTAGE_API_KEY')}"
    r = requests.get(url)
    data = r.json()

    df = pd.DataFrame.from_dict(data['Time Series (5min)'], orient='index')

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

    df = df[(df.date >= max_date)]
    df = df[~((df.date == max_date) & (df.time <= max_time))]

    df['stock_id'] = stock_id

    df = df[((df.time >= datetime.strptime('08:05:00', '%H:%M:%S').time()) & (df.time <= datetime.strptime('17:00:00', '%H:%M:%S').time()))]

    return df

#TODO: Add error processing
def insertNewRows(df):
    """Used to insert the new data into our db
    Overview:
    ----
    use sqlalchemy.engine URL to create a URL object with our db connection info. Have to specify the drivername associated with the library
    and database driver. From this URL we create an sqlalchemy "engine" and connect to the db. Using the Pandas to_sql function, we can provide
    the table name, schema, and connection to insert the data. (NOTE: This is a new method for me, and while i am not very sold on this method,
    because of the simplicity i wanted to give it a try.) If your table exists already, and you are adding to the table, you must specify "append"
    to the if_exists parameter. Also since i do not have an index in this dataframe, i must specify that i do not want to use the index in the insert.
    The to_sql function apparently returns the number of affected rows but i seem to only return None which according to the documentation is possible,
    and not really an issue. I would like to add error processing on this step in the future though
    Arguments:
    ----
    df {pandas.DataFrame} -- The dataframe to insert into the db
    Returns:
    ----
    {None:int} -- This is the return from the to_sql method and can be a number of affected rows or None. Have to do more research
    """
    url = URL.create(
        drivername="postgresql+psycopg2",
        host=config.get('ec2', 'DB_HOST'),
        port=config.get('ec2', 'DB_PORT'),
        username=getDbCreds()['username'],
        password=getDbCreds()['password']       
    )
    db = create_engine(url)

    count = None

    try:

        with db.connect() as conn:

            conn.autocommit = True

            count = df.to_sql(
                name = "stock_data",
                con = conn, 
                schema = "avg_inv",
                if_exists='append',
                index = False
            )
            print("----------------------------------------------------")
            print("Insert completed with no errors")
            conn.close()
            
    except Exception as e:
        print("----------------------------------------------------")
        print("----------------------------------------------------")
        print("----------------------------------------------------")
        print(f"Insert failed")
        print("----------------------------------------------------")

    if not count:
        count = 0

    return count

if __name__ == "__main__":

    # Get config object to access config variables
    global config
    config = getConfigVars()

    # Set print of dataframe to no longer truncate
    pd.set_option("display.max_colwidth", None)

    # Get most recent date, time, and the stock_id that exists in the db
    max_date, max_time, stock_id = getLatestTime()

    # Grab the newest data from alpha vantage
    df = getLatestData(max_date, max_time, stock_id)

    # Formatting Logging
    print(f"Data from {max_date} at {max_time} currently exist!")
    print("----------------------------------------------------")
    print("Data to be inserted!")
    print("----------------------------------------------------")
    print(df)
    print("----------------------------------------------------")
    print("Inserting above data!")

    # Insert new data to the table
    count = insertNewRows(df)
    print("----------------------------------------------------")

    # Check latest data
    max_date, max_time, stock_id = getLatestTime()
    print(f"Data from {max_date} at {max_time} now exist!")

    print(f"Rows affected: {count}")

