# README

Simple setup and further fastapi documentation follow instruction at
https://www.youtube.com/watch?v=VSQZl43jFzk

## SETTING UP VIRTUAL ENV IN TERMINAL

1. Open root repo folder

2. Create new virtual environment using below command

```
py -m venv venv
```

## CLONING REPO AND SETUP

1. Create a new virtual environment with Python 3.7.9. Follow above instructions

2. Activate your virtual environment using below command on windows cmd

```
.\venv\Scripts\activate
```

2.1. If you run into

```
cannot be loaded because running
scripts is disabled on this system. For more information, see about_Execution_Policies at
https:/go.microsoft.com/fwlink/?LinkID=135170.
```

Then open PowerShell as Admin and run
`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine`
saying `yes` to the prompt.

3. Install necessary libraries using supplied requirement.txt file after activating venv

```
pip install -r requirements.txt
```

## PUSHING CHANGES FOR EASY PULLING

1. Verify all updates are working as necessary

2. Cache required libraries for later pulling

```
pip freeze > requirements.txt
```

3. Push changes into bugfix or feature branch

4. Create PR to dev and get code reviewed and merged

5. Create PR from dev to master to get reviewed and merged!

## SETTING UP RAILWAY DB

1. Follow directions in https://www.youtube.com/watch?v=HEV1PWycOuQ

2. Need to update connection settings with new user and password

## CREATING FAST API BASICS

1. Follow video tutorial https://www.youtube.com/watch?v=Lj7ivxUvSog

## Running FASTAPI Locally

1. Run fast api server locally by running

```
uvicorn cac.api.main:app --reload
```

## INITIALIZING ALEMBIC

1. Run alembic initialization command

```
alembic init alembic
```

2. This will create a subfolder called alembic and an alembic.ini file in the root

3. Update connection variable in alembic.ini file (sqlalchemy.url) You can find the connection URL in railway.app

## CREATE ALEMBIC DB MIGRATION

1. Once Alembic has been initialized run command

```
alembic revision -m "init"
```

2. This will create a version folder in alembic with a new version pythong file

3. Open the newest version python file

4. Implement new upgrade and downgrade functions similar to previous versions

5. Now we can run the migration against the railway postgresql database using command

```
alembic upgrade head
```

6. Final step is to check the db in railway to ensure the migration was successful

6.1 If unsuccessful, you can remove the latest migration from the database by running

```
alembic downgrade -1
```

## RUN GET REQUEST WITH CURL

1. Run command below and update the ?= value to whatever value you want to try to query

```
curl --request GET "localhost:8000?username={username}"
```

## FASTAPI SWAGGER DOCS

1. Once the api is running with uvicorn, go to http://localhost:8000/docs

## GENERATE SECRET KEY

1. Follow directions according to this website to install openssl

2. Run below command

```
openssl rand -hex 32
```

## SETTING UP ENV FILE

1. Create ".env" file in ROOT folder. In this case it would be in the "\cacapi" folder

2. Add all environment variable in this file as shown below

```
DATABASE_HOSTNAME={hostname}
DATABASE_PORT={8000}
DATABASE_USERNAME={username}
DATABASE_PASSWORD={password}
DATABASE_NAME={db name}
SECRET_KEY={fnh5ruji43wobneajitogf589034wgebni5490wbhe945jort23n546kyhfed}
ALGORITHM={algorithm}
ACCESS_TOKEN_EXPIRE_MINUTES={expiration in minutes}
```

3. Please note you must reach out to me to get the real values for above env data.

4. DO NOT REMOVE ".env" FROM GITIGNORE FILE

## Deploying API to Railway.app

1. Follow directions as per https://faun.pub/deploy-a-fastapi-website-to-railway-c08df2a1e878

2. Pull master into local branch

3. Remove bitbucket origin

4. Add new github origin with https://github.com/sweiler6420/CarsAndCoffeeAPI.git url

5. Commit and push local branch to new github origin into dev branch (for development)

6. Remove github origin

7. Add bitbucket origin back

8. THIS WILL MOST LIKELY CHANGE!


## Tech Used

AWS RDS

## To build the Docker Image

1. Open terminal to correct directory

2. Run 

```
docker build -t [name of docker image] .
```