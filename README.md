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
        - [AWS RDS -- Data Setup](#aws-rds----data-setup)
      - [AWS SECRET MANAGER](#aws-secret-manager)
      - [AWS ECR](#aws-ecr)
        - [AWS ECR -- Setup](#aws-ecr----setup)
      - [AWS EC2](#aws-ec2)
        - [AWS EC2 -- Setup](#aws-ec2----setup)
      - [AWS LAMBDA](#aws-lambda)
        - [AWS LAMBDA -- Setup](#aws-lambda----setup)
      - [AWS EVENTBRIDGE](#aws-eventbridge)
        - [AWS EVENTBRIDGE -- Setup](#aws-eventbridge----setup)
      - [AWS IAM ROLES AND POLICIES](#aws-iam-roles-and-policies)
        - [AWS LAMBDA -- Role/Policy Setup](#aws-lambda----rolepolicy-setup)
          - [Role](#role)
        - [AWS EC2 -- Role/Policy Setup](#aws-ec2----rolepolicy-setup)
          - [ECR Policy](#ecr-policy)
          - [ECR Role](#ecr-role)

## Why?

  I have been trading for many years, starting with penny stocks, then options contracts, and now long term dividends. I have made multiple "trading bots" with python and have made a few python portfolio scripts. While that is awesome and fun, it doesnt actually help most investors like me, and I still have trouble doing research effeciently. I wanted to create a website that relays stock information in the most compact and easy to read way possible. If you actively trade (outside of robinhood and webull), then i'm sure you have seen the websites that just hurl numbers all over the screen. It's not only uncomfortable to look at, but also extremely difficult to digest. Being a software engineer for quite some time, and have been in a full stack position for over 2 years, I decided it was time to use my skills to achieve this goal. 

  I would like to note, that in order to make this website as effeciently as possible, I did have to make sacrifices to the overall scope. The 2 biggest eyesores that some of you may see is that the data is limited to trading hours, and on past days, only 8am to 5pm. This was the first struggle. Finding a data source that is reliable and "cheap" was very difficult. This may be something I update in the future if this website takes off at all, but time will only tell. The second compromise was on the infrustructure side. AWS is awesome, it enabled developers like myself to create awesome projects. But the only way AWS can do this, is by charging. The original scope of this website was to attempt to use only the free tier features in AWS but many of the services I leveraged have an expiration after 12 months. During the free period, I will be calculating the price to keep it up and running and hope to be able to keep it running for under $50 a month. 

## Structure

  - This website's front and back end was designed by myself and I attempted to keep it as modern as possible. To do this, I have been using AWS services as much as I can. 

### Database
  - This website has a postgres database hosted on AWS RDS.
  - Because of the data limitation on AWS free tier, the database only holds the "FAANG" stocks data. This data is 5 minute intraday data from 2020. 
  - There is a folder called [db_migrations](db_migrations) that show the database iterations and script I have used to create the database. 
  - Everyday, a microservice updates the db with the last trading day's data. How this works is explained next.

### DB Update Microservice
  1. This microservice adds the last tradings days data into the DB for the "FAANG" stocks.
  2. Starting from the bottom level. An AWS Eventbridge trigger is set to run everyday at 1 am to trigger an AWS Lambda.
  3. The AWS [Lambda Function](lambda/lambda_to_ec2.py) starts up an EC2 instance, runs a shell script, then stops the ec2 instance. 
  4. The EC2 instance is an Amazon Linux 2 instance. To setup this instance I created a shell script called [setup.sh](ec2/setup.sh). This instance also holds the [run.sh](ec2/run.sh) script that starts docker, pulls a docker image from ECR, runs that docker image, then deletes the docker image. 
  5. In ECR, I am hosting a Docker repo of our [database update script](ec2/update_stock_db.py) in a python 3.7 base layer. The [Dockerfile](ec2/Dockerfile) can be seen here. This image is used to update our RDS DB with the latest data. This script grabs the latest data in the db, saves the current available date, and time, and stock_id for that stock. Then pulls the newest info that comes after that date and time and then inserts it into the db.
  - Just a note here. There is a [requirements.txt](ec2/requirements.txt) for the docker image as well as a config.ini file. I decided not to include a template for the config.ini just to save me some time. 

### Back End
  1. WIP! This is the next step in the creation of this website! Wish me luck! The API will be created using python and fastapi. It will be ran serverless through lambda and utilize API Gateway for request configuration and tracking. While API Gateway is TOTALLY not needed for this project, it may be thrown out. I would like to include API Gateway but once again we are limited by AWS free tier usage. Depending on the size of the docker image for the api, i would like to use ECR again in order to make deployments and changes easier. I would also like to automate db migrations from the ECR image, possibly using lambda or ec2 to run the migrations but if i hit limitations i will have to settle for local migrations for the time being.

### Front End
  1. React will be used for front end and will be hosted using AWS Amplify. This is the ideal way of hosting the react front end but depending on the limitations i may have to swap it to EC2. I would prefer to host it using a seperate AWS Service in order to integrate as many services as i can.

## Services Used

  In this section, I will showcase all the tech I used for this website/app along with the generic setup needed to get this working. Most of this setup will be infrustructure based and may not pertain to your project, but I find it important to be as transparent as possible when working on a project of this nature. Also, keep in mind that some of the setup may not be the most "optimized" solution but due to aws pricing I had to work around with what was available. This section also already assumes you have an account with AWS already as I will not be showing you how to setup your account or configure your AWS credentials on your local machine. If this is an issue, there are numerous tutorials online showing how to set this all up!

#### AWS RDS

  In an effort to keep most of the backend data hands off, while using modern technologies, I decided to use AWS RDS. AWS allows up to 20gb of data and the db.t2.micro database instance. While I know this instance size is very small and does not leave room to grow, I had to compromise somewhere, and since I wanted to showcase full AWS integration, this was pretty much my only option. 

  ##### AWS RDS -- Setup

  1. Since the database is needed for the start of the ground up project, I created the database instance first. Navigate to RDS and click create database. I opted for the standard create instead of easy create although there wasnt much customization done. This is largely due to the fact that aws has a "free tier" setup button. Which I did use. While the database engine is not really important, I did opt for postgreSQL as I have the most experience with that engine. 
  2. When creating the database, I chose the Free Tier template which automatically sets up everything in accordance to AWS' free tier. This includes the instance settings which means we only get a single instance and does not support cluster snapshots.
  3. Next is changing your instance id. I just made a generic name for the website name. 
  4. The credentials are relatively simple to setup, but I opted to use the Secrets Manager for the database connection info, and has AWS set the password. This is pretty much an industry standard as it allows AWS to control your passwords. 
  5. The instance configuration is already setup based on the template so that is just based on the free tier template.
  6. From here, I have the storage settings all the same as the template, except I decided to turn off autoscaling storage. The main reason for this was price. If I happen to autoscale larger than 20gb, I would end up having to pay. This just allows me to not worry about it. One thing I did not do, that I should have, is change the storage type to GP3. The free tier auto sets to GP2 but the free tier actually allows for GP3 storage as it is still general purpose.
  7. This next section is important. The connectivity, or vpc setup is essential for allowing your EC2 instance to connect. I actually allowed AWS to auto set all these settings EXCEPT the public access. I decided to make the DB public access. NOTE: IF YOU ALREADY HAVE AN EC2 INSTANCE SETUP, YOU MUST USE THE SAME VPC AND AVAILABILITY ZONE.
  8. For the Database authentication, I clicked password authentication. I decided to not use IAM authorization as it makes the setup a little easier in my opinion. This way I can access secrets manager through boto3, and connect directly to the database without having to make a new user. Now this actually wouldnt have been an issue since I am using the Root User Credentials. This is actually frowned upon by AWS, so I advise against this. Normal practice/real world use cases, I would use IAM authentication as well. 
  9. After setting this all up, click Create Database and you are good to go!
  - After creating the database, you should see a default outbound security group, and a public-access inbound and outbound security group. I am writing this after setting everything up so mine looks different but the extra security groups will be setup with our EC2 instance.

  ##### AWS RDS -- Data Setup

  - The first trick to setting up the database was finding the optimal way to hold the data I want to store. As it is now, it is not complete. I only added a single stocks data going back to 2020. This is due to size limitations for now. I have some of the csvs I used to import data into the table as well as the database migrations scripts I used to setup the schema and tables. The data was manually entered through csvs and all additional info will be inserted automatically through our micro service. Eventually I will add the rest of the "FAANG" stocks data up to 2020, as well as some pertinent company information for each stock.

#### AWS SECRET MANAGER

  - This section is honestly pretty simple. The only secret I am maintaining is the RDS DB access. This was setup during our RDS instance creation, and automated by AWS! How awesome is that! That being said, you do still need to use boto3 to access our secrets, and that implementation can be seen in the [database update script!](ec2/update_stock_db.py)

#### AWS ECR

  Since I knew ahead of time that I would need to continue to add the daily prices and data into the database, I decided to make a python based Docker container to make organization and future deployments easier. Once again, I think it is important to highlight that I don't believe this to be the most optimized structure for setting up a microservice. I have worked on MANY other microservices in my professional career and decided to leverage ECR in order to host the latest Docker Image so that I can pull this image into EC2 and run it on a daily basis. The leading driver in this decision was once again, the service limitations set up by AWS free tier. While I don't necessarily love this setup, it works very well and is about as rigid as I needed!

  ##### AWS ECR -- Setup

  1. Now that we officially have a postgres database running with some data in it. We need a way to automate some ETL microservices. Well really, just one for now. We do this with a python script I talked about above. In order to make deployment painless, I decided to use a Docker image to deploy my code. This Docker Image is stored in ECR. navigate to AWS ECR, and click create repository.
  2. Since I do not necessarily want anyone to be able to change my image for regidity reasons, I decided to make this repo private. I generally opt for open source work but this is a large project and I would like to protect my work here. 
  3. Give this Repo a name, once again I chose something to do with my website name.
  4. Leave tag immutability disabled, as this allows us to pull the "latest" tag and overwrite it on deployments. 
  5. I left the image scan settings off.
  6. Finally I left the Encryption settings off as well.
  7. Create your Repo!
  8. Navigate to your repo and click View push commands at the top right.
  9. Open your local terminal to the root folder where your Dockerfile is. 
  10. Run each command, there should be 4, 1 after another. This should login to aws and docker, build your image, tag your image, and then push your image with the :latest tag to your repo!
  11. If you need to update your Docker image at all in the future, you can now run those 4 commands and create a new image in your repo and the image with the :latest tag will now be the most updated image!

#### AWS EC2

  Now that we have our docker image pushed up to ECR, we need a way to pull that docker image, and run it, all while being full automated and, well, free. I would have PREFERRED to work with ECS but that costs money. I opted for EC2 which can be setup completely free under AWS free tier. I do believe that the free period expires after 12 months, but by then I can budget the monthly price of maintainence, and if not, I can find a different solution. Like mentioned before, the target for this is to use a full AWS implementation.

  ##### AWS EC2 -- Setup

  1. So we have our database, our script we need to run daily, and our Docker image repo setup to be pulled from. Here is where we wrap it all together! Here is where I would have liked to do things differently. But as I mentioned above, this was really my only option. Lets start off by navigating to AWS EC2.
  2. Click launch instance. 
  3. Enter your instance name, it can be anything but once again, I like to keep everything named pretty similar.
  4. Because AWS makes the Amazon linux setups very easy, I decided to try the Amazon Linux 2 AMI that was offered by the free tier. This proved to be a valuable effort because the setup was very easy.
  5. For my instance type, I chose the free tier because thats the goal, do all this as cheap as possible.
  6. I did decide to create a Key Pair, and actually was told by a good buddy to give the ED25519 algorithm a try. The inner workings are the exact same, and they do not change anything on the development side, its just simply a better algorithm for the generation. I also use PuTTY for most of my work so I used the .ppk file format. Feel free to use the traditional .pem file though.
  7. For the network settings, I made sure the VPC is the same as my RDS DB VPC, allowed AWS to create a new security group. The name is auto generated as launch-wizard-1. Lastly, I decided to only allow ssh traffic from 0.0.0.0/0. Technically speaking, this is not the most secure server settings but for what I need it works. In fact, AWS will show you a warning about allowing 0.0.0.0/0 aka. all IP addresses to access your instance. AWS suggested that you use security groups for this setup. I will most likely change this eventually!
  8. For our storage config, AWS allows up to 30gb of EBS general purpose SSD or Mag storage. I did swap to GP3 as it autofilled GP2, and I actually limited my storage to 15 Gibs. This was done so that I can make another instance if needed without worrying about over using my free tier limitations.
  9. I left all the advanced details alone, although should I do this again, I would use the User Data section to run the [setup.sh](ec2\setup.sh) file I used to set the instance up. Also just a note, I don't think you need to use the sudo command in the User Data section. 
  10. Now just launch your instance!
  11. Now that the instance is running, click on the instance, and hit connect in the upper right corner.
  12. This should open a new tab and you can just hit connect again. This will give us SSH access into the instance.
  13. From here I ran each command in the [setup.sh](ec2\setup.sh), 1 by 1. Do note here, you may want to run the amazon-ssm-agent command after setting up the role on this instance that we will be talking about shortly. This ssm-agent was key to getting our Lambda function to execute a command programmatically in our EC2 instance. Also, after running the usermod command, you will most likely have to log back in before you can access docker from the ec2-user without specifying sudo.
  14. After setting this all up, now is the time to nano into a new script in the SSH terminal and copy the commands from [run.sh](ec2\run.sh) into the shell script. Obviously replacing the amazon user id, repo name, and region. You may not need the docker start command at first, but since we will be starting and stopping the instance, I found I needed that command at the beginning of the shell script. 
  - This wraps up the EC2 instance setup, obviously we have some permissions and policies to setup, but that will be talked about below.

#### AWS LAMBDA

  We officially have our ec2 instance setup, able to call ECR, run that docker image, and update the database. The last thing we need to do for our microservice is automate. Lambda is not only completely free for this task, but it's also incredibly simple to setup. With a python Lambda function, I can start our EC2 instance, run a command with ssm, and then stop our ec2 instance in about 5 minutes. The last thing we need, is our scheduled trigger!

  ##### AWS LAMBDA -- Setup

  1. We have everything ready to be automated! YAY. Lets start by navigating to AWS LAMBDA. Click create function.
  2. Enter a function name, relative to the project, as always.
  3. Choose Python 3.7 for your runtime. Obviously your application may differ, I chose python 3.7 because its what i'm comfortable with and 3.7 is the version that I know works. Since I tested it locally.
  4. I left the architecture to x86_64.
  5. Now I allowed AWS to create a new role for me, but this was only temporary as I knew I would change it.
  6. Next hit create function. 
  7. In the Code section, you can now paste in your [lambda function.](lambda\lambda_to_ec2.py)
  8. Because I am using some secret values, I decided to incorporate some environment variables. To add the environment variable in your function, click the configuration tab, then environment variables!
  9. From here, I actually made the Eventbridge trigger, so hop below to the eventbridge setup

#### AWS EVENTBRIDGE

  The last piece of the puzzle for our automated microservice is setting a trigger for our lambda. Eventbridge is surely our best option here since we only need it to be triggered mon-fri sometime in the night. It is easy enough to setup the EventBridge trigger and can actually be done through the Lambda function trigger settings!

  ##### AWS EVENTBRIDGE -- Setup

  1. Since I made my Eventbridge trigger from inside my lambda function, I will lay out how I did it from memory.
  2. At the top, click on add trigger, from the diagram. Select Eventbridge.
  3. Name your trigger. 
  4. from here I chose reoccuring schedule and used the cron expression, ```cron(0 1 ? * MON-FRI *)```. 
  5. Thats it, hit create and your trigger is now setup! Yay! Your automation is done! Not so fast though, if you havent setup all the IAM roles and policies then NONE of this will work. The next session will describe MY policies and roles, you may need to do further research on your use case. 
   
#### AWS IAM ROLES AND POLICIES

  If you have never used IAM in aws, it may seem very overwhelming. It did for me at first. I am still not a genius at IAM but I can certainly get around. The first step to setting this all up is to understand the connections each service needs. Lets start from beginning to end.

  1. AWS EVENTBRIDGE -> AWS LAMBDA: There is nothing needed here actually. This was all taken care of on the lambda setup when we created the trigger from the lambda function console.
  2. AWS LAMBDA -> EC2, SSM: Here, we need to give our lambda function the ability to access our EC2 instance, as well as SSM permissions to send our bash command to that instance.
  3. EC2 -> SSM, ECR, RDS, Secret Manager: Our EC2 instance needs to be able to recieve SSM commands, as well as pull images from ECR, and also needs to be able to query and insert into the RDS Database with our Secret Manager data.

  ##### AWS LAMBDA -- Role/Policy Setup

  - For our microservice lambda function, we know we need to allow the lambda function to access EC2 but it also needs access to SSM. SSM is the AWS Systems Manager Agent, it is used to update, manager, and configure EC2 instances from the AWS api. This will be needed to execute a bash command on our EC2 instance, as if we SSHed into the instance and ran the command ourselves. This should be mentioned a bit during the EC2 Setup section.

  ###### Role
  1. In order to allow our Lambda function to access EC2, we first must make a new Role. Head over to IAM console and click on Role. Click create new Role.
  2. Because this Role will be used to connect 1 AWS Service to another, select AWS Service as the trusted entity type.
  3. Next select Lambda as our Use case.
  4. On the next page, you can add policies to the role. I select ```'AmazonEC2FullAccess', 'AWSLambdaExecute', 'AmazonSSMFullAccess'```.
  5. Finally hit next and give your role a name.
  6. Once your Role is created, you can officially create your Lambda function and attach that new Role to that new function.

  ##### AWS EC2 -- Role/Policy Setup

  - Unlike our Lambda function, we need to create 2 policies as well as an EC2 role. We will start with the Policies.

  ###### ECR Policy
  1. Navigate to IAM console and click create new policy.
  2. Select Elastic Container Registry for the service.
  3. I opted to use the JSON format. This can be seen below. If you use this input make sure to fill in the user specific data.

    ```
    {
      "Version": "2012-10-17",
      "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability",
                "ecr:CompleteLayerUpload",
                "ecr:GetDownloadUrlForLayer",
                "ecr:InitiateLayerUpload",
                "ecr:PutImage",
                "ecr:UploadLayerPart"
            ],
            "Resource": "arn:aws:ecr:<AVAILABILITY_REGION>:<AWS_ACCOUNT_ID>:repository/<ECR_REPO>"
        },
        {
            "Effect": "Allow",
            "Action": "ecr:GetAuthorizationToken",
            "Resource": "*"
        }
      ]
    }
    ```

  4. Now go next and give this policy a useful name and description.

  - Now that your ECR policy is created, duplicate this process but this time select Secrets Manager. If you do not use the Secrets Manager service and you instead put your credentials as environment variables, this should not be needed. Below is the JSON format I used.

    ```
    {
      "Version": "2012-10-17",
      "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "secretsmanager:GetSecretValue",
            "Resource": "*"
        }
      ]
    }
    ```

  - If you have a keen eye, you can see that the resource that is allowed to be accessed is '*', this is because I only have 1 secret, but if you wanted to create a policy specific to a single secret name you can use the ARN in the resource location.

  ###### ECR Role

  - Now that our Policies are created for the Lambda function, we can now replicate the same steps as our Role creation for the Lambda. Make sure to use EC2 as our trust relationship. From here we can now add our 2 custom policies as well as a few extras. If you remember, I mentioned that we need to enable SSM access to our EC2 instance as well. This is our list of Policies without our custom ones. ```'AmazonSSMFullAccess', 'AmazonEC2RoleForSSM', 'AmazonSSMManagedInstaceCore', 'AmazonSSMManagedEC2InstanceDefaultPolicy'```.
  - I did read in some of the documentation that 1 or 2 of those roles will be retired soon but because I did not know when, I decided to add not only the old SSM policies, but the new ones as well. 
  - Attach this Role to your EC2 instance.
  - Keep in mind, even with this Role, we do not have access to the RDS database yet. To do this, I decided to navigate to my EC2 instance. Click on your instance, then select the actions dropdown. From the actions drop down you should be able to click network, and then 'Connect RDS database'. This is will walk you through connecting them and should automatically add all the Security group permissions to your EC2 and RDS instances. You should now have all the EC2 access you need.
  - As I mentioned earlier, I allowed all ip addresses to access the RDS instance should they have the correct login information. I did this for setup and debugging but at this point, you can now remove those inbound and outbound security group rules. Now that your EC2 instance is able to connect to the database, you could in theory get all your db access through your EC2 instance. I decided to leave those security groups for now as I have my credentials setup in Secrets Manager and don't have to worry about security at this point. Plus there is still plenty of development that needs to get done on the API. Once I have the API configured and deployed, I can use Alembic to make migrations, so I will remove those eventually.
