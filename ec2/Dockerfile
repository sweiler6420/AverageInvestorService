FROM python:3.7-slim-buster

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN apt-get update \
    && apt-get install -y libpq-dev gcc \ 
    && pip3 install --no-cache-dir -r /code/requirements.txt

COPY config.ini /code/config.ini
COPY update_stock_db.py /code/update_stock_db.py

ENTRYPOINT [ "python", "/code/update_stock_db.py" ]