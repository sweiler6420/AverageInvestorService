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

from ..utils import utils


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
        username=utils.getDbCreds()['username'],
        password=utils.getDbCreds()['password']       
    )
    db = create_engine(url)

    count = None

    print(df)

    try:

        with db.connect() as conn:

            conn.autocommit = True

            count = df.to_sql(
                name = "politicians",
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


def getPoliticiansDF():

    with open("scraping\politician_trades.json", "r") as file:
        file = json.load(file)

    politicians = {}
    count = 0

    for data in file:
        # This will iterate through each scraped page. Each page has a master key of data and meta. 
        # Data has all the info we want, meta has the page info
        # print(data.keys())
        for row in data['data']:

            # In order to make deduping easy, we will store the politicianId as the master key for each politician child record
            if not row["_politicianId"] in politicians.keys():
                politician_meta_data = {
                    "state": row['politician']["_stateId"],
                    "chamber": row['politician']["chamber"],
                    "dob": row['politician']["dob"],
                    "first_name": row['politician']["firstName"],
                    "last_name": row['politician']["lastName"],
                    "gender": row['politician']["gender"],
                    "party": row['politician']["party"]
                }
                politicians[row["_politicianId"]] = politician_meta_data
                count = count + 1

    print("Number of Politicians found: " + str(count))

    politician_df = pd.DataFrame.from_dict(politicians, orient='index')

    politician_df['politician_id'] = politician_df.index
    politician_df = politician_df.reset_index(drop=True)

    return politician_df


def main():
    df = getPoliticiansDF()

    count = insertNewRows(df)

    print("Insert count: " + str(count))


if __name__ == "__main__":

    # Get config object to access config variables
    global config
    config = utils.getConfigVars()

    # Set print of dataframe to no longer truncate
    pd.set_option("display.max_colwidth", None)

    main()