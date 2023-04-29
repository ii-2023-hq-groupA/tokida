import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time

# 店名
# 最寄駅
# 住所
# レビュー(10件)


class Tabelog:
    """
    食べログスクレイピングクラス
    test_mode=Trueで動作させると、最初のページの3店舗のデータのみを取得できる
    """
    def __init__(self, base_url, begin_page=1, end_page=5):
        
        # 変数宣言
        self.store_id_num = 0
        self.store_name = ""
        self.station = ""
        self.address = ""
        self.review_cnt = 0
        self.review = ""
        self.columns = ["store_name", "station", "address", "review_cnt", "review"]
        self.df = pd.DataFrame(columns=self.columns)

        self.__regexcomp = re.compile(r'\n|\s') # \nは改行、\sは空白
        
        # page_num = begin_page # 店舗一覧ページ番号

        print(self.df)
        self.scrape_list(base_url)
        # print(self.df)
    
    def scrape_list(self, list_url):
        """
        店舗一覧ページのパーシング
        """
        r = requests.get(list_url) # データ取得
        if r.status_code != requests.codes.ok:
            return False
        
        soup = BeautifulSoup(r.content, 'html.parser') # データ抽出,子要素の取得
        soup_a_list = soup.find_all('a', class_='list-rst__rst-name-target') # 店名一覧

        if len(soup_a_list) == 0:
            return False
        
        # print(soup_a_list)
        # soup_a_list[0].contents[0]　＃contents取得済

        for soup_a in soup_a_list:
            item_url = soup_a.get('href') # 店の個別ページURLを取得
            self.store_id_num += 1
            self.store_name = soup_a.contents[0] # 店の名前を取得
            print(self.store_id_num, self.store_name, item_url) # 1 創作麺工房 鳴龍 https://tabelog.com/tokyo/A1323/A132302/13141302/

            self.scrape_item(item_url)

        return True


    def scrape_item(self, item_url):
        """
        個別店舗情報ページのパーシング
        """
            
            
        # self.scrape_item(item_url)

        # 各店のページへ遷移 pick
        pick_r = requests.get(item_url) # データ取得
        if pick_r.status_code != requests.codes.ok:
            return False
            
        pick_soup = BeautifulSoup(pick_r.content, 'html.parser') # データ抽出,子要素の取得
        pick_url = pick_soup.select("#review")[0].get("href") # 口コミへ飛ぶURL
        self.station = pick_soup.find('span', class_="linktree__parent-target-text").contents[0] # 最寄駅
        # <span class="linktree__parent-target-text">新大塚駅</span>
        
        pick_address = pick_soup.find('p', class_="rstinfo-table__address").contents
        _address = ""
        for address in pick_address:
            _address += address.getText()
        self.address = _address
        # <p class="rstinfo-table__address"><span><a href="/tokyo/" class="listlink">東京都</a></span><span><a href="/tokyo/C13116/rstLst/" class="listlink">豊島区</a><a href="/tokyo/C13116/C36718/rstLst/" class="listlink">南大塚</a>2-34-4</span> <span>SKY南大塚 1F</span></p>


        # 口コミページへ遷移 pick_comment
        comment_num = 0
        pick_comment_r = requests.get(pick_url) # データ取得
        if pick_comment_r.status_code != requests.codes.ok:
            return False
            
        pick_comment_soup = BeautifulSoup(pick_comment_r.content, 'html.parser') # データ抽出,子要素の取得
        # print(pick_comment_soup)
        # <a class="rvw-item__title-target" href="/tokyo/A1305/A130501/13005588/dtlrvwlst/B59309417/?use_type=0&amp;smp=1"><strong>焼きさんまの旨味が凝縮したラーメン、と言う他ない</strong></a>
        pick_comment_list = pick_comment_soup.find_all('a', class_="rvw-item__title-target", limit=10) # 口コミの題名
        _review = ""
        for comment in pick_comment_list:
            comment_num += 1
            _review += comment.contents[0].getText().replace("\n","")
            # print(comment.contents[0].getText())
        self.review = _review
        self.review_cnt = comment_num
        # print(self.review)
        print(self.review_cnt)  # 10

        self.make_df()

        return
    
    def make_df(self):
        self.store_id = str(self.store_id_num).zfill(8) #0パディング
        # メモ　self.columns = ["store_name", "station", "address", "review_cnt", "review"]
        se = pd.Series([self.store_name, self.station, self.address, self.review_cnt, self.review], self.columns) # 行を作成
        self.df = self.df.append(se, self.columns) # データフレームに行を追加
        # self.df = pd.concat([self.df, se])
        return
    



tokyo_ramen_review = Tabelog(base_url="https://tabelog.com/tokyo/R9/rstLst/ramen/?popular_spot_id=&SrtT=rt&Srt=D&sort_mode=1")
#CSV保存
tokyo_ramen_review.df.to_csv("output/tokyo_ramen_review_1.csv")

 