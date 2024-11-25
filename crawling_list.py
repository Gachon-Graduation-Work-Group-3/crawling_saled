import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
url = 'https://m.bobaedream.co.kr/myinfo/seller/no/775518/t/cyber/gubun/A/tab/3'
car_data = []
for i in range(19):
    url_path = url + '/page/' + str(i) + '?'  
    data = requests.get(url_path, headers=headers)
    data.encoding = 'utf-8'
    soup = BeautifulSoup(data.text, 'html.parser')

    product_list = soup.find_all('li', class_='product-list')
    for product in product_list:
        name_tag = product.find('p', class_ = 'ptit')
        name = name_tag.text.strip() if name_tag else '정보 없음'

        price_tag = product.find('dd', class_ = 'price').find('i')
        price = price_tag.text.strip() + '만원' if name_tag else '정보 없음'

        link_tag = product.find('a', class_ = 'list-inner')
        relative_link = link_tag['href'] if link_tag else None
        full_link = f"https://m.bobaedream.co.kr{relative_link}" if relative_link else '링크 없음'

        car_data.append({
            '차량 이름': name,
            '가격': price,
            '링크': full_link
        })
    df = pd.DataFrame(car_data)

    df.to_csv('cars_list.csv', index=False, encoding='utf-8-sig')

 
 