# src/fetch_methods/4.py
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def fetch_posts(website):
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)
    driver.get(website['url'])
    
    html_source = driver.page_source
    # Wait for the page to load
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, website['selector'])))
    # print(html_source)
    # print(os.getcwd())
    # with open('crawled.html', 'w', encoding='utf-8') as file:
    #     file.write(html_source)
    driver.quit()

    soup = BeautifulSoup(html_source, 'html.parser')
    posts = []

    # 게시글의 제목과 날짜를 가져오는 로직 수정
    for i in range(10):  # '0'부터 '9'까지 반복
        title_id = f'td_NTT_SJ_{i}'
        date_id = f'td_REG_DT_{i}'

        title_element = soup.find(id=title_id)
        date_element = soup.find(id=date_id)

        if title_element and date_element:
            title = title_element.text.strip()
            date = date_element.text.strip()
            link = website['base_url'] + title_element.get('href', '')
            source = website['name']
            posts.append({'title': title, 'link': link, 'date': date, 'source': source})

    return posts