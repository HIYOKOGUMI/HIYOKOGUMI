import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import json

# categories.jsonの読み込み
with open('../config/categories.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# select_manual_fileの設定に基づいて参照するファイルを決定
data_folder = '../data/products'
if config.get("select_manual_file", False):  # 設定がTrueなら、ユーザー入力のファイルを使用
    file_name = input("使用するファイル名を入力してください（拡張子.csvを含む）: ")
    file_path = os.path.join(data_folder, file_name)
else:
    # 設定がFalseなら、data/productsフォルダ内の最新ファイルを使用
    file_pattern = os.path.join(data_folder, 'output_*.csv')
    files = glob.glob(file_pattern)
    if files:
        file_path = max(files, key=os.path.getmtime)
    else:
        print("指定されたフォルダにデータファイルが見つかりません。")
        exit()

# 指定したファイルが存在するかチェック
if not os.path.isfile(file_path):
    print("指定されたファイルが見つかりません。")
    exit()

# データの読み込み
data = pd.read_csv(file_path)

# 価格のカンマを削除し、数値型に変換
data_filtered = data[data['price'].str.replace(',', '').str.isnumeric()]
data_filtered['price'] = data_filtered['price'].str.replace(',', '').astype(float)

# 商品状態と対応する色
color_map = {
    '新品、未使用': 'blue',
    '未使用に近い': 'cyan',
    '目立った傷や汚れなし': 'green',
    'やや傷や汚れあり': 'yellow',
    '傷や汚れあり': 'orange',
    '全体的に状態が悪い': 'red'
}

# カラーマップに基づいて色のリストを作成
colors = data_filtered['condition'].map(color_map).fillna('gray')

# 保存するフォルダとファイル名の設定
output_folder = '../data/charts'
os.makedirs(output_folder, exist_ok=True)

# ファイル名を取得し、拡張子を.pngに変更
output_filename = os.path.splitext(os.path.basename(file_path))[0] + '.png'
output_path = os.path.join(output_folder, output_filename)

# グラフの作成と保存
plt.figure(figsize=(6, 12))
plt.scatter(data_filtered['index'], data_filtered['price'], c=colors, marker='o', s=20)  # s=20で点の大きさを調整
plt.xlabel('Index')
plt.ylabel('Price')
plt.title('Price Distribution by Condition')
plt.grid(True)

# ファイル保存
plt.savefig(output_path)
plt.close()

print(f"図が保存されました: {output_path}")
