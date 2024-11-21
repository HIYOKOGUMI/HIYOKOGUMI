import pandas as pd
import os
import re
import json
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font

# 設定ファイルのパス
config_path = '../../config/FSS_config/FSS_setting.json'

# 設定ファイルの読み込み
with open(config_path, 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)
suggestion_file_selection_mode_auto = config.get("suggestion_file_selection_mode_auto", True)

# CSVファイルから日付と時刻が最新のファイルを取得する関数
def get_latest_csv_by_date(directory, prefixes):
    # プレフィックスが複数ある場合を考慮して正規表現を作成
    prefix_pattern = "|".join([re.escape(prefix) for prefix in prefixes])
    # プレフィックス + 最初のタイムスタンプ + 任意の文字列 + .csv にマッチ
    pattern = re.compile(rf"({prefix_pattern})(\d{{4}}_\d{{2}}_\d{{2}}_\d{{2}}_\d{{2}}).*\.csv$")
    latest_file = None
    latest_datetime = None

    # デバッグ用: 指定されたディレクトリとファイルを表示
    print(f"Checking directory: {directory}")
    print(f"Files in directory: {os.listdir(directory)}")

    for filename in os.listdir(directory):
        print(f"Checking file: {filename}")  # デバッグ用
        match = pattern.search(filename)
        if match:
            # 最初のタイムスタンプを抽出
            file_datetime = datetime.strptime(match.group(2), "%Y_%m_%d_%H_%M")
            print(f"Matched file: {filename}, extracted datetime: {file_datetime}")  # デバッグ用
            if latest_datetime is None or file_datetime > latest_datetime:
                latest_datetime = file_datetime
                latest_file = os.path.join(directory, filename)

    if latest_file is None:
        raise FileNotFoundError(f"指定されたプレフィックスのCSVファイルが {directory} に見つかりませんでした。")

    return latest_file

# 指定されたファイルを取得する関数
def get_file_by_name(directory, filename):
    file_path = os.path.join(directory, filename)
    if os.path.isfile(file_path):
        return file_path
    else:
        raise FileNotFoundError(f"指定されたファイルが見つかりません: {filename}")

# ファイルパス設定
statistics_dir = '../../MSS/data/statistics'
products_dir = '../_data/f_products'
suggestion_base_dir = '../_data/f_suggestion'  # 保存先ディレクトリ

# 保存先ディレクトリが存在しなければ生成
os.makedirs(suggestion_base_dir, exist_ok=True)

# ファイルの選択
if suggestion_file_selection_mode_auto:
    # 自動モードの場合、最新のCSVファイルを取得
    statistics_file = get_latest_csv_by_date(statistics_dir, ["statistics_IQR_based_", "statistics_range_based_"])
    output_file = get_latest_csv_by_date(products_dir, ["output_"])  # プレフィックスを正確に指定
else:
    # 手動モードの場合、ユーザーにファイル名を2回入力させる
    statistics_input = input("参照する statistics ファイル名を入力してください: ")
    output_input = input("参照する output ファイル名を入力してください: ")
    statistics_file = get_file_by_name(statistics_dir, statistics_input)
    output_file = get_file_by_name(products_dir, output_input)

# デバッグログ出力
print(f"参照された statistics ファイル: {statistics_file}")
print(f"参照された output ファイル: {output_file}")

# ファイル読み込み
statistics_df = pd.read_csv(statistics_file, encoding='utf-8')
output_df = pd.read_csv(output_file, encoding='utf-8', dtype={'price': str})

# 割合列のデータを数値に変換（パーセント表示が含まれている場合も処理）
statistics_df['割合'] = pd.to_numeric(statistics_df['割合'].replace({'%': ''}, regex=True), errors='coerce') / 100

# priceカラムのカンマを除去して数値化
output_df['price'] = pd.to_numeric(output_df['price'].replace({',': ''}, regex=True), errors='coerce')

# 出力ファイル名の設定（suggestion_5_outputの命名規則に従う）
output_base_filename = os.path.splitext(os.path.basename(output_file))[0]
timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
merged_file_name = os.path.join(suggestion_base_dir, f"suggestion_5_output_{timestamp}_{output_base_filename}.xlsx")

# デバッグ: 使用する割合を確認
percentages = statistics_df['割合'].dropna().sort_values(ascending=False)
for threshold in percentages:
    print(f"Using threshold: {threshold * 100}%")

# 選別処理
condition_columns = ['新品、未使用', '未使用に近い', '目立った傷や汚れなし', 'やや傷や汚れあり', '傷や汚れあり', '全体的に状態が悪い']
remaining_df = output_df[output_df['price'] >= 17857]

# 各割合に基づいて分類し、データフレームをリストに追加
dataframes = []
for threshold in percentages:
    mask = remaining_df.apply(
        lambda row: row['price'] <= statistics_df[row['condition']].iloc[0] * (1 - threshold)
        if row['condition'] in condition_columns else False, axis=1
    )
    
    selected_df = remaining_df[mask]
    dataframes.append(selected_df)
    print(f"Data prepared for threshold: {threshold * 100}% with {selected_df.shape[0]} entries")
    
    remaining_df = remaining_df[~mask]

# データフレームをシートとして書き込み、セルの幅を調整
def save_dataframes_to_excel_with_adjustment(dataframes, file_name=merged_file_name):
    sheet_names = ["★", "★★", "★★★", "★★★★", "★★★★★"]

    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        for i, df in enumerate(dataframes):
            sheet_name = sheet_names[i]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        workbook = writer.book
        for i, df in enumerate(dataframes):
            worksheet = workbook[sheet_names[i]]
            for col in worksheet.columns:
                max_length = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                    if col_letter == 'F' and cell.value and isinstance(cell.value, str) and cell.value.startswith("http"):
                        cell.hyperlink = cell.value
                        cell.font = Font(color="0000FF", underline="single")

                if col_letter == 'B':
                    adjusted_width = max_length * 1.5
                elif col_letter == 'D':
                    adjusted_width = max_length * 2
                else:
                    adjusted_width = max_length + 2
                worksheet.column_dimensions[col_letter].width = adjusted_width

    print(f"File saved with adjusted column widths and clickable URLs as {file_name}")

# 各データフレームを1つのExcelファイルにシートとして保存し、セル幅を調整
save_dataframes_to_excel_with_adjustment(dataframes)
