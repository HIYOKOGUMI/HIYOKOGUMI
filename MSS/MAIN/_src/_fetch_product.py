import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import os
import glob
import json
from datetime import datetime

# 設定ファイルのパス
CONFIG_PATH = '../config/setting.json'

# categories.jsonを読み込み
with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
    config = json.load(file)

# 必須設定を取得
try:
    data_count = config["data_count"]  # 取得するデータ数
    fetch_product_file_selection_mode_auto = config.get("fetch_product_file_selection_mode_auto", True)  # デフォルトは自動選択
except KeyError as e:
    print(f"Error: 設定 '{e.args[0]}' が setting.json に存在しません。")
    exit(1)

# ChromeDriverのパスを指定
service = Service('C:/chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)

# ディレクトリの設定
urls_folder = '../_data/urls'
products_folder = '../_data/products'
os.makedirs(products_folder, exist_ok=True)

# 最新のCSVファイルを取得する関数
def get_latest_file(directory, pattern='*.csv'):
    files = sorted(glob.glob(os.path.join(directory, pattern)), key=os.path.getmtime)
    if not files:
        raise FileNotFoundError(f"No CSV files found in directory: {directory}")
    return files[-1]  # 一番最後の項目（最も新しいファイル）を取得

# ファイルを選択する関数
def select_file(directory):
    if fetch_product_file_selection_mode_auto:
        # 最新ファイルを自動選択
        return get_latest_file(directory)
    else:
        # 手動でファイル名を入力
        selected_file = input("元データのCSVファイルの名前を入力してください（拡張子なし）: ") + ".csv"
        file_path = os.path.join(directory, selected_file)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"指定されたファイルが存在しません: {file_path}")
        return file_path

# 商品情報を取得する関数
def extract_product_info(url, index, total):
    try:
        # 進行状況を表示
        progress = (index / total) * 100
        print(f"{index}/{total}件目のデータを取得中 - 進捗: {progress:.2f}%")
        
        driver.get(url)
        time.sleep(2)  # ページが完全に読み込まれるまで待機

        name = driver.find_element(By.TAG_NAME, 'h1').text if driver.find_elements(By.TAG_NAME, 'h1') else "N/A"
        price_element = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="price"]')
        spans = price_element.find_elements(By.TAG_NAME, 'span')
        price = spans[1].text if len(spans) > 1 else "N/A"
        condition = driver.find_element(By.CSS_SELECTOR, 'span[data-testid="商品の状態"]').text if driver.find_elements(By.CSS_SELECTOR, 'span[data-testid="商品の状態"]') else "N/A"
        posted_date = next((p.text for p in driver.find_elements(By.CSS_SELECTOR, 'p.merText.body__5616e150.secondary__5616e150') if "前" in p.text), "日付情報なし")

        return {'index': index, 'name': name, 'price': price, 'condition': condition, 'posted_date': posted_date, 'url': url}

    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        return {'index': index, 'name': 'エラー', 'price': 'エラー', 'condition': 'エラー', 'posted_date': '日付情報なし', 'url': url}

# URLファイルの選択
input_file = select_file(urls_folder)
df = pd.read_csv(input_file)
urls = df['商品URL'].head(data_count)
total_urls = len(urls)
data = [extract_product_info(url, i + 1, total_urls) for i, url in enumerate(urls)]

# 商品情報をCSVに保存
current_time = datetime.now().strftime("%Y_%m_%d_%H_%M")
input_filename = os.path.basename(input_file)  # 元のファイル名を取得
output_file = os.path.join(products_folder, f"output_{current_time}_{input_filename}")
product_df = pd.DataFrame(data)
product_df.to_csv(output_file, index=False)
driver.quit()
print(f"商品情報のCSVファイルを作成しました: {output_file}")