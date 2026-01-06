from bs4 import BeautifulSoup
from selenium import webdriver
import requests

driver = webdriver.Chrome()
news_organ = {
    "yna" : "https://www.yna.co.kr/",
    "ytn" : "https://www.ytn.co.kr"
}

news_organ_content_tag = {
    "yna" : "li[data-cid ^= 'AKR']",
    "ytn" : ".title a[href ^= 'https://www.ytn.co.kr/_ln/']"
}

news_organ_part = {
    "yna" : {
        "economy" : "economy/all",
        "society" : "society/all"
    },

    "ytn" : {
        "economy" : "news/list.php?mcd=0102",
        "society" : "news/list.php?mcd=0103"
    }
}

removing_organ_tag = {
    "yna" : [
        "em",
        "figcaption",
        "p.txt-copyright.adrs",
        "aside",
        "div.related-zone"
    ],

    "ytn" : [
    ]
}

removing_organ_text = {
    "yna" : [
    ],

    "ytn" : [
        "※ '당신의 제보가 뉴스가 됩니다'",
        "[카카오톡]",
        "[전화]",
        "[메일]"
    ]
}

def get_newspage(driver: webdriver, news_organ: str, page_id: str, content_tag: str) -> str:
    url = f"{news_organ}/{page_id}"

    driver.get(url)
    page = driver.page_source
    soup = BeautifulSoup(page, "lxml")
    contents = soup.select(content_tag)
    links = [a["href"] for a in contents][:1]

    for link in links:
        print(fetch_link(link))


def fetch_link(link: str) -> str | None:
    try:
        html = fetch_html(link)
        soup = parse_html(html)
        soup = exctract_contents(soup)
        soup = decompose_contents_tag(soup, removing_organ_tag.get("ytn"))
        return decompose_contents_text(soup, removing_organ_text.get("ytn"))
    except requests.exceptions.RequestException as e:
        print(f"[Error] {link}에서 {e} 발생")
        return None


def fetch_html(url: str) -> str:
    header = {
        "User-Agent" : "Mozilla/5.0"
    }

    result = requests.get(url, headers=header, timeout=5)
    result.raise_for_status()

    return result.text

def parse_html(html: str) -> str:
    return BeautifulSoup(html, "lxml")

def exctract_contents(soup: BeautifulSoup) -> str:
    content = soup.select_one("#CmAdContent.paragraph")
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


get_newspage(driver, news_organ.get("ytn"), news_organ_part.get("ytn").get("economy"), news_organ_content_tag.get("ytn"))