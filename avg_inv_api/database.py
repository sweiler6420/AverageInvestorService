from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
import boto3
import json

from config import settings

# Get database secrets from AWS Secret Manager
secret_key = settings.sm_secret_key
client = boto3.client('secretsmanager', region_name = settings.sm_region)
get_secret_value_response = client.get_secret_value(SecretId=secret_key)
secret = get_secret_value_response['SecretString']
secret = json.loads(secret)

SQLALCHEMY_DATABASE_URL = f"postgresql://{secret['username']}:{secret['password']}@{settings.database_hostname}:{settings.database_port}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base(metadata=MetaData(schema='avg_inv'))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()