import requests
from bs4 import BeautifulSoup
import logging
from .config.websites_config import websites
import os
import csv

logging.basicConfig(filename='log.csv', level=logging.INFO, format='%(asctime)s,%(message)s')

def read_log():
    logged_links = []
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'log.csv'), mode='r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                if row:
                    link = row[3]
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

def log_and_print_posts(posts):
    new_posts = [post for post in posts if post['link'] not in read_log()]
    if not new_posts:
        return False
    for post in new_posts:
        message = f"일자: {post['date']}, 제목: {post['title']}, 출처: {post['source']}, 링크: {post['link']}"
        print(message.replace(',', '\n'))  # 메시지를 콘솔에 출력합니다.
        # CSV 형식에 맞게 로깅
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
