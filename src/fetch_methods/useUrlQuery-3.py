import requests
from bs4 import BeautifulSoup

def fetch_posts(website):
    response = requests.get(website['url'])
    html_source = response.content
    soup = BeautifulSoup(html_source, 'html.parser')
    posts = []

    for row in soup.select('tbody > tr'):
        href_element = row.select_one('td.tl a')
        href = href_element['href'] if href_element else None
        text = href_element.get_text(strip=True) if href_element else None
        date_element = row.select_one('td:last-child')
        date = date_element.get_text(strip=True) if date_element else None

        if href and text and date:
            full_link = website['base_url'] + href
            source = website['name']
            posts.append({'title': text, 'link': full_link, 'date': date, 'source': source})

    return posts
