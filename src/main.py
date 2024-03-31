import logging
import os
import csv
from .websites_config import websites
import hashlib
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import os
from datetime import datetime

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")


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
            message = f"{post['primary']}, {post['date']}, {post['title']}, {post['source']}, {post['link']}"
            print(message.replace(',', '\n'))  # 콘솔에 출력
            app_logger.info(message)  # 로그 파일에 기록
    return new_posts

def post_to_slack(new_posts):
    slack_client = WebClient(token=SLACK_TOKEN)
    for post in new_posts:
        # 소스에서 '>' 문자를 기준으로 분할하고, 첫 번째 부분만 사용합니다.
        source_short = post['source'].split('>')[0]
        
        # 메시지 형식을 설정합니다. "바로가기" 텍스트에 링크를 삽입합니다.
        message = f"💘 _이봐, 떴어! 떴다구!_ 💘\n*{post['title']}*\n일자/번호: {post['date']}\n{source_short}\n<{post['link']}|바로가기>"

        try:
            # 슬랙 채널에 메시지를 송출합니다.
            slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
            print(f"Post sent to Slack channel {SLACK_CHANNEL}")
        except SlackApiError as e:
            # 슬랙 API 에러가 발생하면 콘솔에 에러 메시지를 출력합니다.
            print(f"Error posting to Slack: {e}")

def send_no_new_posts_message():
    slack_client = WebClient(token=SLACK_TOKEN)
    message = "✨ *정찰 완료! 새로운 공고는 없었어!* ✨"
    try:
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
        print("Message sent to Slack channel indicating no new posts were found.")
    except SlackApiError as e:
        print(f"Error posting to Slack: {e}")

def main():
    print(f"Started at: {datetime.now()}")
    new_posts_found = False
    for website in websites:
        if website['onCrawling'] == "true":
            print(f"Start Fetching Posts: {website['name']}")
            posts = fetch_posts(website)
            new_posts = log_and_print_posts(posts)
            if new_posts:
                post_to_slack(new_posts)
                new_posts_found = True
            print(f"Done Fetching Posts: {website['name']}")

    if not new_posts_found:
        print("No new posts found.")
        send_no_new_posts_message()
    
    log_file_path = 'log.csv'
    trim_log_file(log_file_path)

def trim_log_file(log_file_path, max_lines=500):
    with open(log_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    if len(lines) > max_lines:
        with open(log_file_path, "w", encoding="utf-8") as file:
            file.writelines(lines[-max_lines:])

# Assuming the log file path is 'log.csv' and it is located in the current directory

if __name__ == "__main__":
    main()

