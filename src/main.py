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
from .websites_config import websites
import hashlib

def generate_sha256_hash(text):
    full_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    return full_hash[:8]  # 해시의 앞 8자리만 반환

# Setup a specific logger for our app
app_logger = logging.getLogger("AppLogger")
app_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('log.csv', mode='a', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s,%(message)s')
file_handler.setFormatter(formatter)
app_logger.addHandler(file_handler)

def read_log():
    logged_primaries = []
    try:
        with open('log.csv', mode='r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                primary = row[2]  # 해시는 로그의 첫 번째 열에 저장되어 있다고 가정
                logged_primaries.append(primary)
    except FileNotFoundError:
        pass
    return logged_primaries

def fetch_posts(website):
    fetch_method = website['fetch_method']
    module_name = f"src.fetch_methods.{fetch_method}"
    fetch_module = __import__(module_name, fromlist=['fetch_posts'])
    return fetch_module.fetch_posts(website)

def log_and_print_posts(posts):
    logged_primaries = read_log()  # 이전에 로그에 기록된 해시들을 읽어옵니다.

    new_posts = []
    for post in posts:
        post_primary = generate_sha256_hash(post['title']+post['date'])
        if post_primary not in logged_primaries:
            post['primary'] = post_primary  # 해시를 포스트 딕셔너리에 추가
            new_posts.append(post)
    if not new_posts:
        return False
    else:
        for post in new_posts:
            message = f"{post['primary']}, {post['date']}, {post['title']}, {post['source']}, {post['link']}"
            print(message.replace(',', '\n'))  # 콘솔에 출력
            app_logger.info(message)  # 로그 파일에 기록
        return True

def main():
    new_posts_found = False
    for website in websites:
        if website['onCrawling'] == "true":
            print("Start Fetching Posts:", website['name'])
            posts = fetch_posts(website)
            if log_and_print_posts(posts):
                new_posts_found = True
        print("Done Fetching Posts:", website['name'])
    if not new_posts_found:
        print("No new posts found.")

if __name__ == "__main__":
    main()
