from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import csv
import os

app = Flask(__name__)

# グローバル変数
active_sessions = {}  # 進行中の勤務セッション（氏名ごとに管理）

# 氏名リストをJSONから読み込む
def load_employee_names():
    # ファイルがあるとして簡単にデータをサンプル化
    return ["佐藤太郎", "田中花子", "山田次郎"]

# CSVファイル名を生成（名前に基づく）
def get_csv_filename(account_name):
    return f"{account_name}.csv"

# CSVファイルの既存データを読み込む（その人のファイルのみ）
def load_existing_data(account_name):
    filename = get_csv_filename(account_name)
    data = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    return data

# CSVにセッションデータを保存（行を追加または更新）
def save_session_data(account_name, session_data):
    filename = get_csv_filename(account_name)
    data = load_existing_data(account_name)

    # 該当する行を見つけて更新（退勤と休憩のみ）
    updated = False
    for row in data:
        if row['退勤時刻'] == '':  # 退勤がまだされていない行を見つける
            row.update(session_data)
            updated = True
            break

    if not updated:  # 新しい行として出勤時の情報を追加
        data.append(session_data)

    # データをCSVに書き戻す
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['氏名', '出勤時刻', '休憩開始', '休憩終了', '退勤時刻', '勤務時間']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# 時間差を計算して勤務時間を取得
def calculate_work_time(start_time, total_break_seconds=0):
    end_time = datetime.now()
    total_work_time = end_time - start_time
    total_work_seconds = total_work_time.total_seconds() - total_break_seconds
    hours, remainder = divmod(total_work_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}"

# 打刻処理
@app.route('/punch', methods=['POST'])
def punch():
    global active_sessions
    name = request.form['name']
    action = request.form['action']
    
    current_time = datetime.now().strftime("%H:%M")
    
    # 出勤時（必ず新しい行を作成）
    if action == '出勤':
        # 新しい出勤データを作成
        active_sessions[name] = {
            '氏名': name,
            '出勤時刻': current_time,
            '休憩開始': '',
            '休憩終了': '',
            '退勤時刻': '',
            '勤務時間': ''
        }
        save_session_data(name, active_sessions[name])  # 常に新しい行を追加

    # 休憩開始時（同じ行の休憩部分を更新）
    elif action == '休憩開始' and name in active_sessions:
        active_sessions[name]['休憩開始'] = current_time
        save_session_data(name, active_sessions[name])  # 更新のみ

    # 休憩終了時（同じ行の休憩部分を更新）
    elif action == '休憩終了' and name in active_sessions:
        active_sessions[name]['休憩終了'] = current_time
        save_session_data(name, active_sessions[name])  # 更新のみ

    # 退勤時（同じ行に退勤と勤務時間を追加）
    elif action == '退勤' and name in active_sessions:
        active_sessions[name]['退勤時刻'] = current_time

        # 勤務時間を計算
        start_time = datetime.strptime(active_sessions[name]['出勤時刻'], "%H:%M")
        total_work_time = calculate_work_time(start_time)
        active_sessions[name]['勤務時間'] = total_work_time

        save_session_data(name, active_sessions[name])  # 更新のみ

        # セッション終了
        del active_sessions[name]
    
    return redirect(url_for('index'))

# トップページ（氏名選択とボタンの表示）
@app.route('/')
def index():
    names = load_employee_names()
    return render_template('index.html', names=names)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
