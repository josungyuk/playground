from bs4 import BeautifulSoup
from selenium import webdriver
import requests

driver = webdriver.Chrome()
news_organ_homepage = {
    "yna" : "https://www.yna.co.kr",
    "ytn" : "https://www.ytn.co.kr"
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

news_organ_content_tag = {
    "yna" : ".list01 a[href ^= 'https://www.yna.co.kr/view/']",
    "ytn" : ".title a[href ^= 'https://www.ytn.co.kr/_ln/']"
}

new_organ_extract_title_tag = {
    "yna" : "h1.tit01",
    "ytn" : "h2.news_title"
}

new_organ_extract_content_tag = {
    "yna" : "div.story-news.article",
    "ytn" : "#CmAdContent.paragraph"
}

removing_organ_tag = {
    "yna" : [
        "em",
        "figcaption",
        "p.txt-copyright.adrs",
        "aside",
        "div.related-zone",
        "#newsWriterCarousel01"
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

def get_newspage(driver: webdriver, news_organ: str, homepage_addr: str, page_id: str, content_tag: str) -> str:
    url = f"{homepage_addr}/{page_id}"

    driver.get(url)
    page = driver.page_source
    soup = BeautifulSoup(page, "lxml")
    contents = soup.select(content_tag)
    links = [a["href"] for a in contents][:1]

    for link in links:
        print(fetch_link(link, news_organ))


def fetch_link(link: str, organ: str) -> str | None:
    try:
        html = fetch_html(link)
        soup = parse_html(html)
        title = extract_title(soup, new_organ_extract_title_tag.get(organ))
        soup = extract_contents(soup, new_organ_extract_content_tag.get(organ))
        soup = decompose_contents_tag(soup, removing_organ_tag.get(organ))
        return f"{title} \n {decompose_contents_text(soup, removing_organ_text.get(organ))}"
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


get_newspage(driver, "yna", news_organ_homepage.get("yna"), news_organ_part.get("yna").get("economy"), news_organ_content_tag.get("yna"))