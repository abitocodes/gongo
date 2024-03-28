import logging
import os
import csv
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
# Assume .config.websites_config contains the websites configuration
from .config.websites_config import websites

# Setup a specific logger for our app
app_logger = logging.getLogger("AppLogger")
app_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('log.csv', mode='a', encoding='utf-8')  # 'newline' 인자를 제거했습니다.
formatter = logging.Formatter('%(asctime)s,%(message)s')
file_handler.setFormatter(formatter)
app_logger.addHandler(file_handler)


def read_log():
    logged_links = []
    try:
        with open('log.csv', mode='r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                if len(row) == 4:
                    link = row[3]
                    logged_links.append(link)
    except FileNotFoundError:
        pass
    return logged_links

def fetch_posts(website):
    posts = []
    if website['selenium'] == "true":
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)
        driver.get(website['url'])
        search_box = driver.find_element(By.ID, website['selenium_inputBoxId'])
        search_box.send_keys(website['selenium_keyword'] + Keys.RETURN)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, website['selector'])))
        html_source = driver.page_source
        driver.quit()
    else:
        response = requests.get(website['url'])
        html_source = response.content

    soup = BeautifulSoup(html_source, 'html.parser')
    for row in soup.select(website['selector']):
        title_element = row.select_one(website.get('title_selector', '.sbj.txtL a'))
        date_element = row.select_one(website.get('date_selector', '.date'))
        if title_element and date_element:
            title = title_element.text.strip()
            link = website['base_url'] + title_element.get('href', '')
            date = date_element.text.strip()
            source = website['name']
            posts.append({'title': title, 'link': link, 'date': date, 'source': source})
    return posts

def log_and_print_posts(posts):
    logged_links = read_log()  # 이전에 로그에 기록된 링크들을 읽어옵니다.
    new_posts = [post for post in posts if post['link'] not in logged_links]  # 기록되지 않은 새로운 포스트만 필터링
    if not new_posts:
        return False
    else:
        for post in new_posts:
            message = f"{post['date']}, {post['title']}, {post['source']}, {post['link']}"
            print(message.replace(',', '\n'))  # 콘솔에 출력
            app_logger.info(message)  # 로그 파일에 기록
        return True

def main():
    logged_links = read_log()
    new_posts_found = False
    for website in websites:
        if website['crawling'] == "true":
            posts = fetch_posts(website)
            if log_and_print_posts(posts):
                new_posts_found = True
    if not new_posts_found:
        print("No new posts found.")

if __name__ == "__main__":
    main()
