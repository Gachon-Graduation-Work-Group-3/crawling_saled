import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import utils as ut
import time
from concurrent.futures import ThreadPoolExecutor


df = pd.read_csv('./results/cars_list4.csv')


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
}

# 데이터 컬럼 정의
info = ["링크", "이름", "가격", "신차대비가격", "최초등록일",
        "연식", "주행거리", "연료", "배기량", "색상", "설명글"]
spec = ["엔진형식", "연비", "최고출력", "최대토크"]
appearances = ["선루프", "파노라마선루프"]
interiors = ["열선시트(앞좌석)", "열선시트(뒷좌석)"]
safeties = ["동승석에어백", "후측방경보", "후방센서", "전방센서", "후방카메라", "전방카메라", "어라운드뷰"]
conveniences = ["열선핸들", "오토라이트", "크루즈컨트롤", "자동주차"]
multimedia = ["네비게이션(순정)", "네비게이션(비순정)"]
insurance = ["보험처리수", "소유자변경", "전손", "침수전손", "침수분손", "도난", "내차피해_횟수", "내차피해_금액", "타차가해_횟수", "타차가해_금액"]
check = ["판금", "교환", "부식"]

cols = info + spec + appearances + interiors + safeties + conveniences + multimedia + insurance + check


# 차량 데이터를 병렬로 처리하는 함수
def process_car(car):
    url = car['링크']
    price = car['가격']
    
    # 외제차 제외 (URL에 'I' 포함 시 필터링)
    if re.search(r"/I/", url):
        return None

    # 요청 (최대 3번 재시도)
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException as e:
            time.sleep(5)
    else:
        return None  # 요청 실패 시 무시

    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 디버깅용
    print(url)


    # info
    car_summary = soup.find('div', class_='product-summary')
    name = ut.find_class(car_summary, 'h2', 'title')
    feature_box = soup.find("div", class_="product-feature")
    percent = ut.find_class(feature_box, "span", "text")
    article_header = soup.find("li", class_="date")
    regist = article_header.find("span", class_="text").get_text().split() if ut.isvalid(article_header) else None
    
    # car_detail이 없는 경우가 있음
    car_detail = soup.find('article', class_='article-box article-information')
    if ut.isvalid(car_detail):
        year = car_detail.find('span', string = '연식').find_next_sibling("span").get_text().strip()
        km = car_detail.find('span', string = '주행거리').find_next_sibling("span").get_text().strip()
        fuel = car_detail.find('span', string = '연료').find_next_sibling("span").get_text().strip()
        color = car_detail.find('span', string = '색상').find_next_sibling("span").get_text().strip()
        amount = car_detail.find('span', string='배기량').find_next_sibling("span").get_text().strip() if ut.isvalid(car_detail.find('span', string='배기량')) else None
    else:
        year = None
        km = None
        fuel = None
        color = None
        amount = None
    
    explain = soup.find("div", class_="content").get_text().strip() if ut.isvalid(soup.find("div", class_="content")) else None
    res_info = [url, name, price, percent, regist, year, km, fuel, amount, color, explain]


    # spec
    spec_box = soup.find("ul", class_="detail-swiper-list")
    if ut.isvalid(spec_box):
        engin = spec_box.find('p', string='엔진형식').find_next_sibling("p").get_text().strip() if ut.isvalid(spec_box.find('p', string='엔진형식')) else None
        effic = spec_box.find('p', string='연비').find_next_sibling("p").get_text().strip() if ut.isvalid(spec_box.find('p', string='연비')) else None
        max_pow = spec_box.find('p', string='최고출력 ').find_next_sibling("p").get_text().strip() if ut.isvalid(spec_box.find('p', string='최고출력 ')) else None
        max_tok = spec_box.find('p', string='최대토크').find_next_sibling("p").get_text().strip() if ut.isvalid(spec_box.find('p', string='최대토크')) else None
    else: 
        engin = None
        effic = None
        max_pow = None
        max_tok = None

    res_spec = [engin, effic, max_pow, max_tok]


    #option
    res_options = []

    #제원정보가 있을 때, 없을 때 다름
    if ut.isvalid(soup.find("h3", string="제원정보")):
        options_link = soup.find_all("a", class_ = "btn-details")[1]["href"]
    else:
        options_link = soup.find_all("a", class_ = "btn-details")
        if len(options_link)>0:
            options_link = options_link[0]["href"]
        else:
            options_link = None

    if options_link:        
        # 정규식을 사용해 href 속성에서 URL 추출
        match = re.search(r"javascript:window.open\('([^']+)'\)", options_link)

        if match:
            relative_url = match.group(1)  # 상대 URL
        else:
            print("No URL found")

        options_url = 'https://m.bobaedream.co.kr' + relative_url


        for attempt in range(3):  # 최대 3번 재시도
            try:
                options_response = requests.get(options_url, headers=headers, timeout=10)
                if options_response.status_code == 200:
                    break  # 성공 시 종료
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(5)  # 재시도 전 대기

        options_response.encoding = "utf-8"
        options_soup = BeautifulSoup(options_response.text, "html.parser")

        #appearences
        for appearence in appearances:
            res_options.append(ut.option_check(options_soup, appearence))

        #interiors
        for interior in interiors:
            res_options.append(ut.option_check(options_soup, interior))

        #safeties
        for safety in safeties:
            res_options.append(ut.option_check(options_soup, safety))

        #conveniences
        for convenience in conveniences:
            res_options.append(ut.option_check(options_soup, convenience))

        # multimedia
        for media in multimedia:
            res_options.append(ut.option_check(options_soup, media))
    else:
        res_options = [0] * sum(map(len, [appearances, interiors, safeties, conveniences, multimedia]))



    #판매완료 차량은 보험이력이 안나옴
    res_insur = [None] * len(insurance)
    #수리이력이 팝업 형식으로 되어 있어 bs4로는 추출 불가
    res_check = [None] * len(check)

    return res_info + res_spec + res_options + res_insur + res_check


# 병렬 처리
car_data = []
with ThreadPoolExecutor(max_workers=10) as executor:  # 동시 10개의 스레드
    results = list(executor.map(process_car, [car for _, car in df.iterrows()]))

# 유효한 데이터만 필터링
car_data = [result for result in results if result is not None]

# 결과 저장
df = pd.DataFrame(data=car_data, columns=cols)
df.to_csv('./results/saled_cars4.csv', index=False, encoding='utf-8-sig')
