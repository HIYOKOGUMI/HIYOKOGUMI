import requests
import json

def load_webhook_url(filename="url.txt"):
    # url.txtファイルからWebhook URLを読み込む
    with open(filename, "r") as file:
        url = file.readline().strip()
    return url

def send_message_to_google_chat(message):
    webhook_url = load_webhook_url()  # URLを読み込む
    headers = {"Content-Type": "application/json"}
    payload = {"text": message}
    response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        print("メッセージ送信成功")
    else:
        print(f"メッセージ送信失敗: {response.status_code}")

# 使用例
send_message_to_google_chat("こんにちは、ひよこ組!!")
