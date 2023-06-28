# The Average Investor -- Full Docs
  - This website was built by Stephen Weiler in it's entirety. If you have any questions please let me know!

## TABLE OF CONTENTS

- [The Average Investor -- Full Docs](#the-average-investor----full-docs)
  - [TABLE OF CONTENTS](#table-of-contents)
  - [Why?](#why)
  - [Structure](#structure)
    - [Database](#database)
    - [DB Update Microservice](#db-update-microservice)
    - [Back End](#back-end)
    - [Front End](#front-end)
  - [Services Used](#services-used)
      - [AWS RDS](#aws-rds)
        - [AWS RDS -- Setup](#aws-rds----setup)
      - [AWS ECR](#aws-ecr)
        - [AWS ECR -- Setup](#aws-ecr----setup)
      - [AWS EC2](#aws-ec2)
        - [AWS EC2 -- Setup](#aws-ec2----setup)
      - [AWS LAMBDA](#aws-lambda)
        - [AWS LAMBDA -- Setup](#aws-lambda----setup)
      - [AWS EVENTBRIDGE](#aws-eventbridge)
        - [AWS EVENTBRIDGE -- Setup](#aws-eventbridge----setup)

## Why?

  I have been trading for many years, starting with penny stocks, then options contracts, and now long term dividends. I have made multiple "trading bots" with python and have made a few python portfolio scripts. While that is awesome and fun, it doesnt actually help most investors like me, and I still have trouble doing research effeciently. I wanted to create a website that relays stock information in the most compact and easy to read way possible. If you actively trade (outside of robinhood and webull), then i'm sure you have seen the websites that just hurl numbers all over the screen. It's not only uncomfortable to look at, but also extremely difficult to digest. Being a software engineer for quite some time, and have been in a full stack position for over 2 years, i decided it was time to use my skills to achieve this goal. 

  I would like to note, that in order to make this website as effeciently as possible, i did have to make sacrifices to the overall scope. The 2 biggest eyesores that some of you may see is that the data is limited to trading hours, and on past days, only 8am to 5pm. This was the first struggle. Finding a data source that is reliable and "cheap" was very difficult. This may be something I update in the future if this website takes off at all, but time will only tell. The second compromise was on the infrustructure side. AWS is awesome, it enabled developers like myself to create awesome projects. But the only way AWS can do this, is by charging. The original scope of this website was to attempt to use only the free tier features in AWS but many of the services i leveraged have an expiration after 12 months. During the free period, i will be calculating the price to keep it up and running and hope to be able to keep it running for under $50 a month. 

## Structure

  - This website's front and back end was designed by myself and I attempted to keep it as modern as possible. To do this, I have been using AWS services as much as i can. 

### Database
  - This website has a postgres database hosted on AWS RDS.
  - Because of the data limitation on AWS free tier, the database only holds the "FAANG" stocks data. This data is 5 minute intraday data from 2020. 
  - There is a folder called [db_migrations](db_migrations) that show the database iterations and script i have used to create the database. 
  Everyday, a microservice updates the db with the last trading day's data. How this works is explained next.

### DB Update Microservice
  1. This microservice adds the last tradings days data into the DB for the "FAANG" stocks.
  2. Starting from the bottom level. An AWS Eventbridge trigger is set to run everyday at 1 am to trigger an AWS Lambda.
  3. The AWS [Lambda Function](lambda/lambda_to_ec2.py) starts up an EC2 instance, runs a shell script, then stops the ec2 instance. 
  4. The EC2 instance is an Amazon Linux 2 instance. To setup this instance i created a shell script called [setup.sh](ec2/setup.sh). This instance also holds the [run.sh](ec2/run.sh) script that starts docker, pulls a docker image from ECR, runs that docker image, then deletes the docker image. 
  5. In ECR, I am hosting a Docker repo of our [database update script](ec2/update_stock_db.py) in a python 3.7 base layer. The [Dockerfile](ec2/Dockerfile) can be seen here. This image is used to update our RDS DB with the latest data. This script grabs the latest data in the db, saves the current available date, and time, and stock_id for that stock. Then pulls the newest info that comes after that date and time and then inserts it into the db.
  - Just a note here. There is a [requirements.txt](ec2/requirements.txt) for the docker image as well as a config.ini file. I decided not to include a template for the config.ini just to save me some time. 

### Back End
  1. WIP! This is the next step in the creation of this website! Wish me luck!

### Front End
  1. React will be used for front end!

## Services Used

  In this section, I will showcase all the tech I used for this website/app along with the generic setup needed to get this working. Most of this setup will be infrustructure based and may not pertain to your project, but I find it important to be as transparent as possible when working on a project of this nature.

#### AWS RDS

  In an effort to keep most of the backend data hands off, while using modern technologies, I decided to use AWS RDS. AWS allows up to 20gb of data and the db.t2.micro database instance. While I know this instance size it very small and does not leave room to grow, I had to compromise somewhere, and since I wanted to showcase full AWS integration, this was pretty much my only option.

  ##### AWS RDS -- Setup

#### AWS ECR

  Since I knew ahead of time that i would need to continue to add the daily prices and data into the database, I decided to make a python based Docker container to make organization and future deployments easier. Once again, i think it is important to highlight that I don't believe this to be the most optimized structure for setting up a microservice. I have worked on MANY other microservices in my professional career and decided to leverage ECR in order to host the latest Docker Image so that I can pull this image into EC2 and run it on a daily basis. The leading driver in this decision was once again, the service limitations set up by AWS free tier. While I don't necessarily love this setup, it works very well and is about as rigid as i needed!

  ##### AWS ECR -- Setup

#### AWS EC2

  Now that we have our docker image pushed up to ECR, we need a way to pull that docker image, and run it, all while being full automated and, well, free. I would have PREFERRED to work with ECS but that costs money. I opted for EC2 which can be setup completely free under AWS free tier. I do believe that the free period expires after 12 months, but by then i can budget the monthly price of maintainence, and if not, i can find a different solution. Like mentioned before, the target for this is to use a full AWS implementation.

  ##### AWS EC2 -- Setup

#### AWS LAMBDA

  We officially have our ec2 instance setup, able to call ECR, run that docker image, and update the database. The last thing we need to do for our microservice is automate. Lambda is not only completely free for this task, but it's also incredibly simple to setup. With a python Lambda function, i can start our EC2 instance, run a command with ssm, and then stop our ec2 instance in about 5 minutes. The last thing we need, is our scheduled trigger!

  ##### AWS LAMBDA -- Setup

#### AWS EVENTBRIDGE

  The last piece of the puzzle for our automated microservice is setting a trigger for our lambda. Eventbridge is surely our best option here since we only need it to be trigger mon-fri sometime in the night. It is easy enough to setup the EventBridge trigger and can actually be done through the Lambda function trigger settings!

  ##### AWS EVENTBRIDGE -- Setup