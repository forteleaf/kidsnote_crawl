#-*- coding: utf-8 -*-

# pip install selenium

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import datetime
from urllib.request import urlopen
import urllib.parse
import json

user_id = "user_id"
user_pwd = "user_pwd"
start_cnt = 1
comment_json = []

# config.json에서 ID/PW 파싱
with open('config.json') as config_file:
    data = json.load(config_file)
    user_id = data['user_id']
    user_pwd = data['user_pwd']



options = webdriver.ChromeOptions() # 크롬 옵션 객체 생성
options.add_argument('headless') # headless 모드 설정

driver = webdriver.Chrome("./chromedriver.exe", options=options)


# config.json의 ID/PW를 통한 로그인
def login():
    driver.get("https://www.kidsnote.com/login/")

    elem = driver.find_element_by_id("id_username")
    elem.send_keys(user_id)
    elem = driver.find_element_by_id("id_password")
    elem.send_keys(user_pwd)
    elem.send_keys(Keys.ENTER)

# 호칭 설정
def choose_family_role():
    driver.find_element_by_css_selector('div.header-inner > a#roleSelect').click()
    driver.find_element_by_css_selector('div.select-form-wrapper > div:nth-child(2) >  form').click()

# 추억상자로 이동
def to_yester_album():
    driver.find_element_by_css_selector('.dropdown-sidebar > .dropdown-toggle > .dropdown-title > h5').click()
    driver.find_element_by_css_selector('#feedActivateForm > div.dropdown-body > div.dropdown-title > h6').click()
    driver.find_element_by_css_selector('div.content > div#content-inner > h5 > a > span').click()

# 알림장 선생님 글 읽기
def read_comment():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    comment = soup.select_one('div.report-detail-wrapper > div.report-detail > div.content-text').text.encode().decode()
    # comment = driver.find_element_by_css_selector('div.report-detail-wrapper > div.report-detail > div.content-text').text
    return comment.replace("\\n","").strip()

# 알림장 사진 다운로드
def download_all_pic():
    pic_list = driver.find_elements_by_css_selector('#img-grid-container > div.grid > a.gallery-content')
    today_date = get_report_date()

    for idx, pic_url in enumerate(pic_list):
        pic_url_parse = pic_url.get_attribute('href').replace("img_l", "img").strip()
        download_file_name = today_date + "_"+ str(idx+1).zfill(2) +"."+ pic_url_parse.split(".")[-1]
        urllib.request.urlretrieve(pic_url_parse, "./images/" + download_file_name)
        print(download_file_name + " file saved")

# 알림장 목록에서 알림장 선택
def select_card_and_download(idx):
    card_list = driver.find_elements_by_css_selector('div.report-list-wrapper > a > div.card')
    card_list[idx].click()
    
    comment_json.append({"date":get_report_date(), "comment":read_comment()})
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    information_list = soup.select("#img-grid-container > div.grid > a.gallery-content")
    
    if(len(information_list) > 0):
        download_all_pic()
    
    driver.find_element_by_css_selector('div.button-group-wrapper > div.pull-right > a.btn.btn-default > i.kn.kn-list').click()


# 현 페이지의 알림장 목록 갯수 count
def retrieve_card_cnt():
    card_cnt = driver.find_elements_by_css_selector('div.report-list-wrapper > a > div.card')
    return card_cnt
# 총 페이지 수 count
def retrieve_max_page_cnt():
    max_page_cnt = driver.find_elements_by_css_selector('ul.pagination-sm > li > a')[-2].get_attribute('text')
    return (int(max_page_cnt))
# 알림장 작성 일자 파싱
def get_report_date():
    report_date = driver.find_element_by_css_selector('div.content > div.sub-header > h3.sub-header-title').get_attribute('innerHTML')
    this_time_t = datetime.datetime.strptime(report_date.strip()[:-4], '%Y년 %m월 %d일')
    this_time_f = this_time_t.strftime('%Y%m%d')

    return(this_time_f)



if __name__ =="__main__":
    login()
    choose_family_role()
    to_yester_album()
    
    card_cnt = len(driver.find_elements_by_css_selector('div.report-list-wrapper > a > div.card'))
    # 페이지 별 이동
    for idx in range(start_cnt , retrieve_max_page_cnt()):
        # 다음 페이지로 이동
        driver.find_element_by_link_text(str(idx+1)).click()
        
        for idx in range(card_cnt):
            select_card_and_download(idx)
    # 알림장 선생님 글 저장     
    with open('comments.json', 'w', encoding="utf-8") as outfile:
        json.dump(comment_json, outfile, ensure_ascii=False)

    driver.quit()
