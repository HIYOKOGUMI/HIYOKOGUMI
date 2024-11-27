import pandas as pd
import os
import re
import json
from datetime import datetime
from openpyxl.utils import get_column_letter
from openpyxl import Workbook

# 割引率リストを設定ファイルから取得
config_path = '../../config/FSS_config/FSS_setting.json'
with open(config_path, 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)
discount_rates = config.get("suggestion_file_discount_rates", [0.05, 0.04, 0.03, 0.02, 0.01])

# ファイルパスの設定（元の構成を維持）
statistics_dir = '../../MSS/data/statistics'
products_dir = '../_data/f_products'
suggestion_base_dir = '../_data/f_suggestion'

# 保存先ディレクトリ
os.makedirs(suggestion_base_dir, exist_ok=True)

# 最新のCSVファイルを取得する関数（元の正規表現を維持）
def get_latest_csv_by_date(directory, prefixes):
    prefix_pattern = "|".join([re.escape(prefix) for prefix in prefixes])
    pattern = re.compile(rf"({prefix_pattern})(\d{{4}}_\d{{2}}_\d{{2}}_\d{{2}}_\d{{2}}).*\.csv$")
    latest_file = None
    latest_datetime = None

    for filename in os.listdir(directory):
        match = pattern.search(filename)
        if match:
            file_datetime = datetime.strptime(match.group(2), "%Y_%m_%d_%H_%M")
            if latest_datetime is None or file_datetime > latest_datetime:
                latest_datetime = file_datetime
                latest_file = os.path.join(directory, filename)

    if latest_file is None:
        raise FileNotFoundError(f"指定されたプレフィックスのCSVファイルが {directory} に見つかりませんでした。")

    return latest_file

# 最新ファイルの取得
statistics_file = get_latest_csv_by_date(statistics_dir, ["statistics_range_based_"])
output_file = get_latest_csv_by_date(products_dir, ["output_"])

# outputファイル名から末尾文字列を取得
output_file_base = os.path.basename(output_file)
output_suffix = output_file_base.split("output_")[1]  # "yyyy_mm_dd_hh_mm_アークテリクス"を取得
output_suffix = "_".join(output_suffix.split("_")[5:])  # "アークテリクス"以降の文字列を抽出

# 出力ファイル名の設定
timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
output_file_base_with_suffix = f"suggestion_5_{output_file_base.rsplit('.', 1)[0]}_{timestamp}.xlsx"
output_excel_file = os.path.join(suggestion_base_dir, output_file_base_with_suffix)

# データの読み込み
statistics_df = pd.read_csv(statistics_file, encoding='utf-8')
output_df = pd.read_csv(output_file, encoding='utf-8')

# outputファイルのprice列に含まれるカンマを削除して数値型に変換
output_df['price'] = pd.to_numeric(output_df['price'].replace({',': ''}, regex=True), errors='coerce')

# データフレームリスト（割引率ごとの分類結果を格納）
dataframes = {f"{int(rate * 100)}%_{output_suffix}": [] for rate in discount_rates}
debug_logs = []

# 状態ごとに割引率を適用して分類
for _, row in statistics_df.iterrows():
    condition = row['状態']
    average_price = row['平均値']

    # 該当する商品のフィルタリング
    condition_df = output_df[output_df['condition'] == condition].copy()

    for discount_rate in discount_rates:
        threshold = average_price * (1 - discount_rate)
        selected_df = condition_df[condition_df['price'] <= threshold].copy()

        # デバッグログの記録
        for _, selected_row in selected_df.iterrows():
            debug_logs.append({
                "商品名": selected_row["name"],
                "状態": selected_row["condition"],
                "元価格": selected_row["price"],
                "割引率": f"{int(discount_rate * 100)}%",
                "閾値": threshold
            })

        # 該当する割引率のシートに商品を追加
        selected_df['割引率'] = f"{int(discount_rate * 100)}%"
        dataframes[f"{int(discount_rate * 100)}%_{output_suffix}"].append(selected_df)

        # すでに分類された商品を除外
        condition_df = condition_df[~condition_df.index.isin(selected_df.index)]

# 割引率ごとのデータフレームを統合
for rate, dfs in dataframes.items():
    dataframes[rate] = pd.concat(dfs) if dfs else pd.DataFrame(columns=output_df.columns)

# Excelファイルへの保存
with pd.ExcelWriter(output_excel_file, engine='openpyxl') as writer:
    # 割引率ごとのシートに分類結果を保存
    for rate, df in dataframes.items():
        df.to_excel(writer, sheet_name=rate, index=False)

    # statisticsシートを追加
    statistics_df.to_excel(writer, sheet_name="statistics", index=False)

    # debug_logシートを追加
    debug_log_df = pd.DataFrame(debug_logs)
    debug_log_df.to_excel(writer, sheet_name="debug_log", index=False)

    # referenceシートを追加
    reference_df = pd.DataFrame({
        "File Type": ["Statistics File", "Products File"],
        "File Name": [os.path.basename(statistics_file), os.path.basename(output_file)]
    })
    reference_df.to_excel(writer, sheet_name="reference", index=False)

print(f"分類結果がExcelファイルに保存されました: {output_excel_file}")
