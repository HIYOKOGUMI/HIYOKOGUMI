import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import os
from datetime import datetime

# JSONファイルからカテゴリー、検索キーワード、ページ数、デバッグモードを読み込む
with open('../config/categories.json', 'r', encoding='utf-8') as file:

    data = json.load(file)
    main_category = data["main_category"]
    sub_category = data["sub_category"]
    sub_sub_category = data["sub_sub_category"]
    search_keyword = data["search_keyword"]
    max_pages = data["max_pages"]  # ページ数をJSONから取得
    debug_mode = data["debug_mode"]  # デバッグモードをJSONから取得

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

driver_path = "C:/chromedriver.exe"
driver = webdriver.Chrome(service=Service(driver_path), options=options)

# メルカリの検索ページを開く
url = 'https://jp.mercari.com/search'
driver.get(url)
wait = WebDriverWait(driver, 10)

# ステップ1: 「絞り込み」ボタンをクリック
try:
    filter_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='絞り込み']")))
    filter_button.click()
    time.sleep(1)
except Exception as e:
    print(f"Error clicking filter button: {e}")

# ステップ2: 「おすすめ順」を選択する（デフォルトの選択）
try:
    sort_select_element = wait.until(EC.presence_of_element_located((By.NAME, "sortOrder")))
    sort_select = Select(sort_select_element)
    sort_select.select_by_value("score:desc")  # おすすめ順を選択
    time.sleep(1)
except Exception as e:
    print(f"Error selecting 'おすすめ順': {e}")

# ステップ3: 「新しい順」を選択する
try:
    sort_select.select_by_value("created_time:desc")  # 新しい順を選択
    time.sleep(1)
except Exception as e:
    print(f"Error selecting '新しい順': {e}")

# ステップ4: 「カテゴリー」メニューを開く
try:
    category_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@data-testid='category_id']//button[@id='accordion_button']")))
    category_button.click()
    time.sleep(1)
except Exception as e:
    print(f"Error clicking category accordion button: {e}")

# ステップ5: JSONから読み込んだメインカテゴリーを選択
try:
    select_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "select__da4764db")))
    select = Select(select_element)
    select.select_by_visible_text(main_category)  # JSONファイルから読み込み
    time.sleep(1)
except Exception as e:
    print(f"Error selecting '{main_category}': {e}")

# ステップ6: JSONから読み込んだサブカテゴリーを選択
try:
    sub_category_option = wait.until(EC.presence_of_element_located((By.XPATH, f"//option[text()='{sub_category}']")))
    sub_category_option.click()
    time.sleep(1)
except Exception as e:
    print(f"Error selecting '{sub_category}': {e}")

# ステップ7: JSONから読み込んだサブサブカテゴリーを選択
try:
    sub_sub_category_option = wait.until(EC.presence_of_element_located((By.XPATH, f"//option[text()='{sub_sub_category}']")))
    sub_sub_category_option.click()
    time.sleep(1)
except Exception as e:
    print(f"Error selecting '{sub_sub_category}': {e}")

# ステップ8: 販売状況の「絞り込み」ボタンをクリック
try:
    sales_status_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='販売状況']//button[@id='accordion_button']")))
    sales_status_button.click()
    time.sleep(1)
except Exception as e:
    print(f"Error clicking '販売状況' accordion button: {e}")

# ステップ9: 「売り切れのみ」のチェックボックスをクリック
try:
    sold_out_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='sold_out|trading']")))
    sold_out_checkbox.click()
    time.sleep(1)
except Exception as e:
    print(f"Error clicking '売り切れのみ' checkbox: {e}")

# ステップ10: 検索ボックスに JSON から読み込んだキーワードを入力
try:
    search_box = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='検索キーワードを入力']")))
    search_box.send_keys(search_keyword)  # JSONファイルから読み込み
    time.sleep(1)
except Exception as e:
    print(f"Error entering text into search box: {e}")

# ステップ11: エンターキーを押して検索を実行
try:
    search_box.send_keys(Keys.ENTER)
    time.sleep(3)
except Exception as e:
    print(f"Error pressing Enter key: {e}")

# 検索結果のURLを全て取得する処理
item_urls = []  # URLを保存するリスト
page = 1  # ページ番号

while page <= max_pages:  # JSONから取得したmax_pagesに従ってループ
    print(f"Scraping page {page}...")
    
    # スクロール処理を追加 - ゆっくりスクロールして読み込みが完了するまで待つ
    scroll_pause_time = 3  # スクロール後に待つ時間（秒）
    increment_scroll = 1000  # 一回のスクロール量
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # ページを少しずつスクロール
        driver.execute_script(f"window.scrollBy(0, {increment_scroll});")

        # スクロール後、商品が読み込まれるまで待機
        time.sleep(scroll_pause_time)

        # 新しいページの高さを取得
        new_height = driver.execute_script("return document.body.scrollHeight")

        # ページの高さが変わらない場合、すべてのアイテムが読み込まれたと判断
        if new_height == last_height:
            break

        last_height = new_height

    # スクロールが完了したら、500px上にスクロール
    driver.execute_script("window.scrollBy(0, -500);")

    # 検索結果のアイテムを取得
    items = driver.find_elements(By.CLASS_NAME, "sc-bcd1c877-2.cvAXgx")

    print(f"Found {len(items)} items on page {page}.")

    # 各アイテムのURLを取得してリストに追加
    for item in items:
        try:
            item_url = item.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            item_urls.append(item_url)
        except Exception as e:
            print(f"Error retrieving item URL: {e}")

    # 次へボタンをクリックして次のページを読み込む
    try:
        next_button = driver.find_element(By.XPATH, "//a[contains(text(), '次へ')]")
        next_button.click()
        time.sleep(3)  # 次のページが読み込まれるまで待機
        page += 1
    except Exception:
        print("No more pages found or error clicking the next page button.")
        break

# デバッグモードでなければブラウザを自動で閉じる
if not debug_mode:
    driver.quit()
    print("ブラウザを閉じました。")
else:
    print("デバッグモード: 手動でブラウザを閉じてください。")
    try:
        # 手動で停止させるために無限ループを設定
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("デバッグモードを終了しました。")

# 現在の日時を取得し、yyyy,mm,dd,hh,mm形式にフォーマット
now = datetime.now().strftime('%Y_%m_%d_%H_%M')

# ディレクトリを作成（存在しない場合のみ）
output_dir = '../data/urls'
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)

# ファイル名を検索キーワードと現在の日時を合わせた形式にする
file_name = f"{search_keyword}_{now}.csv"
file_path = os.path.join(output_dir, file_name)

# 取得したURLをCSVファイルに保存
df = pd.DataFrame(item_urls, columns=['商品URL'])
df.to_csv(file_path, index=False, encoding='utf-8-sig')

print(f"取得したURL数: {len(item_urls)}")
print(f"データが '{file_path}' に保存されました。")
