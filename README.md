# The Average Investor -- Full Docs
    - This website was built by Stephen Weiler in it's entirety. If you have any questions please let me know!

## TABLE OF CONTENTS

- [The Average Investor -- Full Docs](#the-average-investor----full-docs)
  - [TABLE OF CONTENTS](#table-of-contents)
  - [Why?](#why)
  - [Structure](#structure)
    - [Database](#database)
    - [DB Update Microservice](#db-update-microservice)
    - [FastAPI](#fastapi)
  - [Services Used -- Setup](#services-used----setup)
      - [AWS RDS](#aws-rds)
      - [AWS ECR](#aws-ecr)
      - [AWS EC2](#aws-ec2)
      - [AWS LAMBDA](#aws-lambda)
      - [AWS EVENTBRIDGE](#aws-eventbridge)

## Why?

I have been trading for many years, starting with penny stocks, then options contracts, and now long term dividends. I have made multiple "trading bots" with python and have made a few python portfolio scripts. While that is awesome and fun, it doesnt actually help most investors like me, and I still have trouble doing research effeciently. I wanted to create a website that relays stock information in the most compact and easy to read way possible. If you actively trade (outside of robinhood and webull), then i'm sure you have seen the websites that just hurl numbers all over the screen. It's not only uncomfortable to look at, but also extremely difficult to digest. Being a software engineer for quite some time, and have been in a full stack position for over 2 years, i decided it was time to use my skills to achieve this goal. 

I would like to note, that in order to make this website as effeciently as possible, i did have to make sacrifices to the overall scope. The 2 biggest eyesores that some of you may see is that the data is limited to trading hours, and on past days, only 8am to 5pm. This was the first struggle. Finding a data source that is reliable and "cheap" was very difficult. This may be something I update in the future if this website takes off at all, but time will only tell. The second compromise was on the infrustructure side. AWS is awesome, it enabled developers like myself to create awesome projects. But the only way AWS can do this, is by charging. The original scope of this website was to attempt to use only the free tier features in AWS but many of the services i leveraged have an expiration after 12 months. During the free period, i will be calculating the price to keep it up and running and hope to be able to keep it running for under $50 a month. 

## Structure

This website's front and back end was designed by myself and I attempted to keep it as modern as possible. To do this, I have been using AWS services as much as i can. 

### Database
    - This website has a postgres database hosted on AWS RDS.
    - Because of the data limitation on AWS free tier, the database only holds the "FAANG" stocks data. This data is 5 minute intraday data from 2020. 
    - There is a folder called [db_migrations](db_migrations) that show the database iterations and script i have used to create the database. 
    - Everyday, a microservice updates the db with the last trading day's data. How this works is explained next.

### DB Update Microservice
   1. This microservice adds the last tradings days data into the DB for the "FAANG" stocks.
   2. Starting from the bottom level. An AWS Eventbridge trigger is set to run everyday at 1 am to trigger an AWS Lambda.
   3. The AWS [Lambda Function](lambda\lambda_to_ec2.py) starts up an EC2 instance, runs a shell script, then stops the ec2 instance. 
   4. The EC2 instance is an Amazon Linux 2 instance. To setup this instance i created a shell script called [setup.sh](ec2\setup.sh). This instance also holds the [run.sh](ec2\run.sh) script that starts docker, pulls a docker image from ECR, runs that docker image, then deletes the docker image. 
   5. In ECR, I am hosting a Docker repo of our [database update script](ec2\update_stock_db.py) in a python 3.7 base layer. The [Dockerfile](ec2\update_stock_db.py) can be seen here. This image is used to update our RDS DB with the latest data. This script grabs the latest data in the db, saves the current available date, and time, and stock_id for that stock. Then pulls the newest info that comes after that date and time and then inserts it into the db.
        - Just a note here. There is a [requirements.txt](ec2\requirements.txt) for the docker image as well as a config.ini file. I decided not to include a template for the config.ini just to save me some time. 

### FastAPI
   1. WIP! This is the next step in the creation of this website! Wish me luck!


## Services Used -- Setup

#### AWS RDS
#### AWS ECR
#### AWS EC2
#### AWS LAMBDA
#### AWS EVENTBRIDGE