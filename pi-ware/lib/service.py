import requests
from lib import get_var


class Service:
    @staticmethod
    def post_message(data: dict):
        url = f'{get_var("SERVICE_URL")}api/message'
        requests.post(url, json=data)
