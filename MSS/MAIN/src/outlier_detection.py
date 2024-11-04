import pandas as pd
import os
import json
from glob import glob

# 設定ファイルのパス
CONFIG_PATH = '../config/categories.json'

# 設定ファイルから"select_outlier"の値を取得する関数
def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config.get("select_outlier", False)

# 最新のファイルを取得する関数
def get_latest_file(directory, pattern='output_*_*.csv'):
    files = glob(os.path.join(directory, pattern))
    if not files:  # ファイルが存在しない場合のエラーハンドリング
        raise FileNotFoundError(f"No files matching '{pattern}' found in directory: {directory}")
    latest_file = max(files, key=os.path.getctime)
    return latest_file

# ユーザーが指定したファイルを取得する関数
def get_user_selected_file(directory):
    # ディレクトリ内のファイル一覧を表示
    print("Available files:")
    files = glob(os.path.join(directory, '*.csv'))
    for f in files:
        print(os.path.basename(f))
    
    # ユーザーにファイル名を入力させる
    selected_file = input("Enter the exact file name to load: ").strip()
    file_path = os.path.join(directory, selected_file)
    
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{selected_file}' was not found in directory: {directory}")
    
    return file_path

# 異常値検出関数
def detect_outliers(data):
    # Price列を数値型に変換
    data['price'] = pd.to_numeric(data['price'].str.replace(',', ''), errors='coerce')

    # Conditionごとに異常値を検出
    def flag_outliers(group):
        Q1 = group['price'].quantile(0.25)
        Q3 = group['price'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        group['outlier_flag'] = (group['price'] < lower_bound) | (group['price'] > upper_bound)
        return group

    # グループ化後に"condition"カラムを明示的に保持する方法に変更
    result = data.groupby('condition', group_keys=False).apply(flag_outliers)
    result['condition'] = data['condition']  # グループ化で失われた"condition"を再追加
    return result

# メイン処理
if __name__ == "__main__":
    try:
        # 設定ファイルを読み込み
        select_outlier = load_config()
        
        # ファイル選択の条件分岐
        products_dir = '../data/products'
        if select_outlier:
            # ユーザーにファイル名を指定してもらう
            file_path = get_user_selected_file(products_dir)
        else:
            # 最新のファイルを自動的に取得
            file_path = get_latest_file(products_dir)
        
        print(f"Processing file: {file_path}")
        
        # CSVファイルの読み込み
        data = pd.read_csv(file_path)
        
        # 異常値を検出して新しいカラムを追加
        data = detect_outliers(data)
        
        # 結果の保存ディレクトリを作成（存在しない場合のみ）
        output_dir = '../data/outlier_detection_results'
        os.makedirs(output_dir, exist_ok=True)
        
        # ファイル名を生成し、CSVとして保存
        output_file = os.path.join(output_dir, 'processed_' + os.path.basename(file_path))
        data.to_csv(output_file, index=False)
        print(f"File saved to: {output_file}")
        
    except FileNotFoundError as e:
        print(e)
