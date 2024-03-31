import requests
from bs4 import BeautifulSoup

def fetch_posts(website):
    response = requests.get(website['url'])
    html_source = response.content
    soup = BeautifulSoup(html_source, 'html.parser')
    posts = []

    for row in soup.select(website['selector']):
        title_element = row.select_one(website['title_selector'])
        date_element = row.select_one(website['date_selector'])
        if title_element and date_element:
            title = title_element.text.strip()
            link = website['base_url'] + title_element.get('href', '')
            date = date_element.text.strip()
            source = website['name']
            posts.append({'title': title, 'link': link, 'date': date, 'source': source})

    return posts
