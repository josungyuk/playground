import crawling_domain as nd

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
import requests
import random

options = Options()
options.add_argument("--incognito")

driver = webdriver.Chrome(options=options)

def get_newspage(driver: webdriver, news_organ: str, homepage_addr: str, page_id: str, content_tag: str) -> str:
    url = f"{homepage_addr}/{page_id}"

    driver.get(url)
    page = driver.page_source
    soup = BeautifulSoup(page, "lxml")
    contents = soup.select(content_tag)
    links = [
        urljoin(url, a["href"])
        for a in contents
    ][:1]

    for link in links:
        print(fetch_link(link, news_organ))


def fetch_link(link: str, organ: str) -> str | None:
    try:
        html = fetch_html(link)
        soup = parse_html(html)
        title = extract_title(soup, nd.new_organ_extract_title_tag.get(organ))
        soup = extract_contents(soup, nd.new_organ_extract_content_tag.get(organ))
        soup = decompose_contents_tag(soup, nd.removing_organ_tag.get(organ))
        return f"{title} \n {decompose_contents_text(soup, nd.removing_organ_text.get(organ))}"
    except requests.exceptions.RequestException as e:
        print(f"[Error] {link}에서 {e} 발생")
        return None


def fetch_html(url: str) -> str:
    headers = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Mozilla/5.0"
        ]

    result = requests.get(url, headers={"User-Agent": random.choice(headers)}, timeout=5)
    result.raise_for_status()

    return result.text

def parse_html(html: str) -> str:
    return BeautifulSoup(html, "lxml")

def extract_title(soup: BeautifulSoup, tag: str) -> str:
    return soup.select_one(tag).get_text("\n", strip=True)

def extract_contents(soup: BeautifulSoup, tag: str) -> str:
    content = soup.select_one(tag)
    if not content:
        return None
    
    return content

def decompose_contents_tag(soup: BeautifulSoup, selector: list) -> str:
    for sel in selector:
        for tag in soup.select(sel):
            tag.decompose()

    return soup

def decompose_contents_text(soup: BeautifulSoup, selector: list) -> str:
    for keyword in selector:
        for text in soup.find_all(string=True):
            if text.strip().startswith(keyword):
                text.extract()

    return soup.get_text("\n", strip=True)

parameters = [
    (driver, nd.NewsSource.YNA, nd.news_organ_homepage[(nd.NewsSource.YNA)], nd.news_organ_type[nd.NewsSource.YNA][nd.NewsType.ECONOMY], nd.news_organ_content_tag[(nd.NewsSource.YNA)]),
    (driver, nd.NewsSource.YTN, nd.news_organ_homepage[(nd.NewsSource.YTN)], nd.news_organ_type[nd.NewsSource.YTN][nd.NewsType.ECONOMY], nd.news_organ_content_tag[(nd.NewsSource.YTN)]),
    (driver, nd.NewsSource.BBC, nd.news_organ_homepage[(nd.NewsSource.BBC)], nd.news_organ_type[nd.NewsSource.BBC][nd.NewsType.ECONOMY], nd.news_organ_content_tag[(nd.NewsSource.BBC)]),
    # (driver, nd.NewsSource.BBC, nd.news_organ_homepage[(nd.NewsSource.BBC)], nd.news_organ_type[nd.NewsSource.BBC][nd.NewsType.ECONOMY], nd.news_organ_content_tag[(nd.NewsSource.BBC)]),
]

for param in parameters:
    get_newspage(*param)