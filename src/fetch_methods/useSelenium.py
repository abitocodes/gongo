from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

def fetch_posts(website):
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)
    driver.get(website['url'])
    search_box = driver.find_element(By.ID, website['selenium_inputBoxId'])
    search_box.send_keys(website['selenium_keyword'])
    button = driver.find_element(By.XPATH, website['selenium_searchBtnXpath'])
    button.click()
    html_source = driver.page_source
    driver.quit()

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
