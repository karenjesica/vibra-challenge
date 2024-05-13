import urllib.parse
import urllib.request
from app.models import CSVData
from flask import current_app as app
from json import dumps


async def process_search_csv(name, city, quantity, transaction_id):
    log_prefix = "[CSV Search][Async Task]"
    try:
        query = CSVData.query

        if name:
            query = query.filter(CSVData.first_name.ilike(f"%{name}%"))
        if city:
            query = query.filter(CSVData.city.ilike(f"%{city}%"))

        if quantity:
            query = query.limit(quantity)

        results = query.all()

        results_dict = [row.to_dict() for row in results]

        url = "http://localhost:5000/redis/" + urllib.parse.quote_plus(transaction_id)
        req = urllib.request.Request(url, data=dumps(results_dict).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='PUT')
        urllib.request.urlopen(req)
        
        app.logger.info(f"{log_prefix} Listing {len(results_dict)} results.")

    except Exception as e:
        app.logger.error(f"Error: {e}")
        return None
