import logging
from logging.handlers import TimedRotatingFileHandler
import schedule
import time
from datetime import datetime, timedelta
import subprocess
import csv
import os

# 로거 설정
logger = logging.getLogger("CrawlerLogger")
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler("crawler_logs.log", when="midnight", interval=1)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# 실행 시간 설정 (한국 시각 기준)
execution_times = ['08:00', '11:00', '14:00', '17:00', '20:00']

def calculate_next_execution(now):
    # 현재 요일을 확인하여 주말인 경우 월요일로 설정
    if now.weekday() >= 5:  # 토요일(5) 또는 일요일(6)인 경우
        days_until_monday = 7 - now.weekday()  # 월요일까지 남은 일수
        next_day = now + timedelta(days=days_until_monday)
        return datetime.strptime(f"{next_day.strftime('%Y-%m-%d')} {execution_times[0]}", "%Y-%m-%d %H:%M")
    else:
        for exec_time in execution_times:
            exec_datetime = datetime.strptime(f"{now.strftime('%Y-%m-%d')} {exec_time}", "%Y-%m-%d %H:%M")
            if exec_datetime > now:
                return exec_datetime
        # 다음날 첫 번째 실행 시간으로 설정
        next_day = now + timedelta(days=1)
        return datetime.strptime(f"{next_day.strftime('%Y-%m-%d')} {execution_times[0]}", "%Y-%m-%d %H:%M")

def run_main_and_log():
    now = datetime.now()
    next_execution = calculate_next_execution(now)

    logger.info(f"지원사업 정보 크롤링을 시작합니다. 예정된 다음 크롤링 실행 시각은 {next_execution.strftime('%Y년 %m월 %d일 %H시 %M분')}입니다.")

    # src/main.py 실행
    subprocess.run(["python", "./src/main.py"], check=True)

    # 실행 후 메시지
    now = datetime.now()
    next_execution = calculate_next_execution(now)
    logger.info(f"지원사업 정보 크롤링이 종료되었습니다. 예정된 다음 크롤링 실행 시각은 {next_execution.strftime('%Y년 %m월 %d일 %H시 %M분')}입니다.")

    # 실행 시간 기록
    with open("executions.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

def schedule_crawling():
    for exec_time in execution_times:
        # 실행 시간별로 작업 예약
        schedule.every().monday.at(exec_time).do(run_main_and_log)
        schedule.every().tuesday.at(exec_time).do(run_main_and_log)
        schedule.every().wednesday.at(exec_time).do(run_main_and_log)
        schedule.every().thursday.at(exec_time).do(run_main_and_log)
        schedule.every().friday.at(exec_time).do(run_main_and_log)

# 스크립트 시작 시 다음 크롤링 실행 시각 계산 및 출력
now = datetime.now()
next_execution = calculate_next_execution(now)
logger.info(f"지원사업 정보 크롤링 타이머가 설정되었습니다. 예정된 다음 크롤링 실행 시각은 {next_execution.strftime('%Y년 %m월 %d일 %H시 %M분')}입니다.")

schedule_crawling()

while True:
    logger.info(f"현재 시각: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}, 대기 중...")
    schedule.run_pending()
    time.sleep(60)  # 매 1분마다 현재 시간 출력 (너무 빈번한 출력을 피하기 위해)
