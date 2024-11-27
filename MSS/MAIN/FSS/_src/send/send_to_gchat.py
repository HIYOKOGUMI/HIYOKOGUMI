import os
import pandas as pd
import re
from datetime import datetime
import requests
import json
import time

# ディレクトリの設定
directory_path = '../../_data/f_suggestion'
config_path = '../../../config/FSS_config/FSS_setting.json'

# Webhook URLの読み込み
def load_webhook_url(filename="dev_url.txt"):  # 本番環境のときはurl.txtに変更、この設定はconfigファイルに移動予定
    with open(filename, "r") as file:
        url = file.readline().strip()
    return url

# Google Chatにメッセージを送信する関数
def send_message_to_google_chat(message):
    webhook_url = load_webhook_url()
    headers = {"Content-Type": "application/json"}
    modified_message = re.sub(r"(https?://\S+)", r"\1\n\n", message)  # URLの後に改行を追加
    payload = {"text": modified_message}
    response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print("メッセージ送信成功")
    else:
        print(f"メッセージ送信失敗: {response.status_code}")

# 最新のファイルを取得する関数
def get_latest_file(directory, prefix):
    # ファイル名の最後の日付部分を抽出する正規表現パターン
    pattern = re.compile(rf"{prefix}.*?_(\d{{4}}_\d{{2}}_\d{{2}}_\d{{2}}_\d{{2}})\.xls[zx]$")
    latest_file = None
    latest_date = None

    for filename in os.listdir(directory):
        match = pattern.search(filename)
        if match:
            file_date_str = match.group(1)
            file_date = datetime.strptime(file_date_str, "%Y_%m_%d_%H_%M")
            if latest_date is None or file_date > latest_date:
                latest_date = file_date
                latest_file = filename

    return latest_file

# 設定ファイルから自動モードを読み込む
def load_auto_mode_from_config(config_path):
    try:
        with open(config_path, "r", encoding="utf-8") as file:  # utf-8エンコーディングを指定
            config = json.load(file)
            return config.get("send_to_gchat_file_selection_mode_auto", True)
    except Exception as e:
        print(f"設定ファイルの読み込みエラー: {e}")
        return True

# 処理するシート名の条件を満たすものを抽出
def process_sheets(file_path):
    # Excelファイルの読み込み
    excel_data = pd.ExcelFile(file_path)
    # 条件：シート名に '%' を含む
    target_sheets = [sheet for sheet in excel_data.sheet_names if '%' in sheet]
    
    for sheet_name in target_sheets:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        # データフレームの内容をメッセージ形式に変換
        text_representation = df.apply(lambda x: ' | '.join(x.astype(str)), axis=1)
        text_content = '\n'.join(text_representation)
        # Google Chatへ送信
        send_message_to_google_chat(f"{sheet_name} シートの内容:\n\n{text_content}")
        time.sleep(1)  # リクエスト制限回避
    send_message_to_google_chat("END\nEND\nEND\nEND\nEND\nEND")
# メイン処理
file_prefix = "suggestion_5_output_"
auto_mode = load_auto_mode_from_config(config_path)

if auto_mode:
    # 自動モードで最新のファイルを取得
    latest_file_name = get_latest_file(directory_path, file_prefix)
else:
    # 手動モードでファイル名を入力
    user_file_name = input("参照するファイル名を入力してください: ")
    latest_file_name = user_file_name if user_file_name in os.listdir(directory_path) else None

if latest_file_name:
    # ファイルのパス
    file_path = os.path.join(directory_path, latest_file_name)

    # 最初に参照ファイル名をGoogle Chatに送信
    send_message_to_google_chat(f"参照ファイル: {latest_file_name}")

    # シートを処理
    process_sheets(file_path)
else:
    print("指定されたファイルが見つかりませんでした。")
