import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import telepot

# GitHub Secrets에서 정보를 가져옵니다
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
TARGET_URL = "http://www.kfoodtimes.com/news/articleList.html?sc_section_code=S1N26&view_type=sm"
FILE_NAME = "kfood_news_list.xlsx"

def crawl_kfood_news():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = requests.get(TARGET_URL, headers=headers)
    response.encoding = 'utf-8'
    if response.status_code != 200: return []
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.select("ul.type2 li")
    news_data = []
    for article in articles:
        try:
            title_tag = article.select_one("h4.titles a")
            if not title_tag: continue
            title = title_tag.get_text(strip=True)
            link = "http://www.kfoodtimes.com" + title_tag['href']
            info_tags = article.select(".byline em")
            date = info_tags[-1].get_text(strip=True) if info_tags else datetime.now().strftime("%Y-%m-%d")
            news_data.append({"수집일자": datetime.now().strftime("%Y-%m-%d"), "기사날짜": date, "제목": title, "링크": link})
        except: continue
    return news_data

def save_to_excel(data):
    new_df = pd.DataFrame(data)
    if os.path.exists(FILE_NAME):
        old_df = pd.read_excel(FILE_NAME)
        combined_df = pd.concat([old_df, new_df], ignore_index=True).drop_duplicates(subset=['제목'], keep='first')
        combined_df.to_excel(FILE_NAME, index=False)
    else:
        new_df.to_excel(FILE_NAME, index=False)

def send_telegram_file(file_path, token, chat_id):
    bot = telepot.Bot(token)
    with open(file_path, 'rb') as f:
        bot.sendDocument(chat_id, f, caption=f"📅 {datetime.now().strftime('%Y-%m-%d')} 외식신문 뉴스 업데이트입니다.")

# 실행
news_list = crawl_kfood_news()
if news_list:
    save_to_excel(news_list)
    send_telegram_file(FILE_NAME, TELEGRAM_TOKEN, CHAT_ID)
