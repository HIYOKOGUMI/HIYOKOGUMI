import pandas as pd
import os
import glob
import json
from datetime import datetime

# 設定ファイルのパス
CONFIG_PATH = '../../config/MSS_config/MSS_setting.json'

# MSS_setting.jsonを読み込み
with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
    config = json.load(file)

# 必須設定を取得
try:
    detect_outliers_file_selection_mode_auto = config.get("detect_outliers_file_selection_mode_auto", True)
    detect_outliers_file_data_cleaning_mode = config.get("detect_outliers_file_data_cleaning_mode", "IQR_based")
    detect_outliers_file_data_cleaning_max = config.get("detect_outliers_file_data_cleaning_max", 50000)
    detect_outliers_file_data_cleaning_mini = config.get("detect_outliers_file_data_cleaning_mini", 3000)
except KeyError as e:
    print(f"Error: 設定 '{e.args[0]}' が MSS_setting.json に存在しません。")
    exit(1)

# ディレクトリの設定
products_folder = '../data/products'
cleaned_folder = '../data/cleaned'
os.makedirs(cleaned_folder, exist_ok=True)

# 最新のCSVファイルを取得する関数
def get_latest_file(directory, pattern='*.csv'):
    files = sorted(glob.glob(os.path.join(directory, pattern)), key=os.path.getmtime)
    if not files:
        raise FileNotFoundError(f"No CSV files found in directory: {directory}")
    return files[-1]  # 一番最後の項目（最も新しいファイル）を取得

# ファイルを選択する関数
def select_file(directory):
    if detect_outliers_file_selection_mode_auto:
        # 最新ファイルを自動選択
        return get_latest_file(directory)
    else:
        # 手動でファイル名を入力
        selected_file = input("検出対象のCSVファイルの名前を入力してください（拡張子なし）: ") + ".csv"
        file_path = os.path.join(directory, selected_file)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"指定されたファイルが存在しません: {file_path}")
        return file_path

# 異常値検出関数（IQR_basedモード：四分位範囲による判定）
def detect_outliers_iqr(data):
    data['price'] = pd.to_numeric(data['price'].str.replace(',', ''), errors='coerce')
    def flag_outliers(group):
        Q1, Q3 = group['price'].quantile(0.25), group['price'].quantile(0.75)
        IQR = Q3 - Q1
        group['outlier_flag'] = (group['price'] < Q1 - 1.5 * IQR) | (group['price'] > Q3 + 1.5 * IQR)
        return group
    
    # グループ化と異常値フラグの追加後、conditionカラムを元のデータから再度追加
    result = data.groupby('condition', group_keys=False).apply(flag_outliers, include_groups=False)
    result['condition'] = data['condition']  # グループ化後のデータにconditionカラムを再度追加

    # カラムの順序をpriceの次にconditionが来るように指定
    result = result[['index', 'name', 'price', 'condition', 'posted_date', 'url', 'outlier_flag']]
    return result

# 異常値検出関数（range_basedモード：指定された範囲外の金額による判定）
def detect_outliers_fixed_range(data, min_price, max_price):
    data['price'] = pd.to_numeric(data['price'].str.replace(',', ''), errors='coerce')
    data['outlier_flag'] = (data['price'] < min_price) | (data['price'] > max_price)
    return data[['index', 'name', 'price', 'condition', 'posted_date', 'url', 'outlier_flag']]

# ファイルの選択
input_file = select_file(products_folder)
product_data = pd.read_csv(input_file)

# 異常値を検出し結果を保存
current_time = datetime.now().strftime("%Y_%m_%d_%H_%M")
input_filename = os.path.basename(input_file)  # 元のファイル名を取得

# モードに応じた異常値検出方法を実行
if detect_outliers_file_data_cleaning_mode == "IQR_based":
    product_data_with_outliers = detect_outliers_iqr(product_data)
    outlier_output_file = os.path.join(cleaned_folder, f"cleaned_IQR_based_{current_time}_{input_filename}")
else:
    product_data_with_outliers = detect_outliers_fixed_range(product_data, detect_outliers_file_data_cleaning_mini, detect_outliers_file_data_cleaning_max)
    outlier_output_file = os.path.join(cleaned_folder, f"cleaned_range_based_{current_time}_{input_filename}")

# 結果を保存
product_data_with_outliers.to_csv(outlier_output_file, index=False)
print(f"異常値検出後のファイルを保存しました: {outlier_output_file}")
