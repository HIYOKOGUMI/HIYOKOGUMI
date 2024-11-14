import os
import pandas as pd
import re
from datetime import datetime

# ディレクトリの設定
directory_path = '../../_data/f_suggestion'

# 最新のファイルを取得するための関数
def get_latest_file(directory, prefix):
    # ファイル名のパターンを指定
    pattern = re.compile(rf"{prefix}(\d{{4}}_\d{{2}}_\d{{2}}_\d{{2}}_\d{{2}})_output_\d{{4}}_\d{{2}}_\d{{2}}_\d{{2}}_\d{{2}}.*\.xlsx")
    latest_file = None
    latest_date = None

    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            file_date_str = match.group(1)
            file_date = datetime.strptime(file_date_str, "%Y_%m_%d_%H_%M")
            if latest_date is None or file_date > latest_date:
                latest_date = file_date
                latest_file = filename

    return latest_file

# 最新のファイルを取得
file_prefix = "suggestion_5_output_"
latest_file_name = get_latest_file(directory_path, file_prefix)

if latest_file_name:
    # ファイルのパス
    file_path = os.path.join(directory_path, latest_file_name)
    
    # Excelファイルを読み込む
    excel_data = pd.read_excel(file_path, sheet_name=None)

    # 各シートを処理してパイプ区切りのテキストに変換
    for sheet_name, df in excel_data.items():
        # 各セルを文字列に変換し、カラム間に | を挿入
        text_representation = df.apply(lambda x: ' | '.join(x.astype(str)), axis=1)
        text_content = '\n'.join(text_representation)

        # 出力するテキストファイル名
        output_filename = f"{sheet_name}_formatted.txt"
        output_path = os.path.join(directory_path, output_filename)

        # UTF-8エンコーディングでテキストファイルに保存
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(text_content)
            
        print(f"Saved: {output_path}")
else:
    print("最新の日付のファイルが見つかりませんでした。")
