import requests
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging
from .config.websites_config import websites
from dotenv import load_dotenv
import os
import sys

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s:%(message)s')

slack_token = os.getenv('SLACK_TOKEN')
slack_channel = os.getenv('SLACK_CHANNEL')

if not slack_channel:
    print("SLACK_CHANNEL 환경 변수가 설정되어 있지 않습니다. 프로그램을 종료합니다.")
    sys.exit(1)

client = WebClient(token=slack_token)

def read_log():
    logged_links = []
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'log.txt'), 'r') as log_file:
            for line in log_file:
                if 'Link:' in line:
                    link = line.split('Link: ')[-1].strip()
                    logged_links.append(link)
    except FileNotFoundError:
        pass
    return logged_links

def fetch_posts(website):
    response = requests.get(website['url'])
    soup = BeautifulSoup(response.content, 'html.parser')
    posts = []
    for row in soup.select(website['selector']):  # 각 게시글의 행을 순회
        title_element = row.select_one('.sbj.txtL a')
        date_element = row.select_one('.date')  # 날짜 정보를 포함하는 엘리먼트 선택
        if title_element and date_element:
            title = title_element.text.strip()
            link = website['base_url'] + title_element.get('href')
            date = date_element.text.strip()  # 날짜 정보 추출
            source = website['name']
            posts.append({'title': title, 'link': link, 'date': date, 'source': source})
    return posts

def send_slack_message(posts):
    new_posts = [post for post in posts if post['link'] not in read_log()]
    if not new_posts:
        return False
    for post in new_posts:
        # 메시지 형식을 '일자, 제목, 출처, 링크' 순으로 변경
        message = f"일자: {post['date']}\n제목: {post['title']}\n출처: {post['source']}\n링크: {post['link']}"
        try:
            client.chat_postMessage(channel=slack_channel, text=message)
            logging.info(message)  # 로그 메시지 형식도 이에 맞게 변경
        except SlackApiError as e:
            logging.error(f"Error sending message: {e.response['error']}")
    return True

def main():
    logged_links = read_log()
    new_posts_found = False
    for website in websites:
        if website['crawling'] == "true":
            posts = fetch_posts(website)
            new_posts = [post for post in posts if post['link'] not in logged_links]
            if new_posts and send_slack_message(new_posts):
                new_posts_found = True
    if not new_posts_found:
        print("새로운 게시글이 없습니다.")

if __name__ == "__main__":
    main()
