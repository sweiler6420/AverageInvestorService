import requests
from bs4 import BeautifulSoup
import re
import sys

column_names = []
trades = []

url = 'https://www.capitoltrades.com/trades?per_page=24'
page = requests.get(url)

soup = BeautifulSoup(page.content, "html.parser")

# Check If Trades Exist
if soup.find("no-results"):
    print("No More Pages, Exiting")
    sys.exit(0)

trades_table = soup.find("table", class_="q-table trades-table")

# Get Column Names
trades_table_header = trades_table.find("thead")

trades_table_header_columns = trades_table_header.findAll("span")

for cols in trades_table_header_columns:
    if cols.text.strip() != '':
        column_names.append(cols.text.strip())


# Get Column Values
trades_table_body = trades_table.find("tbody")

trades_table_rows = trades_table_body.findAll("tr")

for row in trades_table_rows:
    temp_row = {}

    # Politician Column
    trades_table_politician_row_data = row.find("td", class_=re.compile("q-td q-column--politician", re.I))
    trades_table_row_politician_name = trades_table_politician_row_data.find("h3", class_=re.compile("q-fieldset politician-name", re.I)).find("a").text.strip()
    trades_table_row_politician_party = trades_table_politician_row_data.find("span", class_=re.compile("q-field party", re.I)).text.strip()
    trades_table_row_politician_chamber = trades_table_politician_row_data.find("span", class_=re.compile("q-field chamber", re.I)).text.strip()
    trades_table_row_politician_state = trades_table_politician_row_data.find("span", class_=re.compile("q-field us-state-compact", re.I)).text.strip()

    temp_row["name"] = trades_table_row_politician_name
    temp_row["party"] = trades_table_row_politician_party
    temp_row["chamber"] = trades_table_row_politician_chamber
    temp_row["state"] = trades_table_row_politician_state

    # Traded Issuer
    trades_table_issuer_row_data = row.find("td", class_=re.compile("q-td q-column--issuer", re.I))
    trades_table_row_trade_issuer = trades_table_issuer_row_data.find("h3", class_=re.compile("q-fieldset issuer-name", re.I)).find("a").text.strip()
    trades_table_row_ticker_symbol = trades_table_issuer_row_data.find("span", class_=re.compile("q-field issuer-ticker", re.I)).text.strip()

    temp_row["issuer"] = trades_table_row_trade_issuer
    temp_row["ticker_symbol"] = trades_table_row_ticker_symbol

    # Published
    trades_table_published_row_data = row.find("td", class_=re.compile("q-td q-column--pubDate", re.I))
    trades_table_row_published_label = trades_table_published_row_data.find("div", class_="q-label").text.strip()
    trades_table_row_published_value = trades_table_published_row_data.find("div", class_="q-value").text.strip()

    temp_row["published_label"] = trades_table_row_published_label
    temp_row["published_value"] = trades_table_row_published_value

    # Traded
    trades_table_traded_row_data = row.find("td", class_=re.compile("q-td q-column--txDate", re.I))
    trades_table_row_traded_label = trades_table_traded_row_data.find("div", class_="q-label").text.strip()
    trades_table_row_traded_value = trades_table_traded_row_data.find("div", class_="q-value").text.strip()

    temp_row["traded_label"] = trades_table_row_traded_label
    temp_row["traded_value"] = trades_table_row_traded_value

    # Filed After
    trades_table_reporting_row_data = row.find("td", class_=re.compile("q-td q-column--reportingGap", re.I))
    trades_table_row_reported_label = trades_table_reporting_row_data.find("div", class_="q-label").text.strip()
    trades_table_row_reported_value = trades_table_reporting_row_data.find("div", class_="q-value").text.strip()

    temp_row["reported_label"] = trades_table_row_reported_label
    temp_row["reported_value"] = trades_table_row_reported_value

    # Owner
    trades_table_owner_row_data = row.find("td", class_=re.compile("q-td q-column--owner", re.I))
    trades_table_row_owner = trades_table_owner_row_data.find("span", class_="q-label").text.strip()

    temp_row["owner"] = trades_table_row_owner

    # Type
    trades_table_type_row_data = row.find("td", class_=re.compile("q-td q-column--txType", re.I))
    trades_table_row_type = trades_table_type_row_data.find("span").text.strip()

    temp_row["type"] = trades_table_row_type

    # Size
    trades_table_size_row_data = row.find("td", class_=re.compile("q-td q-column--value", re.I))
    trades_table_row_size = trades_table_size_row_data.find("span", class_="q-label").text.strip()

    temp_row["size"] = trades_table_row_size

    # Price
    trades_table_price_row_data = row.find("td", class_=re.compile("q-td q-column--price", re.I))
    trades_table_row_price = trades_table_price_row_data.find("span").text.strip()

    temp_row["price"] = trades_table_row_price

    # Transaction
    trades_table_transaction_row_data = row.find("td", class_=re.compile("q-td q-column--_txId", re.I))
    trades_table_row_transaction_url = trades_table_transaction_row_data.find("a").get("href")
    trades_table_row_transaction_id = trades_table_row_transaction_url.split("/")

    temp_row["transaction_url"] = trades_table_row_transaction_url
    temp_row["transaction_id"] = trades_table_row_transaction_id[2]

    trades.append(temp_row)