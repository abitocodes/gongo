import requests
from bs4 import BeautifulSoup

def fetch_posts(website):
    response = requests.get(website['url'])
    html_source = response.content
    soup = BeautifulSoup(html_source, 'html.parser')
    posts = []

    for row in soup.select('tbody > tr'):
        title_element = row.select_one('td.tl > div.co > div > a')
        date_element = row.find_all('span', class_="bco")[2]  # Assuming the first span.bco contains the date
        
        if title_element and date_element:
            title = title_element.text.strip()
            link = website['base_url'] + title_element.get('href', '').strip()
            date = date_element.text.strip().split('~')[0].strip()  # To get the start date if there is a range
            source = website['name']
            posts.append({'title': title, 'link': link, 'date': date, 'source': source})

    return posts
