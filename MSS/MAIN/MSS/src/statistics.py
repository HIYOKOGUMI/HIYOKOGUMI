import os
import json
import pandas as pd
import numpy as np
import sys

# ディレクトリの設定
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
data_dir = os.path.join(base_dir, 'data')
cleaned_dir = os.path.join(data_dir, 'cleaned')
statistics_dir = os.path.join(data_dir, 'statistics')
config_file_path = os.path.abspath(os.path.join(base_dir, '..', 'config', 'MSS_setting.json'))

# 統計ディレクトリが存在しない場合は作成
if not os.path.exists(statistics_dir):
    os.makedirs(statistics_dir)

# 設定ファイルの読み込み
with open(config_file_path, 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

# 自動選択モードが有効か確認
if config.get("statistics_file_selection_mode_auto", True):
    # 自動モード: 最新のcleanedファイルを取得
    files = [f for f in os.listdir(cleaned_dir) if f.startswith('cleaned') and f.endswith('.csv')]
    latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(cleaned_dir, x)))
else:
    # 手動モード: ユーザー入力を求める
    print("以下のファイルから選択してください:")
    files = [f for f in os.listdir(cleaned_dir) if f.startswith('cleaned') and f.endswith('.csv')]
    for file_name in files:
        print(f"- {file_name}")
    
    selected_file = input("ファイル名を入力してください: ")
    if selected_file not in files:
        raise ValueError("無効なファイル名が入力されました。")
    latest_file = selected_file

input_file_path = os.path.join(cleaned_dir, latest_file)

# 保存するファイル名を設定（拡張子を .xlsx に変更）
output_file_name = latest_file.replace('cleaned', 'statistics').replace('.csv', '.xlsx')
output_file_path = os.path.join(statistics_dir, output_file_name)

# 割引後のCSV出力ファイルのパスを設定
discount_output_file_path = output_file_path.replace('.xlsx', '_discount.csv')

# データの読み込み
data = pd.read_csv(input_file_path)

# 異常値の除外
filtered_data = data[data['outlier_flag'] == False]

# 条件ごとの集計
results = {}
median_data = {}

# 指定の順番で条件リストを設定
condition_order = [
    "新品、未使用", "未使用に近い", "目立った傷や汚れなし", 
    "やや傷や汚れあり", "傷や汚れあり", "全体的に状態が悪い", "エラー"
]

for condition in condition_order:
    group = filtered_data[filtered_data['condition'] == condition]
    if not group.empty:
        top_5_max = group.nlargest(5, 'price')
        top_5_min = group.nsmallest(5, 'price')
        median_price = group['price'].median()
        mean_price = group['price'].mean()

        # 集計結果を辞書に保存
        results[condition] = {
            'top_5_max': top_5_max[['name', 'price', 'condition', 'posted_date', 'url']],
            'top_5_min': top_5_min[['name', 'price', 'condition', 'posted_date', 'url']],
            'median': median_price,
            'mean': mean_price
        }

        # 中央値データを辞書に追加
        median_data[condition] = median_price if not np.isnan(median_price) else 0  # NaNの場合は0に設定

# エラーURLの収集
error_urls = data[data['outlier_flag'] == True][['url']]

# Excelファイルの書き出し
with pd.ExcelWriter(output_file_path) as writer:
    for condition in condition_order:
        if condition in results:
            stats = results[condition]
            
            # 各セクションを作成し空行を挟んでまとめる
            top_5_max = stats['top_5_max'].assign(Category='Top 5 Max')
            top_5_min = stats['top_5_min'].assign(Category='Top 5 Min')
            median_df = pd.DataFrame([{'condition': condition, 'price': stats['median'], 'Category': 'Median'}])
            mean_df = pd.DataFrame([{'condition': condition, 'price': stats['mean'], 'Category': 'Mean'}])

            # 空のDataFrameを挟んで結合
            condition_df = pd.concat([
                top_5_max, pd.DataFrame(),  # 空行後にTop 5 Max
                top_5_min, pd.DataFrame(),  # 空行後にTop 5 Min
                median_df, pd.DataFrame(),  # 空行後にMedian
                mean_df
            ], ignore_index=True)

            # シートに書き込み
            condition_df.to_excel(writer, sheet_name=condition, index=False)

    # エラーシート
    error_urls.to_excel(writer, sheet_name="エラー", index=False)

# 割引率の設定を設定ファイルから取得、存在しない場合はエラーメッセージを表示して終了
if "statistics_file_discount_rates" in config:
    discount_rates = config["statistics_file_discount_rates"]
else:
    print("エラー: 設定ファイルに 'statistics_file_discount_rates' が見つかりません。")
    sys.exit(1)  # スクリプトを終了

# 割引データの作成
discount_data = []

for rate in discount_rates:
    discount_row = {'割合': f'{int(rate * 100)}%'}
    for condition, median_price in median_data.items():
        # 割引価格を計算し、整数に丸め込み
        discount_price = round(median_price * (1 - rate))
        discount_row[condition] = discount_price
    discount_data.append(discount_row)

# 割引データをDataFrameに変換し、指定のファイルに保存
discount_df = pd.DataFrame(discount_data)
discount_df.to_csv(discount_output_file_path, index=False, encoding='utf-8-sig')

print(f"処理が完了しました。結果は {output_file_path} に保存されています。")
print(f"割合金額データは {discount_output_file_path} に保存されています。")
