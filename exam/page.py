import time
import pandas as pd
import os
import re
import shutil
import requests
from page import yes, kyobo, aladin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


def yes(keyword = None, yes_page = 1):
    if not(keyword):
        print("검색어를 입력해주세요")
        return print("프로그램이 종료됩니다.")
    try:
        print(f"yes24 {yes_page}페이지 크롤링")
        options = Options()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 10)
        driver.get("https://www.yes24.com/Main")
        time.sleep(2)
        data = []

        search_box = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#query')
            )
        )

        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.ENTER)

        # yes24 크롤링 시간 측정
        before = time.time()
        for page in range(1, yes_page + 1):
            data = yes_crawling(keyword, driver, data)
            if not(data):
                print("데이터가 없습니다. 크롤링을 종료합니다.")
                break
            print(f"{page}페이지 크롤링 완료")
            if page != yes_page:
                try:
                    if page < 10:
                        next_page = wait.until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, f'#goodsListWrap > div.sGoodsPagen > div > a:nth-child({page + 1})')
                            )#goodsListWrap > div.sGoodsPagen > div > a:nth-child(4)
                        )
                    elif page % 10 != 0:
                        next_page = wait.until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, f'#goodsListWrap > div.sGoodsPagen > div > a:nth-child({page % 10 + 3})')
                            )
                        )
                    else:
                        next_page = wait.until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, f'#goodsListWrap > div.sGoodsPagen > div > a.bgYUI.next')
                            )
                        )
                    next_page.click()
                    time.sleep(2)

                except Exception as e:
                    print("다음 페이지가 없습니다")
                    break
            else:break
    except TimeoutException:
        print("할당 대기시간을 초과하였습니다.")
        driver.quit()
        return None
    after = time.time()
    elapsed_time = after - before
    print(f"yes24 크롤링이 {elapsed_time:.2f}초만큼 걸렸습니다.")
    yes_df = pd.DataFrame(data)
    driver.quit()
    return yes_df
    

def yes_crawling(keyword, driver, data):
    req = driver.page_source
    soup = BeautifulSoup(req, "html.parser")

    books_info = soup.select('ul#yesSchList li')
    for book_info in books_info:
        title_tag = book_info.select_one("div.info_row.info_name a.gd_name")
        author_tag = book_info.select_one("div.info_row.info_pubGrp span.authPub.info_auth a:nth-child(1)")
        price_tag = book_info.select_one("em.yes_b")
        publisher_tag = book_info.select_one("span.authPub.info_pub a")
        publication_date_tag = book_info.select_one("span.authPub.info_date")
        image_tag = book_info.select_one("em.img_bdr img")

        if not(title_tag):
            continue

        title = title_tag.get_text(strip=True)
        author = author_tag.get_text(strip=True) if author_tag else ""
        price = price_tag.get_text(strip=True) if price_tag else ""
        publisher = publisher_tag.get_text(strip=True) if publisher_tag else ""
        publication_date = publication_date_tag.get_text(strip=True) if publication_date_tag else ""
        image_url = ""
        file_path = ""
        if image_tag:
            image_url = (
                image_tag.get("data-original")
                or image_tag.get("src")
                or ""
            )

        os.makedirs("images/yes24", exist_ok=True)
        img_response = requests.get(image_url)
        img_response.content
        safe_title = re.sub(r'[\\/:*?"<>|]', '', title)
        file_name = f"{safe_title}_{len(data) + 1}.jpg"
        save_path = os.path.join("images/yes24", file_name)

        # 이미지 다운 무결성 검사
        with open(save_path, "wb") as file:
            file.write(img_response.content)
        file_path = f"images/yes24/{file_name}"

        data.append({
            "검색어": keyword,
            "책제목": title,
            "저자": author,
            "가격": price + "원",
            "출판사": publisher,
            "출판일": publication_date,
            "이미지": file_path
        })
    return data

