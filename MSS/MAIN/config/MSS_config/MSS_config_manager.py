import PySimpleGUI as sg
import json
from collections import OrderedDict

# 保存するJSONデータの初期形式（順序を明確に定義）
default_data = OrderedDict([
    ("main_category", ""),
    ("sub_category", ""),
    ("sub_sub_category", ""),
    ("sub_sub_sub_category", ""),
    ("sub_sub_sub_sub_category", ""),
    ("brand", ""),
    ("search_keyword", ""),
    ("max_pages", 0),
    ("debug_mode", False),
    ("data_count", 0),
    ("fetch_product_file_selection_mode_auto", True),
    ("detect_outliers_file_selection_mode_auto", True),
    ("detect_outliers_file_data_cleaning_mode", "IQR_based"),
    ("detect_outliers_file_data_cleaning_mini", 0),
    ("detect_outliers_file_data_cleaning_max", 0),
    ("statistics_file_selection_mode_auto", True),
    ("generate_distribution_chart_file_selection_mode_auto", True)
])

# プリセットファイルのパス
preset_file = "MSS_presets.json"
settings_file = "MSS_setting.json"

# プリセットを読み込む
def load_presets():
    try:
        with open(preset_file, 'r', encoding='utf-8') as file:
            return json.load(file, object_pairs_hook=OrderedDict)
    except FileNotFoundError:
        return OrderedDict({"default": default_data})

# プリセットを保存する
def save_presets(presets):
    with open(preset_file, 'w', encoding='utf-8') as file:
        json.dump(presets, file, indent=4, ensure_ascii=False, sort_keys=False)

# 設定ファイルを保存する
def save_settings(settings):
    with open(settings_file, 'w', encoding='utf-8') as file:
        json.dump(settings, file, indent=4, ensure_ascii=False, sort_keys=False)

# GUIを使って編集
def edit_json():
    # プリセットを読み込む
    presets = load_presets()
    current_preset = "default"
    current_data = presets[current_preset].copy()  # デフォルトのデータをコピーして使用

    # current_data に存在しないキーをデフォルト値で補完
    for key, default_value in default_data.items():
        if key not in current_data:
            current_data[key] = default_value

    # GUIのレイアウトを作成
    layout = []
    for key, value in default_data.items():
        if isinstance(value, bool):
            layout.append([sg.Text(key), sg.Checkbox("", default=current_data[key], key=key)])
        else:
            layout.append([sg.Text(key), sg.InputText(current_data[key], key=key)])

    layout.append([sg.Text("プリセット選択:"), sg.Combo(list(presets.keys()), default_value=current_preset, key="preset_selector", enable_events=True)])
    layout.append([sg.Button("保存"), sg.Button("プリセット登録して保存"), sg.Button("終了")])

    # ウィンドウを表示
    window = sg.Window("MSS Config Manager", layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "終了"):
            break
        elif event == "保存":
            # 現在のデータを保存
            for key in default_data.keys():
                if isinstance(default_data[key], bool):
                    current_data[key] = values[key]  # Checkboxの値をTrue/Falseとして保存
                elif isinstance(default_data[key], int):
                    current_data[key] = int(values[key])
                elif isinstance(default_data[key], float):
                    current_data[key] = float(values[key])
                else:
                    current_data[key] = values[key]
            save_settings(current_data)  # 設定ファイルを保存
            window.close()
        elif event == "プリセット登録して保存":
            # 新しいプリセットを保存
            preset_name = values["search_keyword"]
            if preset_name in presets:
                sg.popup(f"プリセット '{preset_name}' はすでに存在します。別の名前を入力してください。")
            else:
                new_preset = default_data.copy()
                for key in default_data.keys():
                    if isinstance(default_data[key], bool):
                        new_preset[key] = values[key]
                    elif isinstance(default_data[key], int):
                        new_preset[key] = int(values[key])
                    elif isinstance(default_data[key], float):
                        new_preset[key] = float(values[key])
                    else:
                        new_preset[key] = values[key]
                presets[preset_name] = new_preset
                save_presets(presets)
                sg.popup(f"プリセット '{preset_name}' を保存しました。")
                window["preset_selector"].update(values=list(presets.keys()), value=preset_name)
        elif event == "preset_selector":
            # プリセットのデータを反映
            selected_preset = values["preset_selector"]
            if selected_preset in presets:
                current_data = presets[selected_preset]
                for key in default_data.keys():
                    if key in current_data:
                        window[key].update(current_data[key])

    window.close()

# 実行
edit_json()
