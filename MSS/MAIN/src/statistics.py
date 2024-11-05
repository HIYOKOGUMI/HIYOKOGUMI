import os
import json
import pandas as pd

# ディレクトリの設定
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
data_dir = os.path.join(base_dir, 'data')
cleaned_dir = os.path.join(data_dir, 'cleaned')
statistics_dir = os.path.join(data_dir, 'statistics')
config_file_path = os.path.join(base_dir, 'config', 'categories.json')

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

# データの読み込み
data = pd.read_csv(input_file_path)

# 異常値の除外
filtered_data = data[data['outlier_flag'] == False]

# 条件ごとの集計
results = {}
for condition, group in filtered_data.groupby('condition'):
    top_5_max = group.nlargest(5, 'price')
    top_5_min = group.nsmallest(5, 'price')
    median_price = group['price'].median()
    mean_price = group['price'].mean()

    results[condition] = {
        'top_5_max': top_5_max[['name', 'price', 'condition', 'posted_date', 'url']],
        'top_5_min': top_5_min[['name', 'price', 'condition', 'posted_date', 'url']],
        'median': median_price,
        'mean': mean_price
    }

# エラーURLの収集
error_urls = data[data['outlier_flag'] == True][['url']]

# Excelファイルの書き出し
with pd.ExcelWriter(output_file_path) as writer:
    for condition in ["新品、未使用", "未使用に近い", "目立った傷や汚れなし", "やや傷や汚れあり", "傷や汚れあり", "全体的に状態が悪い", "エラー"]:
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

print(f"処理が完了しました。結果は {output_file_path} に保存されています。")
