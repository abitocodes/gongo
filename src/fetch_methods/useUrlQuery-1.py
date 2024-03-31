import requests
from bs4 import BeautifulSoup

def fetch_posts(website):
    response = requests.get(website['url'])
    html_source = response.content
    soup = BeautifulSoup(html_source, 'html.parser')
    posts = []

    # Since the provided HTML structure is different from the initial setup,
    # we adjust the logic to fetch the required data
    for row in soup.find_all("div", class_="toggle"):
        link_element = row.find('a')
        print("link_element: ", link_element)
        title_element = row.find('p', class_="title")
        print("title_element: ", title_element)
        date_element = row.find('span', class_="date")
        print("date_element: ", date_element)
        
        if title_element and date_element and link_element:
            title = title_element.text.strip()
            link = link_element.get('href', '').strip()
            date = date_element.text.strip()
            source = website['name']
            posts.append({'title': title, 'link': link, 'date': date, 'source': source})

    return posts
