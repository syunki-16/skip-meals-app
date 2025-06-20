from flask import Flask, render_template_string, request, redirect, send_file
import csv, os
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

def get_csv_filename_by_date(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
    except:
        d = datetime.now()
    monday = d - timedelta(days=d.weekday())
    return f"skip_meals_{monday.strftime('%Y-%m-%d')}.csv"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        date_str = request.form.get("week_date")
        csv_file = get_csv_filename_by_date(date_str)
        skips = []
        for day in days:
            for meal in meals:
                skips.append(request.form.get(f"{day}_{meal}"))
        file_exists = os.path.exists(csv_file)
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["名前"] + [f"{d}_{m}" for d in days for m in meals])
            writer.writerow([name] + skips)
        return redirect("/")
    return render_template_string(TEMPLATE_FORM, members=members, days=days, meals=meals)

@app.route("/list")
def skip_list():
    today = datetime.now()
    csv_file = get_csv_filename_by_date(today.strftime("%Y-%m-%d"))
    skips_by_day = defaultdict(list)
    base_date = datetime.strptime(csv_file[12:22], "%Y-%m-%d")
    if os.path.exists(csv_file):
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["名前"]
                for i, day in enumerate(days):
                    for meal in meals:
                        key = f"{day}_{meal}"
                        if row.get(key):
                            actual_date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
                            skips_by_day[f"{actual_date} {meal}"].append(name)
    return render_template_string(TEMPLATE_LIST, skips=skips_by_day)

@app.route("/weeks")
def list_weeks():
    files = sorted([f for f in os.listdir(".") if f.startswith("skip_meals_") and f.endswith(".csv")], reverse=True)
    return render_template_string(TEMPLATE_WEEKS, files=files)

@app.route("/download/<filename>")
def download_named(filename):
    return send_file(filename, as_attachment=True, download_name=filename)

# HTML テンプレート
TEMPLATE_FORM = """<!doctype html><html><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>欠食申告フォーム</title>
<style>
  body { font-family: sans-serif; background: #e9f1ec; color: #004225; padding: 20px; }
  h2 { color: #004225; }
  label, select, input[type="date"] { font-size: 1.1em; display: block; margin-bottom: 10px; }
  .checkbox-group { display: flex; flex-wrap: wrap; gap: 10px; }
  .checkbox-item { background: #fff; padding: 10px; border: 2px solid #004225; border-radius: 8px; flex: 1 1 45%; min-width: 130px; }
  button { font-size: 1.2em; padding: 10px 20px; margin-top: 20px; background: #004225; color: white; border: none; border-radius: 6px; }
  a { color: #004225; font-weight: bold; }
</style>
</head><body>
<h2>欠食申告フォーム（食べない時だけチェック）</h2>
<form method='post'>
<label>名前：</label>
<select name='name' required>
<option value=''>-- 選択 --</option>
{% for member in members %}<option value='{{ member }}'>{{ member }}</option>{% endfor %}
</select>
<label>申告する週の月曜日の日付：</label>
<input type='date' name='week_date' required>
<div class='checkbox-group'>
{% for day in days %}{% for meal in meals %}
<label class='checkbox-item'><input type='checkbox' name='{{ day }}_{{ meal }}' value='1'>{{ day }} {{ meal }}</label>
{% endfor %}{% endfor %}
</div>
<button type='submit'>提出</button>
</form><br><a href='/list'>▶ 欠食一覧を見る</a> ｜ <a href='/weeks'>週別CSV一覧</a>
</body></html>"""

TEMPLATE_LIST = """<!doctype html><html><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>欠食一覧</title>
<style>
  body { font-family: sans-serif; background-color: #e9f1ec; padding: 20px; color: #004225; }
  h2 { color: #004225; }
  ul { list-style-type: square; }
  a { color: #004225; font-weight: bold; }
</style>
</head><body>
<h2>欠食者一覧（日付と時間別）</h2>
{% for key, names in skips.items() %}
<h3>{{ key }}</h3><ul>{% for name in names %}<li>{{ name }}</li>{% endfor %}</ul>
{% endfor %}
<br><a href='/'>◀ 戻る</a>
</body></html>"""

TEMPLATE_WEEKS = """<!doctype html><html><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>週別CSV一覧</title>
<style>
  body { font-family: sans-serif; background-color: #e9f1ec; padding: 20px; color: #004225; }
  h2 { color: #004225; }
  ul { list-style-type: circle; }
  a { color: #004225; font-weight: bold; }
</style>
</head><body>
<h2>📅 週ごとの欠食記録</h2><ul>
{% for file in files %}
  <li>{{ file }} — <a href="/download/{{ file }}">📥 ダウンロード</a></li>
{% endfor %}
</ul><br><a href="/">◀ 戻る</a>
</body></html>"""

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
