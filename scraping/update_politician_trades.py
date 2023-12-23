import requests
import random
import time
import json

def get_pages():
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/json',
        'Origin': 'https://www.capitoltrades.com',
        'Referer': 'https://www.capitoltrades.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    session = requests.Session()

    url = "https://bff.capitoltrades.com/trades"

    first_page = session.get(url, headers=headers).json()
    yield first_page

    num_pages = first_page['meta']['paging']['totalPages']
    print("number of pages to grab: " + str(num_pages))
    
    for page in range(2, num_pages + 1):
        print("")

        # Sleeping To Hopefully Prevent BlackListing Or Hitting Throttle Limit
        sleep_delay = random.uniform(1, 20)
        time.sleep(sleep_delay)
        print("Slept for {:.2f} seconds".format(sleep_delay))
        print("Processing Page: " + str(page))

        # Return the next page
        next_page = session.get(url, params={'page': page}, headers=headers).json()
        yield next_page


results = []

# Grab all results
for page in get_pages():
    results.append(page)

# Write all results to file for now. We can ingest later?
results = json.dumps(results, indent=4)

with open("politician_trades.json", "w") as outfile:
    outfile.write(results)



    