def kyobo(keyword=None, kyobo_page=1):
    if keyword is None:
        print("검색어를 입력해주세요")
        return print("프로그램이 종료됩니다.")
    try:
        print(f"교보문구 {kyobo_page}페이지 크롤링")
        options = Options()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 10)
        driver.get("https://product.kyobobook.co.kr/")
        time.sleep(2)
        data = []

        search_box = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#searchKeyword')
            )
        )

        search_box.clear()
        time.sleep(1)
        search_box.send_keys(" ")
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.ENTER)

        # kyobo 크롤링 시간 측정
        before = time.time()
        for page in range(1, kyobo_page + 1):
            data = kyobo_crawling(keyword, driver, data, wait)
            if not(data):
                print("데이터가 없습니다. 크롤링을 종료합니다.")
                break
            print(f"{page}페이지 크롤링 완료")
            if page != kyobo_page:
                try:
                    next_page = wait.until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, f'#pagi > button.btn_page.next')
                        )
                    )
                    next_page.click()
                    time.sleep(1)

                except Exception as e:
                    print("다음 페이지 이동 실패:", e)
                    break
            else:break
    except TimeoutException:
        print("할당 대기시간을 초과하였습니다.")
        driver.quit()
        return None
    after = time.time()
    elapsed_time = after - before
    print(f"교보문구 페이지 크롤링이 {elapsed_time:.2f}초만큼 걸렸습니다.")
    kyobo_df = pd.DataFrame(data)
    driver.quit()
    return kyobo_df
    

def kyobo_crawling(keyword, driver, data, wait):
    # 요소가 나타날 때까지 기다리기
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#shopData_list > ul')
        )
    )
    req = driver.page_source
    soup = BeautifulSoup(req, "html.parser")
    books_info = soup.select('ul.prod_list li')
    

    for book_info in books_info:
        file_path = ""
        title_tag = book_info.select_one("div.auto_overflow_inner a")
        author_tag = book_info.select_one("div.auto_overflow_inner a")
        price_tag = book_info.select_one("span.price span.val")
        publisher_tag = book_info.select_one("div.prod_publish a")
        publication_date_tag = book_info.select_one("span.date")
        image_tag = book_info.select_one("span.img_box img")

        if not(title_tag):
            continue

        title = title_tag.get_text(strip=True)
        author = author_tag.get_text(strip=True) if author_tag else ""
        price = price_tag.get_text(strip=True) if price_tag else ""
        publisher = publisher_tag.get_text(strip=True) if publisher_tag else ""
        publication_date = publication_date_tag.get_text(strip=True) if publication_date_tag else ""
        image_url = image_tag.get("src", "") if image_tag else ""
        os.makedirs("images/kyobo", exist_ok=True)
        if image_url:
            img_response = requests.get(image_url)
            img_response.content
            

            # 제목의 특수문자 제거
            safe_title = re.sub(r'[\\/:*?"<>|]', '', title)
            file_name = f"{safe_title}_{len(data) + 1}.jpg"
            save_path = os.path.join("images/kyobo", file_name)
            
            # 이미지 다운 무결성 검사
            try:
                with open(save_path, "wb") as file:
                    file.write(img_response.content)
            except:
                print(f"{title}의 이미지 다운로드를 실패했습니다.")
                driver.quit()
                return None
            file_path = f"images/kyobo/{file_name}"
        else:
            pass

        data.append({
            "검색어": keyword,
            "책제목": title,
            "저자": author,
            "가격": price + '원',
            "출판사": publisher,
            "출판일": publication_date,
            "이미지": file_path
        })
    return data

