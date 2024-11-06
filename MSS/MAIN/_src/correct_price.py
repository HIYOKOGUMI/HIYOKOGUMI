import pandas as pd
import os
from datetime import datetime

# 最新ファイルを取得する関数
def get_latest_file(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

# ファイルパス設定
statistics_dir = '../data/statistics'
products_dir = '../_data/products'
suggestion_base_dir = '../_data/suggestion'  # ベースの保存先ディレクトリ

# 保存先ディレクトリが存在しなければ生成
os.makedirs(suggestion_base_dir, exist_ok=True)

# 最新のstatisticsファイルとproductsファイルを取得
statistics_file = get_latest_file(statistics_dir)
output_file = get_latest_file(products_dir)

# ファイル読み込み
statistics_df = pd.read_csv(statistics_file, encoding='utf-8')
output_df = pd.read_csv(output_file, encoding='utf-8', dtype={'price': str})

# 割合列のデータを数値に変換（パーセント表示が含まれている場合も処理）
statistics_df['割合'] = pd.to_numeric(statistics_df['割合'].replace({'%': ''}, regex=True), errors='coerce') / 100

# priceカラムのカンマを除去して数値化
output_df['price'] = pd.to_numeric(output_df['price'].replace({',': ''}, regex=True), errors='coerce')

# 出力ファイルの名前を元にフォルダ名を設定
output_base_filename = os.path.splitext(os.path.basename(output_file))[0]
timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
suggestion_dir = os.path.join(suggestion_base_dir, f"suggestion_5_{output_base_filename}_{timestamp}")

# 新しい保存フォルダが存在しなければ生成
os.makedirs(suggestion_dir, exist_ok=True)

# ファイル名リストの生成
file_names = [
    os.path.join(suggestion_dir, "s.csv"),
    os.path.join(suggestion_dir, "ss.csv"),
    os.path.join(suggestion_dir, "sss.csv"),
    os.path.join(suggestion_dir, "ssss.csv"),
    os.path.join(suggestion_dir, "sssss.csv")
]

# デバッグ: 使用する割合を確認
percentages = statistics_df['割合'].dropna().sort_values(ascending=False)
for threshold, file_name in zip(percentages, file_names):
    print(f"Using threshold: {threshold * 100}% for file: {file_name}")

# 選別処理
condition_columns = ['新品、未使用', '未使用に近い', '目立った傷や汚れなし', 'やや傷や汚れあり', '傷や汚れあり', '全体的に状態が悪い']
remaining_df = output_df[output_df['price'] >= 17857]

# 各割合に基づいて分類と保存（最も易しい条件から順に処理）
for threshold, file_name in zip(percentages, file_names):
    # 各行に対して、状態ごとの基準値でフィルタ
    mask = remaining_df.apply(
        lambda row: row['price'] <= statistics_df[row['condition']].iloc[0] * (1 - threshold)
        if row['condition'] in condition_columns else False, axis=1
    )
    
    # 条件に合う行を抽出してファイル保存
    selected_df = remaining_df[mask]
    selected_df.to_csv(file_name, index=False)
    print(f"File saved: {file_name} with {selected_df.shape[0]} entries")
    
    # 残りのデータから抽出された行を除外
    remaining_df = remaining_df[~mask]
