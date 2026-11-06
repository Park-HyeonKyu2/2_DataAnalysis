from client.request import get_html_as_bs
from pathlib import Path
import pandas as pd
import requests
from client.client import _headers_02
import json
import pprint
from datetime import datetime


if __name__ == "__main__":
  # 저장할 경로 준비하기 (현재 파일의 디렉터리)
  BASE_PATH = Path(__file__) / ".."

  SAVE_PATH = BASE_PATH / "data" / f"melon_chart_100_{datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")}.csv"

  SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)

  DOMAIN = "https://www.melon.com"

  # beautifulsoupt 긁어오기
  html = get_html_as_bs(DOMAIN+"/chart/index.htm")

  # 테이블에서 tr 100개 가져오기 (차트 100개)
  chart_100 = html.select("div.service_list_song.type02.d_song_list > table > tbody > tr")

  print(f"총 데이터: {len(chart_100)}개")

  # 차트 만들어두기
  # columns=["rank", "link", "title", "artist", "album", "like_count"]
  chart_list = []

  print("\n --- 시작 --- \n")
  i=1
  for c in chart_100:
    print()
    print(f"{i}번 데이터 시작")
    # 한 행에서 12개의 td이 존재함
    tr_list = c.select("td")
    # print(len(tr_list))

    # 1. 랭크 뽑기
    # print(int(tr_list[1].select_one("div.wrap.t_center > span.rank").text))
    rank = int(tr_list[1].select_one("div.wrap.t_center > span.rank").text)

    # 2. 링크 뽑기
    # print(DOMAIN + tr_list[4].select_one("div.wrap > a")['href'])
    link = DOMAIN + tr_list[4].select_one("div.wrap > a")['href']

    # 3. 제목 뽑기
    title = tr_list[5].select_one(".ellipsis.rank01 a").text

    # 4. 아티스트 뽑기
    artist = tr_list[5].select_one(".ellipsis.rank02 a").text
    
    # 5. 앨범 명 뽑기
    album = tr_list[6].select_one("a").text

    # 6. 좋아요 수 뽑기
    # 곡 수를 js로 채워서 곡 id를 기반으로 json 데이터 요청하기
    res = requests.request("get", "https://www.melon.com/commonlike/getSongLike.json?contsIds="+link.split("=")[-1], headers=_headers_02)
    # 데이터 형태
    # {
    #   "contsLike":
    #     [{"CONTSID":39504779,"LIKEYN":"N","SUMMCNT":113382}],
    #   "httpDomain":"http://www.melon.com",
    #   "httpsDomain":"https://www.melon.com",
    #   "staticDomain":"https://static.melon.co.kr"
    # }
    like_count = res.json()['contsLike'][0]['SUMMCNT']


    # 저장하기
    # data = {
    #   "rank": rank, 
    #   "link": link, 
    #   "title": title, 
    #   "artist": artist, 
    #   "album": album, 
    #   "like_count": like_count
    # }
    # pprint.pprint(data)
    chart_list.append({
      "rank": rank,
      "link": link,
      "title": title,
      "artist": artist,
      "album": album, 
      "like_count": like_count
    })

    print(f"{i}번 데이터 종료")
    i+=1

  chart_df = pd.DataFrame(chart_list, columns=["rank", "link", "title", "artist", "album", "like_count"]).sort_values('rank')
  print(chart_df)
  with open(SAVE_PATH, "w", newline="") as f:
    chart_df.to_csv(f, encoding="utf-8-sig", index=False)
