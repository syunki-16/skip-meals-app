from flask import Flask, render_template_string, request, redirect, send_file
import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

members = [
    "徳本監督", "岡田コーチ",
    "内山壽頼", "大森隼人", "菊池笙", "國井優仁", "佐竹響", "長谷川琉斗", "本田伊吹", "横尾皓",
    "石井達也", "植田航生", "宇野利希", "小坂悠太", "澤田悠斗", "塩崎浩貴", "新城陽", "丹野暁翔", "永田覇人", "米原大祐",
    "上原駿希", "太田直希", "熊井康太", "小林圭吾", "酒井忠久", "高橋柊", "中川成弥", "水戸瑛太", "宮本大心",
    "赤繁咲多", "岩瀬駿介", "大沼亮太", "奥村心", "後藤秀波", "高松桜太", "竹中友規", "森尻悠翔", "渡邊義仁"
]

days = ["月", "火", "水", "木", "金", "土", "日"]
meals = ["朝", "夜"]

# 今週の月曜日の日付を取得してファイル名を決定
def get_weekly_csv_filename():
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return f"skip_meals_{monday.strftime('%Y-%m-%d')}.csv"

@app.route("/", methods=["GET", "POST"])
def index():
    csv_file = get_weekly_csv_filename()
    if request.method == "POST":
        name = request.form.get("name")
        skips = []
        for day in days:
            for meal in meals:
                key = f"{day}_{meal}"
                skips.append(request.form.get(key))
        file_exists = os.path.exists(csv_file)
        with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["名前"] + [f"{d}_{m}" for d in days for m in meals])
            writer.writerow([name] + skips)
        return redirect("/")
    return render_template_string(TEMPLATE_FORM, members=members, days=days, meals=meals)

@app.route("/list")
def skip_list():
    csv_file = get_weekly_csv_filename()
    skips_by_day = defaultdict(list)
    if os.path.exists(csv_file):
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["名前"]
                for day in days:
                    for meal in meals:
                        key = f"{day}_{meal}"
                        if row.get(key):
                            skips_by_day[f"{day} {meal}"].append(name)
    return render_template_string(TEMPLATE_LIST, skips=skips_by_day)

@app.route("/download")
def download():
    csv_file = get_weekly_csv_filename()
    return send_file(csv_file, as_attachment=True, download_name=csv_file)

TEMPLATE_FORM = """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>欠食申告フォーム</title>
<style>table { border-collapse: collapse; width: 100%; } th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }</style>
</head>
<body>
<h2>欠食申告フォーム（食べない時だけチェック）</h2>
<form method="post">
<label>名前：</label>
<select name="name" required>
<option value="">-- 選択 --</option>
{% for member in members %}<option value="{{ member }}">{{ member }}</option>{% endfor %}
</select><br><br>
<table><thead><tr><th>曜日</th>{% for meal in meals %}<th>{{ meal }}</th>{% endfor %}</tr></thead><tbody>
{% for day in days %}<tr><td>{{ day }}</td>{% for meal in meals %}<td><input type="checkbox" name="{{ day }}_{{ meal }}" value="1"></td>{% endfor %}</tr>{% endfor %}
</tbody></table><br><button type="submit">提出</button></form>
<br><a href="/list">▶ 欠食一覧を見る</a>
</body></html>
"""

TEMPLATE_LIST = """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>欠食一覧</title></head>
<body>
<h2>欠食者一覧（曜日・時間別）</h2>
{% for key, names in skips.items() %}
<h3>{{ key }}</h3>
<ul>
  {% for name in names %}<li>{{ name }}</li>{% endfor %}
</ul>
{% endfor %}
<br>
<a href="/">◀ 戻る</a> ｜ <a href="/download">CSVをダウンロード</a>
</body></html>
"""

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
