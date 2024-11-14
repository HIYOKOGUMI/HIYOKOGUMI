import os
import pandas as pd
import re
from datetime import datetime
import requests
import json
import time

# ディレクトリの設定
directory_path = '../../_data/f_suggestion'

# Webhook URLの読み込み
def load_webhook_url(filename="url.txt"):
    # url.txtファイルからWebhook URLを読み込む
    with open(filename, "r") as file:
        url = file.readline().strip()
    return url

# Google Chatにメッセージを送信する関数
def send_message_to_google_chat(message):
    webhook_url = load_webhook_url()  # URLを読み込む
    headers = {"Content-Type": "application/json"}
    payload = {"text": message}
    response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        print("メッセージ送信成功")
    else:
        print(f"メッセージ送信失敗: {response.status_code}")

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

# メイン処理
file_prefix = "suggestion_5_output_"
latest_file_name = get_latest_file(directory_path, file_prefix)

if latest_file_name:
    # ファイルのパス
    file_path = os.path.join(directory_path, latest_file_name)
    
    # Excelファイルを読み込む
    excel_data = pd.read_excel(file_path, sheet_name=None)

    # 各シートを処理してパイプ区切りのテキストに変換し、Google Chatへ送信
    for sheet_name in ["★", "★★", "★★★", "★★★★", "★★★★★"]:
        if sheet_name in excel_data:
            # 各セルを文字列に変換し、カラム間に | を挿入
            df = excel_data[sheet_name]
            text_representation = df.apply(lambda x: ' | '.join(x.astype(str)), axis=1)
            text_content = '\n'.join(text_representation)

            # メッセージをGoogle Chatに送信
            send_message_to_google_chat(f"{sheet_name}シートの内容:\n{text_content}")
            
            # リクエスト制限を回避するために5秒の待機時間を追加
            time.sleep(1)
else:
    print("最新の日付のファイルが見つかりませんでした。")
