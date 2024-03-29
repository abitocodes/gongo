import time
from httpcore import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import os

def fetch_posts(website):
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)
    driver.get(website['url'])

    checkbox = driver.find_element(By.ID, website['selenium_checkboxId'])
    checkbox.click()  # 체크박스 선택
    search_box = driver.find_element(By.ID, website['selenium_inputBoxId'])
    search_box.send_keys(website['selenium_keyword'])
    try:
        # CSS 선택자를 이용하여 검색 버튼을 찾고 클릭
        # search_button.click() 실행
        search_button = driver.find_element(By.CSS_SELECTOR, '#content > form > div > div > button')
        search_button.click()

        # 검색 결과 로딩이 완료되었음을 알 수 있는 체크박스의 체크가 해제될 때까지 기다리기
        WebDriverWait(driver, 120).until(
            lambda d: not d.find_element(By.ID, "check_02").is_selected()
        )
    except TimeoutException:
        print("The page waited 120 seconds but didn't load.")
        driver.quit()  # 드라이버 종료
    else:
        # 로딩 완료 후 페이지 소스 얻기
        html_source = driver.page_source
        driver.quit()
        # 페이지 소스를 이용한 나머지 처리 로직

    soup = BeautifulSoup(html_source, 'html.parser')
    posts = []

    for row in soup.select(website['selector']):
        title_element = row.select_one(website['title_selector'])
        date_element = row.select_one(website['date_selector'])
        if title_element and date_element:
            title = title_element.text.strip()
            number = re.search(r"fncShow\('(\d+)'\)", title_element.get('href', ''))
            # print("number: ", number)
            link = website['base_url'] + "&seq=" + number.group(1)
            # print("link: ", link)
            date = date_element.text.strip()
            source = website['name']
            posts.append({'title': title, 'link': link, 'date': date, 'source': source})

    return posts
