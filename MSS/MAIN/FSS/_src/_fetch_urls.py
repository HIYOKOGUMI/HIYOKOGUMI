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
from selenium.webdriver.common.action_chains import ActionChains

# JSONファイルからカテゴリー、検索キーワード、ページ数、デバッグモードを読み込む
with open('../../config/FSS_config/FSS_setting.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    main_category = data["main_category"]
    sub_category = data["sub_category"]
    sub_sub_category = data["sub_sub_category"]
    sub_sub_sub_category = data.get("sub_sub_sub_category")  # 新たに追加
    sub_sub_sub_sub_category = data.get("sub_sub_sub_sub_category")  # 新たに追加
    brand_name = data.get("brand", "")
    search_keyword = data["search_keyword"]
    max_pages = data["max_pages"]
    debug_mode = data["debug_mode"]

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

driver_path = "C:/chromedriver.exe"
driver = webdriver.Chrome(service=Service(driver_path), options=options)

# メルカリの検索ページを開く
url = 'https://jp.mercari.com/search'
driver.get(url)
wait = WebDriverWait(driver, 20)

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
    time.sleep(2)
except Exception as e:
    print(f"Error clicking category accordion button: {e}")

# ステップ5: JSONから読み込んだメインカテゴリーを選択
try:
    select_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "select__da4764db")))
    select = Select(select_element)
    select.select_by_visible_text(main_category)  # JSONファイルから読み込み
    time.sleep(2)
except Exception as e:
    print(f"Error selecting '{main_category}': {e}")

# ステップ6: JSONから読み込んだサブカテゴリーを選択
try:
    sub_category_option = wait.until(EC.presence_of_element_located((By.XPATH, f"//option[text()='{sub_category}']")))
    sub_category_option.click()
    time.sleep(2)
except Exception as e:
    print(f"Error selecting '{sub_category}': {e}")

# ステップ7: JSONから読み込んだサブサブカテゴリーを選択
try:
    sub_sub_category_option = wait.until(EC.presence_of_element_located((By.XPATH, f"//option[text()='{sub_sub_category}']")))
    sub_sub_category_option.click()
    time.sleep(2)
except Exception as e:
    print(f"Error selecting '{sub_sub_category}': {e}")

# ステップ8: JSONから読み込んだサブサブサブカテゴリーを選択
try:
    sub_sub_sub_category_option = wait.until(EC.presence_of_element_located((By.XPATH, f"//option[text()='{sub_sub_sub_category}']")))
    sub_sub_sub_category_option.click()
    time.sleep(2)
except Exception as e:
    print(f"Error selecting '{sub_sub_sub_category}': {e}")

# ステップ9: JSONから読み込んだサブサブサブサブカテゴリーがチェックボックスの場合
try:
    all_checkbox_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='すべて']/ancestor::label")))
    all_checkbox_label.click()
    time.sleep(2)
except Exception as e:
    print(f"Error selecting 'すべて' checkbox: {e}")

'''
# 初期値を設定（デベロッパーが手動で調整）
offset_y = 50  # 入力フィールドからのオフセット（px）

# ブランド選択処理
try:
    # ブランドのドロップダウンボタンをクリック
    brand_dropdown_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='ブランド']//button[@id='accordion_button']"))
    )
    brand_dropdown_button.click()
    time.sleep(2)

    # ブランドの入力フィールドを取得して入力
    brand_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@class='merInputNode' and @placeholder='入力してください']"))
    )
    brand_input.clear()
    brand_input.send_keys(brand_name)  # JSONから取得したブランド名を入力
    time.sleep(2)

    # ハイライト表示用のJavaScriptコード
    def highlight_click_position(x, y):
        js_code = f"""
        var marker = document.createElement('div');
        marker.style.position = 'absolute';
        marker.style.left = '{x}px';
        marker.style.top = '{y}px';
        marker.style.width = '10px';
        marker.style.height = '10px';
        marker.style.backgroundColor = 'red';
        marker.style.border = '2px solid black';
        marker.style.borderRadius = '50%';
        marker.style.zIndex = '9999';
        document.body.appendChild(marker);
        setTimeout(() => marker.remove(), 2000);  // 2秒後にマーカーを削除
        """
        driver.execute_script(js_code)

    # ブランド入力フィールドの位置を取得
    input_location = brand_input.location
    input_size = brand_input.size
    click_x = input_location['x'] + input_size['width'] / 2
    click_y = input_location['y'] + input_size['height'] + offset_y

    # ハイライト表示
    highlight_click_position(click_x, click_y)

    # オフセットを使ってクリック
    action = ActionChains(driver)
    action.move_to_element_with_offset(brand_input, 0, offset_y).click().perform()
    time.sleep(2)

    print(f"入力フィールドから {offset_y}px 下をクリックしました。")
except Exception as e:
    print(f"ブランド選択中にエラーが発生しました: {e}")
'''

