import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from selenium.common.exceptions import NoSuchElementException
import utils as ut


headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

urls = ut.extract_urls("./dealers_info/dealers_info_m.csv", "Link")

car_data = []

for url in urls:

    #마지막 페이지 찾기
    page = requests.get(url, headers=headers)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')

    try:
        last_page = soup.find("a", class_ = "last")
    except NoSuchElementException: 
        last_page = None

    if last_page is None:
        last_page_num = 1
    else:
        last_page = last_page["href"]
        match = re.search(r"page/(\d+)", last_page)
        if match:
            last_page_num = int(match.group(1))
            print(last_page_num)
        else:
            print("페이지 번호를 추출할 수 없습니다.")


    for i in range(last_page_num+1):
        url_path = url + '/page/' + str(i) + '?'  
        data = requests.get(url_path, headers=headers)
        data.encoding = 'utf-8'
        soup = BeautifulSoup(data.text, 'html.parser')

        product_list = soup.find_all('li', class_='product-list')
        for product in product_list:
            name_tag = product.find('p', class_ = 'ptit')
            name = name_tag.text.strip() if name_tag else None

            price_tag = product.find('dd', class_ = 'price').find('i')
            price = price_tag.text.strip() + '만원' if name_tag else None

            link_tag = product.find('a', class_ = 'list-inner')
            relative_link = link_tag['href'] if link_tag else None
            full_link = f"https://m.bobaedream.co.kr{relative_link}" if relative_link else None

            car_data.append({
                '링크': full_link,
                '이름': name,
                '가격': price
            })

df = pd.DataFrame(car_data)

df.to_csv('./results/cars_list.csv', index=False, encoding='utf-8-sig')

