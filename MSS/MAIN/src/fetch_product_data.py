import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import glob
import json
import re
from datetime import datetime  # 現在時刻取得のため

# categories.jsonを読み込む
with open('../config/categories.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

# 必須設定を取得
try:
    data_count = config["data_count"]  # 取得するデータ数
    use_latest_file = config["use_latest_file"]  # 最新ファイルを使用するか
except KeyError as e:
    print(f"Error: 設定 '{e.args[0]}' が categories.json に存在しません。")
    exit(1)

# ChromeDriverのパスを指定
service = Service('C:/chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)

# ディレクトリを作成（存在しない場合に作成）
output_folder = '../data/products'
os.makedirs(output_folder, exist_ok=True)

# 最新ファイルを参照するかどうかの条件分岐
if use_latest_file:
    # 最新のCSVファイルを取得
    list_of_files = glob.glob('../data/urls/*.csv')
    if not list_of_files:
        print("Error: 'data' フォルダー内にCSVファイルが見つかりません。")
        exit(1)
    latest_file = max(list_of_files, key=os.path.getmtime)  # 最新のファイルを選択
    input_file = latest_file
    print(f"最新のCSVファイルを使用しています: {input_file}")
else:
    # ユーザーにファイル名を入力させる
    input_file = input("元データのCSVファイルの名前を入力してください（拡張子なし）: ").strip()
    if not input_file.endswith(".csv"):
        input_file += ".csv"  # 拡張子がなければ追加
    input_file = f'../data/urls/{input_file}'

    # ファイルの存在確認
    if not os.path.exists(input_file):
        print(f"Error: ファイルが見つかりません - {input_file}")
        exit(1)

# 現在時刻を取得してフォーマット（yyyy_mm_dd_hh_mm）
current_time = datetime.now().strftime("%Y_%m_%d_%H_%M")

# 出力ファイル名の設定：outputの直後に現在時刻を追加
input_filename = os.path.basename(input_file)  # 元のファイル名を取得
output_filename = f"output_{current_time}_{input_filename}"
output_file = os.path.join(output_folder, output_filename)

# 商品情報を取得する関数
def extract_product_info(url, index):
    try:
        driver.get(url)
        time.sleep(2)  # ページが完全に読み込まれるまで待機

        # 商品名の取得
        name = driver.find_element(By.TAG_NAME, 'h1').text if driver.find_elements(By.TAG_NAME, 'h1') else "N/A"

        # 金額の取得 (2つ目のspanを選択)
        price_element = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="price"]')
        spans = price_element.find_elements(By.TAG_NAME, 'span')
        if len(spans) > 1:
            price = spans[1].text  # 2つ目のspanタグから金額を取得
        else:
            price = "N/A"

        # 商品状態の取得
        condition = driver.find_element(By.CSS_SELECTOR, 'span[data-testid="商品の状態"]').text if driver.find_elements(By.CSS_SELECTOR, 'span[data-testid="商品の状態"]') else "N/A"

        # 日付に関する文字列の取得（「前」を含む<p>要素を検索）
        posted_date = "日付情報なし"
        p_elements = driver.find_elements(By.CSS_SELECTOR, 'p.merText.body__5616e150.secondary__5616e150')
        for p in p_elements:
            if "前" in p.text:  # 「前」という文字が含まれているかをチェック
                posted_date = p.text
                break

        print(f"商品名: {name}")
        print(f"価格: {price}")
        print(f"商品の状態: {condition}")
        print(f"掲載日: {posted_date}")
        print(f"URL: {url}")

        return {
            'index': index,
            'name': name,
            'price': price,
            'condition': condition,
            'posted_date': posted_date,
            'url': url  # URLをカラムに追加
        }

    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        return {
            'index': index,
            'name': 'エラー',
            'price': 'エラー',
            'condition': 'エラー',
            'posted_date': '日付情報なし',
            'url': url  # URLをエラー時にも追加
        }

# CSVファイルを読み込む
df = pd.read_csv(input_file)

# 指定されたデータ数に基づいて商品情報を取得
urls = df['商品URL'].head(data_count)
data = []

for i, url in enumerate(urls):
    data.append(extract_product_info(url, i + 1))  # インデックス番号を追加

# データをCSVとして保存
product_df = pd.DataFrame(data)
product_df.to_csv(output_file, index=False)

print(f"商品情報のCSVファイルを作成しました: {output_file}")
driver.quit()
