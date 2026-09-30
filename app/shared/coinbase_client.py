from coinbase.rest import RESTClient
from app.shared.config import API_KEY, API_SECRET


def get_rest_client():
    """
    Create authenticated Coinbase REST client
    """
    client = RESTClient(api_key=API_KEY, api_secret=API_SECRET)
    return client