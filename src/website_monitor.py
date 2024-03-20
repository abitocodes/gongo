import requests
from bs4 import BeautifulSoup

def check_for_updates(url, selector):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        element = soup.select_one(selector)
        if element:
            return element.text.strip()
    return None
