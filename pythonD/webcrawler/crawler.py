from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver

url = "https://www.yna.co.kr/international/all"
driver = webdriver.Chrome()
driver.get(url)

page = driver.page_source

bs_obj = BeautifulSoup(page, "html.parser")


lists = bs_obj.find_all("li", "data-cid")

for idx, id in enumerate(lists):
    print(f"{idx} {id}")