# ステップ10: 販売状況の「絞り込み」ボタンをクリック
try:
    sales_status_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='販売状況']//button[@id='accordion_button']")))
    sales_status_button.click()
    time.sleep(1)
except Exception as e:
    print(f"Error clicking '販売状況' accordion button: {e}")

# ステップ11: 「売り切れのみ」のチェックボックスをクリック
try:
    sold_out_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='on_sale']")))
    sold_out_checkbox.click()
    time.sleep(1)
except Exception as e:
    print(f"Error clicking '売り切れのみ' checkbox: {e}")

# ステップ12: 検索ボックスに JSON から読み込んだキーワードを入力
try:
    search_box = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='検索キーワードを入力']")))
    search_box.send_keys(search_keyword)  # JSONファイルから読み込み
    time.sleep(1)
except Exception as e:
    print(f"Error entering text into search box: {e}")

# ステップ13: エンターキーを押して検索を実行
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
        driver.execute_script(f"window.scrollBy(0, {increment_scroll});")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    driver.execute_script("window.scrollBy(0, -500);")
    items = driver.find_elements(By.CLASS_NAME, "sc-bcd1c877-2.cvAXgx")
    print(f"Found {len(items)} items on page {page}.")
    for item in items:
        try:
            item_url = item.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            item_urls.append(item_url)
        except Exception as e:
            print(f"Error retrieving item URL: {e}")

    try:
        next_button = driver.find_element(By.XPATH, "//a[contains(text(), '次へ')]")
        next_button.click()
        time.sleep(3)
        page += 1
    except Exception:
        print("No more pages found or error clicking the next page button.")
        break

# 指定ページ数分のURLを取得後に、総ページ数と最終ページのアイテム数を確認する処理
total_pages = page  # 現在のページ数を記録

# 最初のページのURL数を記録
first_page_item_count = len(item_urls) if item_urls else 0

while True:
    try:
        # 「次へ」ボタンが存在する場合はクリックしてページを進める
        next_button = driver.find_element(By.XPATH, "//a[contains(text(), '次へ')]")
        next_button.click()
        time.sleep(3)  # ページが読み込まれるまで待機
        total_pages += 1
    except Exception:
        print("全ページの確認が完了しました。")
        
        # 最終ページのアイテム数を取得
        last_page_items = driver.find_elements(By.CLASS_NAME, "sc-bcd1c877-2.cvAXgx")
        last_page_item_count = len(last_page_items)
        print(f"最終ページのアイテム数: {last_page_item_count}")
        break

# デバッグモードでなければブラウザを自動で閉じる
if not debug_mode:
    driver.quit()
    print("ブラウザを閉じました。")
else:
    print("デバッグモード: 手動でブラウザを閉じてください。")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("デバッグモードを終了しました。")

# 現在の日時を取得し、yyyy,mm,dd,hh,mm形式にフォーマット
now = datetime.now().strftime('%Y_%m_%d_%H_%M')
output_dir = '../_data/f_urls'
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)

file_name = f"{search_keyword}_{now}.csv"
file_path = os.path.join(output_dir, file_name)

df = pd.DataFrame(item_urls, columns=['商品URL'])
df.to_csv(file_path, index=False, encoding='utf-8-sig')

# 推定総アイテム数の計算（最初のページのアイテム数 + (総ページ数 - 2) * 最初のページのアイテム数 + 最終ページのアイテム数）
estimated_total_items = ((total_pages - 1) * (first_page_item_count // max_pages)) + last_page_item_count

df['総ページ数'] = total_pages
df['最終ページアイテム数'] = last_page_item_count
df['推定総アイテム数'] = estimated_total_items

# データフレームを再度CSVファイルに保存（既存ファイルに上書き）
df.to_csv(file_path, index=False, encoding='utf-8-sig')
print(f"総ページ数: {total_pages}、最終ページのアイテム数: {last_page_item_count}、推定総アイテム数: {estimated_total_items} が '{file_path}' に追加されました。")

print(f"取得したURL数: {len(item_urls)}")
print(f"データが '{file_path}' に保存されました。")
print(first_page_item_count // max_pages)
