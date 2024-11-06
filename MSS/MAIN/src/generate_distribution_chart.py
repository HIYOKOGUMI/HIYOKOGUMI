import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import json

# categories.jsonの読み込み
with open('../config/categories.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# ファイル参照モードの設定に基づくファイルの決定
data_folder = '../data/products'
file_path = None

if config.get("generate_distribution_chart_file_selection_mode_auto", False):
    # モードが自動の場合、最新のファイルを使用
    file_pattern = os.path.join(data_folder, 'output_*.csv')
    files = glob.glob(file_pattern)
    if files:
        file_path = max(files, key=os.path.getmtime)
    else:
        print("指定されたフォルダにデータファイルが見つかりません。")
        exit()
else:
    # モードが手動の場合、ユーザー入力でファイル名を取得し、完全一致するファイルを使用
    file_name = input("使用するファイル名を入力してください（拡張子.csvを含む）: ")
    user_file_path = os.path.join(data_folder, file_name)
    if os.path.isfile(user_file_path):
        file_path = user_file_path
    else:
        print("入力されたファイルが見つかりません。")
        exit()

# 指定したファイルが存在するかチェック
if not file_path:
    print("ファイルパスが設定されていません。")
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

# 保存するフォルダとサブフォルダの設定
output_folder = '../data/charts'
base_filename = os.path.splitext(os.path.basename(file_path))[0]
sub_folder = os.path.join(output_folder, f"{base_filename}_charts")
os.makedirs(sub_folder, exist_ok=True)

# 分散グラフの作成と保存
output_path_distribution = os.path.join(sub_folder, f"{base_filename}.png")

plt.figure(figsize=(6, 12))
plt.scatter(data_filtered['index'], data_filtered['price'], c=colors, marker='o', s=20)
plt.xlabel('Index')
plt.ylabel('Price')
plt.title('Price Distribution by Condition')
plt.grid(True)
plt.savefig(output_path_distribution)
plt.close()
print(f"分散図が保存されました: {output_path_distribution}")

# 全体の金額棒グラフの作成と保存
data_filtered_sorted = data_filtered.sort_values(by='price').reset_index(drop=True)
output_path_sorted_bar = os.path.join(sub_folder, f"{base_filename}_sorted_bar.png")

plt.figure(figsize=(10, 8))
plt.bar(data_filtered_sorted.index, data_filtered_sorted['price'], color=colors, width=1.0)
plt.xlabel('商品 (安い順にソート)')
plt.ylabel('金額')
plt.title('価格分布 (安い順)')
plt.grid(True, axis='y')
plt.savefig(output_path_sorted_bar)
plt.close()
print(f"全体の金額棒グラフが保存されました: {output_path_sorted_bar}")

# 各状態別の金額棒グラフの作成と保存
for condition, color in color_map.items():
    # 状態ごとにデータをフィルタリング
    condition_data = data_filtered_sorted[data_filtered_sorted['condition'] == condition].reset_index(drop=True)
    
    # データが存在する場合のみグラフを作成
    if not condition_data.empty:
        output_path_condition_bar = os.path.join(sub_folder, f"{base_filename}_{condition}_bar.png")

        plt.figure(figsize=(10, 8))
        plt.bar(condition_data.index, condition_data['price'], color=color, width=1.0)
        plt.xlim(0, len(condition_data) - 1)  # 横軸をその状態のデータ数に合わせる
        plt.xlabel('商品 (安い順にソート)')
        plt.ylabel('金額')
        plt.title(f'価格分布 ({condition})')
        plt.grid(True, axis='y')
        plt.savefig(output_path_condition_bar)
        plt.close()
        print(f"{condition}の金額棒グラフが保存されました: {output_path_condition_bar}")
