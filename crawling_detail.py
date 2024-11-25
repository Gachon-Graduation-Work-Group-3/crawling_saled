import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import crawling_col as cc
import find_class as fc

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
car_data = []

df = pd.read_csv('cars_list.csv')

for index, car in df.iterrows():
    url = car['링크']
    data = requests.get(url, headers=headers)
    data.encoding = 'utf-8'
    soup = BeautifulSoup(data.text, 'html.parser')

    car_summary = soup.find('div', class_ = 'product-summary')
    name = fc.find_class(car_summary, 'h2', 'title')

    car_detail = soup.find('article', class_ = 'article-box article-information')
    year = car_detail.find('span', text = '연식').find_next_sibling("span").text.strip()
    km = car_detail.find('span', text = '주행거리').find_next_sibling("span").text.strip()
    fuel = car_detail.find('span', text = '연료').find_next_sibling("span").text.strip()
    
    #피처 추가해주세요.

    car_data.append({
        '차량 이름': name,
        '가격': car['가격'],
        '연식' : year,
        '주행거리' : km,
        '연료' : fuel
    })

df = pd.DataFrame(car_data)
df.to_csv('cars.csv', index=False, encoding='utf-8-sig')