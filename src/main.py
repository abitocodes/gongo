import requests
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging
from .config.websites_config import websites
from dotenv import load_dotenv
import os
import sys
import csv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

logging.basicConfig(filename='log.csv', level=logging.INFO, format='%(asctime)s,%(message)s')

slack_token = os.getenv('SLACK_TOKEN')
slack_channel = os.getenv('SLACK_CHANNEL')

if not slack_channel:
    print("SLACK_CHANNEL 환경 변수가 설정되어 있지 않습니다. 프로그램을 종료합니다.")
    sys.exit(1)

client = WebClient(token=slack_token)

def read_log():
    logged_links = []
    try:
        # log.csv 파일을 열고 csv.reader를 사용하여 읽습니다.
        with open(os.path.join(os.path.dirname(__file__), '..', 'log.csv'), mode='r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                if row:  # 행이 비어있지 않은 경우에만 처리
                    link = row[3]  # 네 번째 열(인덱스는 3)이 링크 정보입니다.
                    logged_links.append(link)
    except FileNotFoundError:
        pass
    return logged_links

def fetch_posts(website):
    response = requests.get(website['url'])
    soup = BeautifulSoup(response.content, 'html.parser')
    posts = []
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

def send_slack_message(posts):
    new_posts = [post for post in posts if post['link'] not in read_log()]
    if not new_posts:
        return False
    for post in new_posts:
        message = f"일자: {post['date']},제목: {post['title']},출처: {post['source']},링크: {post['link']}"
        try:
            client.chat_postMessage(channel=slack_channel, text=message.replace(',', '\n'))
            # CSV 형식에 맞게 로깅
            with open(os.path.join(os.path.dirname(__file__), '..', 'log.csv'), 'a', newline='') as log_file:
                csv_writer = csv.writer(log_file)
                csv_writer.writerow([post['date'], post['title'], post['source'], post['link']])
        except SlackApiError as e:
            logging.error(f"Error sending message: {e.response['error']}")
    return True

def main():
    logged_links = read_log()
    new_posts_found = False
    for website in websites:
        if website['crawling'] == "true":
            posts = fetch_posts(website)
            if posts and send_slack_message(posts):
                new_posts_found = True
    if not new_posts_found:
        print("새로운 게시글이 없습니다.")

if __name__ == "__main__":
    main()
