import csv
import urllib.parse
import urllib.request
from flask import current_app as app
from json import dumps


async def process_search_csv(name, city, quantity, transaction_id):
    log_prefix = "[CSV Search][Async Task]"
    try:
        results = []
        with open("app/files/vibra_challenge.csv", newline="") as csv_file:
            reader = csv.reader(csv_file)

            app.logger.info(f"{log_prefix} Name filter: {name}." if name else f"{log_prefix} No filter applied for name.")
            app.logger.info(f"{log_prefix} City filter: {city}." if city else f"{log_prefix} No filter applied for city.")
            for row in reader:
                name_match = not name or name.lower() in row[1].lower()
                city_match = not city or city.lower() in row[-1].lower()
                if name_match and city_match:
                    results.append(row)

            if quantity:
                results = results[:quantity]

        url = "http://localhost:5000/redis/" + urllib.parse.quote_plus(transaction_id)
        req = urllib.request.Request(url, data=dumps(results).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='PUT')
        urllib.request.urlopen(req)
        app.logger.info(f"{log_prefix} Listing {len(results)} results.")

    except Exception as e:
        app.logger.error(f"Error: {e}")
        return None
