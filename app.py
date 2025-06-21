from flask import Flask, render_template_string, request, redirect, send_file
import csv, os, json
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

MEMBERS = [  # 部員名簿
    "徳本監督", "岡田コーチ", "内山壽頼", "大森隼人", "菊池笙", "國井優仁", "佐竹響", "長谷川琉斗", "本田伊吹", "横尾皓",
    "石井達也", "植田航生", "宇野利希", "小坂悠太", "澤田悠斗", "塩崎浩貴", "新城陽", "丹野暁翔", "永田覇人", "米原大祐",
    "上原駿希", "太田直希", "熊井康太", "小林圭吾", "酒井忠久", "高橋柊", "中川成弥", "水戸瑛太", "宮本大心",
    "赤繁咲多", "岩瀬駿介", "大沼亮太", "奥村心", "後藤秀波", "高松桜太", "竹中友規", "森尻悠翔", "渡邊義仁"
]

CSV_FILE = "skip_meals_daily.csv"
ANNOUNCE_FILE = "announcements.json"

@app.route("/", methods=["GET", "POST"])
def index():
    today = datetime.today().date()
    announcements = load_announcements()
    valid_announcements = [
        a for a in announcements if a["start"] <= today.isoformat() <= a["end"]
    ]

    if request.method == "POST":
        name = request.form["name"]
        dates = request.form.getlist("dates")
        meals = request.form.getlist("meals")
        rows = []
        for d in dates:
            for m in meals:
                rows.append([name, d, m])
        file_exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["名前", "日付", "区分"])
            writer.writerows(rows)
        return redirect("/")

    return render_template_string(TEMPLATE_FORM, members=MEMBERS, announcements=valid_announcements)

@app.route("/list")
def show_skips():
    today = datetime.today().isoformat()
    skips = defaultdict(list)
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["日付"] >= today:
                    key = f"{row['日付']} {row['区分']}"
                    skips[key].append(row["名前"])
    return render_template_string(TEMPLATE_LIST, skips=skips)
@app.route("/delete", methods=["GET", "POST"])
def delete_skip():
    csv_files = [f for f in os.listdir(".") if f.startswith("skip_meals_") and f.endswith(".csv")]
    csv_files.sort(reverse=True)
    current_data = []

    if request.method == "POST":
        target_name = request.form.get("name")
        selected = request.form.getlist("delete")
        for filename in csv_files:
            filepath = os.path.join(".", filename)
            if not os.path.exists(filepath):
                continue
            new_rows = []
            with open(filepath, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["名前"] != target_name:
                        new_rows.append(row)
                        continue
                    new_row = row.copy()
                    for key in selected:
                        if key in new_row:
                            new_row[key] = ""
                    new_rows.append(new_row)
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["名前"] + [f"{date}_{meal}" for date in sorted_dates for meal in meals])
                writer.writeheader()
                for row in new_rows:
                    writer.writerow(row)
        return redirect("/delete")

    # GET: show current skip status
    for filename in csv_files:
        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["名前"]
                for key, val in row.items():
                    if key != "名前" and val:
                        current_data.append((name, key))
    return render_template_string(TEMPLATE_DELETE, data=current_data, members=members)
TEMPLATE_FORM = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>芝浦工業大学駅伝部 | 欠食申請フォーム</title>
  <style>
    body { font-family: 'serif'; background-color: #e9f1ec; padding: 20px; color: #004225; }
    h1 { font-size: 2em; border-bottom: 3px solid #004225; padding-bottom: 10px; font-family: 'serif'; }
    h2 { color: #004225; margin-top: 40px; }
    label, select, input[type="date"] { font-size: 1.1em; margin-bottom: 10px; display: block; }
    .checkbox-group { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
    .checkbox-item { background: #fff; padding: 8px; border: 2px solid #004225; border-radius: 6px; }
    button { font-size: 1em; padding: 10px 20px; background: #004225; color: white; border: none; border-radius: 5px; }
    .announcement { background: #f5f5f5; padding: 10px; border-left: 5px solid #004225; margin-bottom: 20px; }
    .title-banner { background: repeating-linear-gradient(45deg, #004225, #004225 20px, #ffffff 20px, #ffffff 40px); padding: 10px; text-align: center; }
    .title-banner h1 { color: white; margin: 0; font-weight: bold; font-size: 1.8em; font-family: 'serif'; }
  </style>
</head>
<body>
<div class="title-banner">
  <h1>芝浦工業大学駅伝部</h1>
</div>
<h2>欠食申請フォーム</h2>

{% for a in announcements %}
  <div class="announcement">
    <strong>{{ a["writer"] }}</strong>：{{ a["text"] }}（{{ a["start"] }}〜{{ a["end"] }}）
    <form method="post" action="/delete_announcement" style="display:inline;">
      <input type="hidden" name="id" value="{{ a['id'] }}">
      <button type="submit">削除</button>
    </form>
  </div>
{% endfor %}

<form method="post">
  <label>名前：</label>
  <select name="name" required>
    <option value="">-- 選択 --</option>
    {% for member in members %}
      <option value="{{ member }}">{{ member }}</option>
    {% endfor %}
  </select>

  <label>欠食する日付を選択：</label>
  {% for i in range(14) %}
    {% set d = (now + timedelta(days=i)).strftime("%Y-%m-%d") %}
    <fieldset style="margin-bottom:10px;">
      <legend>{{ d }}</legend>
      {% for meal in meals %}
        <label class="checkbox-item">
          <input type="checkbox" name="{{ d }}_{{ meal }}" value="1"> {{ meal }}
        </label>
      {% endfor %}
    </fieldset>
  {% endfor %}
  <button type="submit">提出</button>
</form>

<br>
<a href="/list">▶ 欠食一覧を見る</a> ｜ <a href="/comment">▶ お知らせ投稿</a> ｜ <a href="/delete">▶ 申請の削除</a> ｜ <a href="/weeks">▶ 過去CSV</a>
</body>
</html>
"""
