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

days = ["日", "月", "火", "水", "木", "金", "土"]
meals = ["朝", "夜"]

def get_csv_filename_by_date(date_str):
    try:
        base_date = datetime.strptime(date_str, "%Y-%m-%d")
    except:
        base_date = datetime.now()
    sunday = base_date - timedelta(days=(base_date.weekday() + 1) % 7)
    return f"skip_meals_{sunday.strftime('%Y-%m-%d')}.csv"

def save_comment(text, start, end):
    with open("comments.csv", mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if os.stat("comments.csv").st_size == 0:
            writer.writerow(["コメント", "開始日", "終了日"])
        writer.writerow([text, start, end])
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        date_str = request.form.get("week_date")
        comment = request.form.get("personal_comment", "")
        csv_file = get_csv_filename_by_date(date_str)
        skips = []
        for day in days:
            for meal in meals:
                key = f"{day}_{meal}"
                skips.append(request.form.get(key))
        file_exists = os.path.exists(csv_file)
        with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["名前"] + [f"{d}_{m}" for d in days for m in meals] + ["コメント"])
            writer.writerow([name] + skips + [comment])
        return redirect("/")
    return render_template_string(TEMPLATE_FORM, members=members, days=days, meals=meals)

@app.route("/list")
def skip_list():
    today = datetime.now()
    current_week = get_csv_filename_by_date(today.strftime("%Y-%m-%d"))
    skips_by_day = defaultdict(list)
    base_date = datetime.strptime(current_week[12:22], "%Y-%m-%d")

    # 欠食記録の読み込み
    if os.path.exists(current_week):
        with open(current_week, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["名前"]
                comment = row.get("コメント", "")
                for i, day in enumerate(days):
                    for meal in meals:
                        key = f"{day}_{meal}"
                        if row.get(key):
                            date_label = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
                            display = f"{name}" + (f"（{comment}）" if comment else "")
                            skips_by_day[f"{date_label} {meal}"].append(display)

    # コメントの読み込み（現在日付に有効なものだけ）
    comments_display = []
    if os.path.exists("comments.csv"):
        with open("comments.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    start = datetime.strptime(row["開始日"], "%Y-%m-%d").date()
                    end = datetime.strptime(row["終了日"], "%Y-%m-%d").date()
                    if start <= today.date() <= end:
                        comments_display.append(f"{row['コメント']}（{start}〜{end}）")
                except:
                    pass

    return render_template_string(TEMPLATE_LIST, skips=skips_by_day, notices=comments_display)

@app.route("/comment", methods=["GET", "POST"])
def comment_page():
    if request.method == "POST":
        text = request.form.get("comment")
        start = request.form.get("start_date")
        end = request.form.get("end_date")
        save_comment(text, start, end)
        return redirect("/list")
    return render_template_string(TEMPLATE_COMMENT)
TEMPLATE_FORM = """
<!doctype html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>欠食申告フォーム</title>
<style>
  body { background-color: #e9f1ec; font-family: sans-serif; color: #004225; padding: 20px; }
  h2 { color: #004225; }
  label, select, input, textarea { font-size: 1em; margin-bottom: 10px; display: block; width: 100%; }
  .checkbox-group { display: flex; flex-wrap: wrap; gap: 10px; }
  .checkbox-item { padding: 10px; background: #fff; border: 2px solid #004225; border-radius: 6px; min-width: 120px; }
  button { background: #004225; color: white; padding: 10px 20px; font-size: 1.1em; border: none; border-radius: 6px; margin-top: 10px; }
  a { color: #004225; font-weight: bold; display: block; margin-top: 20px; }
</style></head>
<body>
<h2>欠食申告フォーム</h2>
<form method="post">
<label>名前</label>
<select name="name" required>
<option value="">-- 選択 --</option>
{% for member in members %}<option value="{{ member }}">{{ member }}</option>{% endfor %}
</select>

<label>申告する週の日曜日の日付</label>
<input type="date" name="week_date" required>

<label>チェック（不要なときだけ）</label>
<div class="checkbox-group">
{% for day in days %}
  {% for meal in meals %}
    <label class="checkbox-item"><input type="checkbox" name="{{ day }}_{{ meal }}" value="1"> {{ day }} {{ meal }}</label>
  {% endfor %}
{% endfor %}
</div>

<label>コメント（任意）</label>
<textarea name="personal_comment" rows="2"></textarea>

<button type="submit">提出</button>
</form>

<a href="/list">▶ 欠食一覧を見る</a>
<a href="/comment">▶ お知らせコメントを書く</a>
</body></html>
"""

TEMPLATE_LIST = """
<!doctype html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>欠食一覧</title>
<style>
  body { background-color: #e9f1ec; font-family: sans-serif; color: #004225; padding: 20px; }
  h2, h3 { color: #004225; }
  ul { list-style-type: square; margin-left: 20px; }
  .notice { background: #d2e6dc; padding: 10px; border-left: 6px solid #004225; margin-bottom: 20px; }
  a { color: #004225; font-weight: bold; }
</style></head>
<body>
<h2>欠食一覧</h2>

{% if notices %}
<div class="notice">
<b>📢 お知らせ：</b><br>
{% for n in notices %}
・{{ n }}<br>
{% endfor %}
</div>
{% endif %}

{% for key, names in skips.items() %}
<h3>{{ key }}</h3>
<ul>
  {% for name in names %}<li>{{ name }}</li>{% endfor %}
</ul>
{% endfor %}

<a href="/">◀ 戻る</a>
</body></html>
"""

TEMPLATE_COMMENT = """
<!doctype html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>お知らせ投稿</title>
<style>
  body { background-color: #e9f1ec; font-family: sans-serif; color: #004225; padding: 20px; }
  h2 { color: #004225; }
  label, input, textarea { font-size: 1em; margin-bottom: 10px; display: block; width: 100%; }
  button { background: #004225; color: white; padding: 10px 20px; font-size: 1.1em; border: none; border-radius: 6px; margin-top: 10px; }
  a { color: #004225; font-weight: bold; display: block; margin-top: 20px; }
</style></head>
<body>
<h2>📢 お知らせを追加</h2>
<form method="post">
<label>コメント内容</label>
<textarea name="comment" required rows="2"></textarea>

<label>開始日</label>
<input type="date" name="start_date" required>

<label>終了日</label>
<input type="date" name="end_date" required>

<button type="submit">追加</button>
</form>

<a href="/list">◀ 一覧に戻る</a>
</body></html>
"""
