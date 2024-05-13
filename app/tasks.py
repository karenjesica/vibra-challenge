import urllib.parse
import urllib.request
from flask import current_app as app
from json import dumps

from app.models import CSVData


def send_results_to_redis(results, transaction_id):
    """
    Sending CSV search results to Redis.

    Args:
        results (list): A list of dictionaries containing search results.
        transaction_id (str): The transaction ID.
    """
    try:
        url = f"{app.config.get('REDIS_ENDPOINT')}{urllib.parse.quote_plus(transaction_id)}"
        req = urllib.request.Request(url, data=dumps(results).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='PUT')
        urllib.request.urlopen(req)
    except Exception as e:
        app.logger.error(f"Error sending results to Redis: {e}")

async def process_search_csv(name, city, quantity, transaction_id):
    """
    Asynchronous CSV search processing by filters.

    Args:
        name (str): The name to search for.
        city (str): The city to search for.
        quantity (int): The maximum number of results to return.
        transaction_id (str): The transaction ID.
    """
    log_prefix = "[CSV Search][Async Task]"
    try:
        query = CSVData.query

        if name:
            query = query.filter(CSVData.first_name.ilike(f"%{name}%"))
        if city:
            query = query.filter(CSVData.city.ilike(f"%{city}%"))

        if quantity:
            query = query.limit(quantity)

        results = [row.to_dict() for row in query.all()]
        send_results_to_redis(results, transaction_id)

        app.logger.info(f"{log_prefix} Listing {len(results)} results.")

    except Exception as e:
        app.logger.error(f"Error: {e}")
