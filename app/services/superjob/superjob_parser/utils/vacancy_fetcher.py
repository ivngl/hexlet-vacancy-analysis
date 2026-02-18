import logging
import os

from dotenv import load_dotenv

from app.services.vacancies.utils.http_client import HTTPClient

load_dotenv()
logger = logging.getLogger(__name__)


async def fetch_superjob_vacancies(params):
    secret_key = os.getenv("SUPERJOB_KEY")
    if not secret_key:
        raise ValueError("SUPERJOB_KEY environment variable is not set")
    base_url = "https://api.superjob.ru/2.0/vacancies"
    headers = {"X-Api-App-Id": secret_key}
    api_client = HTTPClient(base_url, headers)
    urls = [base_url]

    responses = await api_client.get(urls=urls, params=params)
    
    for response in responses:
        if not response.get("objects"):
            logger.warning("No vacancy found in superjob api")
            raise ValueError("No vacancy found in superjob api")
        return response.get("objects")
    
