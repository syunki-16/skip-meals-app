
from flask import Flask, render_template_string, request, redirect, send_file
import csv
import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

members = [
    "徳本監督", "岡田コーチ", "内山壽頼", "大森隼人", "菊池笙", "國井優仁", "佐竹響", "長谷川琉斗", "本田伊吹", "横尾皓",
    "石井達也", "植田航生", "宇野利希", "小坂悠太", "澤田悠斗", "塩崎浩貴", "新城陽", "丹野暁翔", "永田覇人", "米原大祐",
    "上原駿希", "太田直希", "熊井康太", "小林圭吾", "酒井忠久", "高橋柊", "中川成弥", "水戸瑛太", "宮本大心",
    "赤繁咲多", "岩瀬駿介", "大沼亮太", "奥村心", "後藤秀波", "高松桜太", "竹中友規", "森尻悠翔", "渡邊義仁"
]

def get_csv_filename(date_str):
    return f"skip_{date_str}.csv"

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("date")
        meal = request.form.get("meal")
        if name and date and meal:
            filename = get_csv_filename(date)
            file_exists = os.path.exists(filename)
            with open(filename, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["名前", "日付", "食事"])
                writer.writerow([name, date, meal])
            message = "登録しました。"
    return render_template_string(FORM_TEMPLATE, members=members, message=message)

@app.route("/list")
def skip_list():
    all_skips = defaultdict(list)
    for file in os.listdir():
        if file.startswith("skip_") and file.endswith(".csv"):
            with open(file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    all_skips[f"{row['日付']} {row['食事']}"].append(row["名前"])
    return render_template_string(LIST_TEMPLATE, skips=all_skips)

FORM_TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset='utf-8'><title>芝浦工業大学駅伝部 欠食申請フォーム</title>
<style>
body { background-color: #e8f5e9; font-family: 'serif'; padding: 20px; color: #004225; }
h1 { font-size: 1.8em; border-bottom: 3px double #004225; display: inline-block; }
form { background: #fff; padding: 15px; border-radius: 10px; }
label { display: block; margin: 10px 0 5px; }
button { margin-top: 10px; background-color: #004225; color: white; padding: 10px; border: none; border-radius: 5px; }
</style></head>
<body>
<h1>芝浦工業大学駅伝部<br>欠食申請フォーム</h1>
<p>{{ message }}</p>
<form method="post">
<label>名前：</label>
<select name="name" required>
  <option value="">-- 選択 --</option>
  {% for m in members %}<option value="{{m}}">{{m}}</option>{% endfor %}
</select>
<label>欠食日：</label><input type="date" name="date" required>
<label>朝・夜：</label>
<select name="meal" required>
  <option value="朝">朝</option>
  <option value="夜">夜</option>
</select>
<br><button type="submit">申請する</button>
</form>
<br><a href="/list">▶ 欠食一覧を見る</a>
</body></html>"""

LIST_TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset='utf-8'><title>欠食一覧</title>
<style>
body { background-color: #e8f5e9; font-family: 'serif'; padding: 20px; color: #004225; }
h1 { font-size: 1.6em; border-bottom: 2px solid #004225; }
h2 { font-size: 1.2em; margin-top: 1em; }
ul { margin-left: 20px; }
</style></head>
<body>
<h1>欠食一覧</h1>
{% for key, names in skips.items() %}
  <h2>{{ key }}</h2>
  <ul>
  {% for name in names %}
    <li>{{ name }}</li>
  {% endfor %}
  </ul>
{% endfor %}
<a href="/">◀ フォームに戻る</a>
</body></html>"""
