# 필요한 라이브러리와 모듈을 임포트합니다.
import logging
import os
import csv
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from .config.websites_config import websites

# 로깅 설정을 정의합니다. 로그 메시지는 'log.csv' 파일에 기록됩니다.
logging.basicConfig(filename='log.csv', level=logging.INFO, format='%(asctime)s,%(message)s')

def read_log():
    logged_links = []
    expected_format = 4  # 예상하는 형식의 컬럼 수입니다.
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'log.csv'), mode='r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                if row:
                    if len(row) >= expected_format:
                        link = row[3]  # 4번째 항목(인덱스 3)이 링크입니다.
                        logged_links.append(link)
                    else:
                        # 현재 행의 형식이 예상과 다를 경우, 콘솔에 로깅합니다.
                        print(f"Unexpected format in log file. Expected {expected_format} columns, but got {len(row)}: {row}")
    except FileNotFoundError:
        # 파일이 없는 경우 예외 처리
        pass
    return logged_links

def fetch_posts(website):
    posts = []
    if website['selenium'] == "true":
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(website['url'])

        search_box = driver.find_element(By.ID, website['selenium_inputBoxId'])
        search_box.send_keys(website['selenium_keyword'] + Keys.RETURN)

        # 페이지가 완전히 로드될 때까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, website['selector']))
        )

        html_source = driver.page_source
        driver.quit()
    else:
        response = requests.get(website['url'])
        html_source = response.content

    soup = BeautifulSoup(html_source, 'html.parser')
    for row in soup.select(website['selector']):
        title_element = row.select_one('.sbj.txtL a')
        date_element = row.select_one('.date')
        if title_element and date_element:
            title = title_element.text.strip()
            link = website['base_url'] + title_element.get('href')
            date = date_element.text.strip()
            source = website['name']
            posts.append({'title': title, 'link': link, 'date': date, 'source': source})
    return posts

def log_and_print_posts(posts):
    new_posts = [post for post in posts if post['link'] not in read_log()]
    if not new_posts:
        return False
    for post in new_posts:
        message = f"일자: {post['date']}, 제목: {post['title']}, 출처: {post['source']}, 링크: {post['link']}"
        print(message.replace(',', '\n'))
        with open(os.path.join(os.path.dirname(__file__), '..', 'log.csv'), 'a', newline='') as log_file:
            csv_writer = csv.writer(log_file)
            csv_writer.writerow([post['date'], post['title'], post['source'], post['link']])
    return True

def main():
    logged_links = read_log()
    new_posts_found = False
    for website in websites:
        if website['crawling'] == "true":
            posts = fetch_posts(website)
            if posts and log_and_print_posts(posts):
                new_posts_found = True
    if not new_posts_found:
        print("새로운 게시글이 없습니다.")

if __name__ == "__main__":
    main()