def aladin(keyword=None, aladin_page=1):
    if keyword is None:
        print("검색어를 입력해주세요")
        return print("프로그램이 종료됩니다.")
    try:
        print(f"알라딘 {aladin_page}페이지 크롤링")
        options = Options()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 10)
        driver.get("https://www.aladin.co.kr/home/welcome.aspx")
        time.sleep(2)
        data = []

        search_box = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#SearchWord')
            )
        )

        search_box.clear()
        time.sleep(1)
        search_box.send_keys(" ")
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.ENTER)

        

        # aladin 크롤링 시간 측정
        before = time.time()
        for page in range(1, aladin_page + 1):
            data = aladin_crawling(keyword, driver, data, wait)
            if not(data):
                print("데이터가 없습니다. 크롤링을 종료합니다.")
                break
            print(f"{page}페이지 크롤링 완료")
            if page != aladin_page:
                try:
                    # 10페이지를 넘기면 11~20을 누르게
                    if page == 1:
                        next_page = wait.until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, f'#short > div:nth-child({page + 1}) > a')
                                
                            )
                        )
                    elif 9 >= page >= 2:
                        next_page = wait.until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, f'#short > div:nth-child({page + 2}) > a')
                            )
                        )


                    elif page % 10 == 0:
                        next_page = wait.until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, f'#short > div.numbox_next > a')
                            )
                        )
                    
                    else:
                        next_page = wait.until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, f'#short > div:nth-child({page % 10 + 3}) > a')
                            )
                        )
                    next_page.click()
                    time.sleep(2)

                except Exception as e:
                    print("다음 페이지 이동 실패:", e)
                    break
            else:break
    except TimeoutException:
        print("할당 대기시간을 초과하였습니다.")
        driver.quit()
        return None
    after = time.time()
    elapsed_time = after - before
    print(f"알라딘 페이지 크롤링이 {elapsed_time:.2f}초만큼 걸렸습니다.")
    
    aladin_df = pd.DataFrame(data)
    driver.quit()
    return aladin_df
    

def aladin_crawling(keyword, driver, data, wait):
    req = driver.page_source
    soup = BeautifulSoup(req, "html.parser")
    books_info = soup.select('div#Search3_Result div.ss_book_box')
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#Search3_Result')
        )
    )
    
    for book_info in books_info:
        title_tag = book_info.select_one("div.ss_book_list a.bo3")
        author_tag = book_info.select_one("div.ss_book_list li:has(a.bo3) + li a:nth-child(1)")
        price_tag = book_info.select_one("span.ss_p2")
        publisher_tag = book_info.select_one("div.ss_book_list li:has(a.bo3) + li a:nth-child(3)")
        publication_date_tag = book_info.select_one("div.ss_book_list li:has(a.bo3) + li")
        image_tag = book_info.select_one("img.front_cover")
        if not(image_tag):
            image_tag = book_info.select_one("tbody tr td div a img")

        if not(title_tag):
            continue

        title = title_tag.get_text(strip=True)
        author = author_tag.get_text(strip=True) if author_tag else ""
        price = price_tag.get_text(strip=True) if price_tag else ""
        
        publisher = publisher_tag.get_text(strip=True) if publisher_tag else ""
        publication_date = publication_date_tag.get_text(strip=True) if publication_date_tag else ""
        publication_date_match = re.search(r'\d{4}년\s*\d{1,2}월', publication_date)
        if publication_date_match:
            publication_date_match = publication_date_match.group()
        image_url = image_tag.get("src", "") if image_tag else ""
        os.makedirs("images/aladin", exist_ok=True)
        img_response = requests.get(image_url)
        img_response.content
        safe_title = re.sub(r'[\\/:*?"<>|]', '', title)
        file_name = f"{safe_title}_{len(data) + 1}.jpg"
        save_path = os.path.join("images/aladin", file_name)

        # 이미지 다운 무결성 검사
        try:
            with open(save_path, "wb") as file:
                file.write(img_response.content)
        except:
            print(f"{title}의 이미지 다운로드를 실패했습니다.")
            driver.quit()
            return None
        file_path = f"images/aladin/{file_name}"

        data.append({
            "검색어": keyword,
            "책제목": title,
            "저자": author,
            "가격": price,
            "출판사": publisher,
            "출판일": publication_date_match,
            "이미지": file_path
        })
    return data