from bs4 import BeautifulSoup
from selenium import webdriver
import requests

url = "https://www.yna.co.kr/international/all"

driver = webdriver.Chrome()
driver.get(url)

page = driver.page_source

bs_obj = BeautifulSoup(page, "lxml")

body = bs_obj.select("li[data-cid^='AKR']")

cids = [li['data-cid'] for li in body][:1]

def fetch_html(url: str) -> str:
    header = {
        "User-Agent" : "Mozilla/5.0"
    }

    res = requests.get(url, headers = header, timeout = 5)
    res.raise_for_status()

    return res.text

def parse_html(html:str) -> str:
    return BeautifulSoup(html, "lxml")

def extract_body(soup: BeautifulSoup) -> str:
    body = soup.select_one("div.story-news.article")
    if not body:
        return ""
    
    return body.get_text("\n", strip=True)

def fetch_akr(akr: str) -> str | None:
    url = f"https://www.yna.co.kr/view/{akr}"

    try:
        html = fetch_html(url)
        soup = parse_html(html)
        return extract_body(soup)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {akr} 요청 실패: ", e)
        return None
    
for akr in cids:
    print(fetch_akr(akr))
