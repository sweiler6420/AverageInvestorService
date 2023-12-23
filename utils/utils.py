from configparser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
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