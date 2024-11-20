import PySimpleGUI as sg
import json
from collections import OrderedDict

# 保存するJSONデータの初期形式（順序を明確に定義）
default_data = OrderedDict([
    ("main_category", "スマホ・タブレット・パソコン"),
    ("sub_category", "スマートフォン・携帯電話"),
    ("sub_sub_category", "スマートフォン本体"),
    ("sub_sub_sub_category", ""),
    ("sub_sub_sub_sub_category", ""),
    ("brand", "アンドロイド"),
    ("search_keyword", "aquos sense8"),
    ("max_pages", 1),
    ("debug_mode", False),
    ("data_count", 3),
    ("fetch_product_file_selection_mode_auto", True),
    ("detect_outliers_file_selection_mode_auto", True),
    ("detect_outliers_file_data_cleaning_mode", "IQR_based"),
    ("detect_outliers_file_data_cleaning_mini", 85000),
    ("detect_outliers_file_data_cleaning_max", 250000),
    ("statistics_file_selection_mode_auto", True),
    ("statistics_file_discount_rates", [0.02, 0.05, 0.10, 0.15, 0.20]),
    ("generate_distribution_chart_file_selection_mode_auto", True)
])

# プリセットファイルのパス
preset_file = "presets.json"

# プリセットを読み込む
def load_presets():
    try:
        with open(preset_file, 'r', encoding='utf-8') as file:
            data = json.load(file, object_pairs_hook=OrderedDict)  # OrderedDictで読み込む
            if data:
                return data
    except FileNotFoundError:
        pass
    return OrderedDict({"default": default_data})

# プリセットを保存する
def save_presets(presets):
    with open(preset_file, 'w', encoding='utf-8') as file:
        json.dump(presets, file, indent=4, ensure_ascii=False, sort_keys=False)

# JSONを保存
def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False, sort_keys=False)

# GUIを使って編集
def edit_json(file_path):
    # プリセットを読み込む
    presets = load_presets()
    current_preset = "default"
    current_data = presets[current_preset]

    # 順序を保ちながらGUIのレイアウトを作成
    layout = []
    for key, value in default_data.items():  # `default_data` の順序を基にループ
        if key == "detect_outliers_file_data_cleaning_mode":
            layout.append([sg.Text(key), sg.Combo(['IQR_based', 'range_based'], default_value=value, key=key)])
        elif isinstance(value, bool):
            layout.append([sg.Text(key), sg.Checkbox("", default=value, key=key)])
        elif isinstance(value, list):
            layout.append([sg.Text(key), sg.InputText(', '.join(map(str, value)), key=key)])
        else:
            layout.append([sg.Text(key), sg.InputText(value, key=key)])
    
    # プリセット選択と保存ボタンを配置
    layout.append([sg.Text("プリセット選択:"), sg.Combo(list(presets.keys()), default_value=current_preset, key="preset_selector", enable_events=True)])
    layout.append([sg.Button("保存"), sg.Button("プリセット登録して保存"), sg.Button("終了")])

    # ウィンドウを表示
    window = sg.Window("JSON Editor", layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "終了"):
            break
        if event == "保存":
            # 現在のGUI値でJSONを保存
            for key in current_data.keys():
                current_data[key] = values[key]
            save_json(file_path, current_data)
            window.close()  # 保存後にウィンドウを閉じる
            break
        elif event == "プリセット登録して保存":
            # 新しいプリセットを登録して保存
            preset_name = values.get("search_keyword")  # プリセット名をsearch_keywordの値にする
            if preset_name:
                presets[preset_name] = OrderedDict((key, values[key]) for key in default_data.keys())
                save_presets(presets)
                sg.popup(f"プリセット '{preset_name}' を保存しました。")
                # プルダウンに新しいプリセットを追加
                window["preset_selector"].update(values=list(presets.keys()), value=preset_name)
        elif event == "preset_selector":
            # プリセットを適用
            selected_preset = values["preset_selector"]
            if selected_preset in presets:
                current_data = presets[selected_preset]
                for key, value in current_data.items():
                    window[key].update(value)

    window.close()

# 実行
json_file_path = "MSS_setting.json"  # JSONファイルのパスを指定
edit_json(json_file_path)
