from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def send_notification(message):
    # 환경 변수에서 토큰과 채널 정보 가져오기
    token = os.getenv('SLACK_TOKEN')
    channel = os.getenv('SLACK_CHANNEL')

    client = WebClient(token=token)
    try:
        response = client.chat_postMessage(channel=channel, text=message)
        print(response)
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
