import pandas as pd
import os
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font

# 最新ファイルを取得する関数
def get_latest_file(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

# ファイルパス設定
statistics_dir = '../../MSS/data/statistics'
products_dir = '../_data/f_products'
suggestion_base_dir = '../_data/f_suggestion'  # 保存先ディレクトリ

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
    # 各行に対して、状態ごとの基準値でフィルタ
    mask = remaining_df.apply(
        lambda row: row['price'] <= statistics_df[row['condition']].iloc[0] * (1 - threshold)
        if row['condition'] in condition_columns else False, axis=1
    )
    
    # 条件に合う行を抽出してデータフレームに追加
    selected_df = remaining_df[mask]
    dataframes.append(selected_df)
    print(f"Data prepared for threshold: {threshold * 100}% with {selected_df.shape[0]} entries")
    
    # 残りのデータから抽出された行を除外
    remaining_df = remaining_df[~mask]

# データフレームをシートとして書き込み、セルの幅を調整
def save_dataframes_to_excel_with_adjustment(dataframes, file_name=merged_file_name):
    sheet_names = ["★", "★★", "★★★", "★★★★", "★★★★★"]  # シート名リスト

    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        for i, df in enumerate(dataframes):
            sheet_name = sheet_names[i]  # シート名を設定
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # 各シートの幅を調整し、URLセルをハイパーリンク化
        workbook = writer.book
        for i, df in enumerate(dataframes):
            worksheet = workbook[sheet_names[i]]
            for col in worksheet.columns:
                max_length = 0
                col_letter = get_column_letter(col[0].column)  # 列の文字番号を取得
                for cell in col:
                    try:
                        # セルの内容の長さを取得して、最大値を更新
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                    # URL列（例えばF列）をハイパーリンクとして設定
                    if col_letter == 'F' and cell.value and isinstance(cell.value, str) and cell.value.startswith("http"):
                        cell.hyperlink = cell.value
                        cell.font = Font(color="0000FF", underline="single")  # ハイパーリンクの見た目に変更

                # B列とD列は個別に幅を広げる
                if col_letter == 'B':
                    adjusted_width = max_length * 1.5  # B列は1.5倍の幅
                elif col_letter == 'D':
                    adjusted_width = max_length * 2  # D列は2倍の幅
                else:
                    adjusted_width = max_length + 2  # 他の列は通常の調整
                worksheet.column_dimensions[col_letter].width = adjusted_width

    print(f"File saved with adjusted column widths and clickable URLs as {file_name}")

# 各データフレームを1つのExcelファイルにシートとして保存し、セル幅を調整
save_dataframes_to_excel_with_adjustment(dataframes)
