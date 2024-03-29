from bs4 import BeautifulSoup
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def fetch_posts(website):
    response = requests.get(website['url'], verify=False)
    html_source = response.content
    soup = BeautifulSoup(html_source, 'html.parser')
    posts = []

    for row in soup.select('tr'):
        title_element = row.select_one('td.subject a')
        date_element = row.select_one('td:last-child')

        if title_element and date_element:
            title = title_element.get_text(strip=True)
            href = title_element['href']
            date = date_element.get_text(strip=True)
            link = website['base_url'] + href
            source = website['name']
            posts.append({'title': title, 'link': link, 'date': date, 'source': source})

    return posts
