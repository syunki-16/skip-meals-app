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

meals = ["朝", "夜"]
DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)
COMMENTS_FILE = os.path.join(DATA_FOLDER, "comments.csv")

def get_csv_filename_by_date(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
    except:
        d = datetime.now()
    return os.path.join(DATA_FOLDER, f"skip_{d.strftime('%Y-%m-%d')}.csv")

def save_skip(name, date, meals_checked):
    filename = get_csv_filename_by_date(date)
    file_exists = os.path.exists(filename)
    with open(filename, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["名前", "日付", "朝", "夜"])
        writer.writerow([name, date] + meals_checked)

def load_skips():
    skips = defaultdict(lambda: {"朝": [], "夜": []})
    now = datetime.now().date()
    for fname in os.listdir(DATA_FOLDER):
        if fname.startswith("skip_") and fname.endswith(".csv"):
            with open(os.path.join(DATA_FOLDER, fname), newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    date = row["日付"]
                    try:
                        d_obj = datetime.strptime(date, "%Y-%m-%d").date()
                        if d_obj >= now:
                            for meal in meals:
                                if row[meal] == "1":
                                    skips[date][meal].append(row["名前"])
                    except:
                        pass
    return skips
def delete_skip(name, date):
    filename = get_csv_filename_by_date(date)
    if not os.path.exists(filename):
        return
    rows = []
    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["名前"] != name:
                rows.append(row)
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["名前", "日付", "朝", "夜"])
        writer.writeheader()
        writer.writerows(rows)

def save_comment(author, content, start_date, end_date):
    file_exists = os.path.exists(COMMENTS_FILE)
    with open(COMMENTS_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["投稿者", "コメント", "開始日", "終了日"])
        writer.writerow([author, content, start_date, end_date])

def load_active_comments():
    comments = []
    today = datetime.now().date()
    if os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    start = datetime.strptime(row["開始日"], "%Y-%m-%d").date()
                    end = datetime.strptime(row["終了日"], "%Y-%m-%d").date()
                    if start <= today <= end:
                        comments.append(row)
                except:
                    pass
    return comments

def delete_comment(index):
    if not os.path.exists(COMMENTS_FILE):
        return
    rows = []
    with open(COMMENTS_FILE, newline="", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        header = reader[0]
        rows = reader[1:]
    if 0 <= index < len(rows):
        del rows[index]
    with open(COMMENTS_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
@app.route("/delete_skip", methods=["GET", "POST"])
def delete_skip_page():
    skips = defaultdict(lambda: {"朝": False, "夜": False})
    if request.method == "POST":
        name = request.form.get("name")
        delete_date = request.form.get("delete_date")
        meal_morning = request.form.get("morning")
        meal_evening = request.form.get("evening")
        if name and delete_date:
            # 対象のCSVを読み込んで編集
            filename = get_csv_filename_by_date(delete_date)
            new_rows = []
            if os.path.exists(filename):
                with open(filename, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row["名前"] == name and row["日付"] == delete_date:
                            if meal_morning:
                                row["朝"] = ""
                            if meal_evening:
                                row["夜"] = ""
                        new_rows.append(row)
                with open(filename, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["名前", "日付", "朝", "夜"])
                    writer.writeheader()
                    writer.writerows(new_rows)
        return redirect("/delete_skip")

    # 名前を選んだとき、現在の欠食状況を表示
    name = request.args.get("name")
    if name:
        for file in os.listdir("."):
            if file.startswith("skip_meals_") and file.endswith(".csv"):
                with open(file, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row["名前"] == name:
                            skips[row["日付"]]["朝"] |= (row["朝"] == "1")
                            skips[row["日付"]]["夜"] |= (row["夜"] == "1")
    return render_template_string(TEMPLATE_DELETE, members=members, skips=skips)

@app.route("/comments", methods=["GET", "POST"])
def comments():
    if request.method == "POST":
        content = request.form.get("comment")
        author = request.form.get("author")
        start = request.form.get("start_date")
        end = request.form.get("end_date")
        save_comment(author, content, start, end)
        return redirect("/comments")
    comments = load_active_comments()
    return render_template_string(TEMPLATE_COMMENTS, comments=comments)

@app.route("/delete_comment/<int:index>")
def delete_comment_by_index(index):
    delete_comment(index)
    return redirect("/comments")
TEMPLATE_FORM = """
<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>芝浦工業大学駅伝部｜欠食申請フォーム</title>
<style>
  body { background-color: #e9f1ec; color: #003b1f; font-family: 'Noto Serif JP', serif; margin: 0; padding: 20px; }
  h1 { font-size: 1.8em; border-bottom: 2px solid #004225; padding-bottom: 5px; }
  h2 { margin-top: 30px; color: #004225; }
  label { display: block; margin-top: 10px; }
  select, input[type='date'], textarea { padding: 6px; font-size: 1em; width: 100%; max-width: 400px; margin-top: 5px; }
  .checkbox { margin-top: 15px; }
  .checkbox label { display: block; margin-bottom: 8px; }
  button { margin-top: 20px; background: #004225; color: white; font-size: 1em; padding: 10px 20px; border: none; border-radius: 5px; }
  .announcement { background: #dff0d8; padding: 10px; border-left: 6px solid #4cae4c; margin-bottom: 20px; }
</style>
</head>
<body>
<h1>🏃‍♂️ 芝浦工業大学駅伝部</h1>
<h2>📋 欠食申請フォーム</h2>

{% for c in comments %}
  <div class="announcement">
    <strong>{{ c.author }}</strong>（{{ c.start }}〜{{ c.end }}）<br>{{ c.content }}
    <div><a href="/delete_comment/{{ loop.index0 }}">❌削除</a></div>
  </div>
{% endfor %}

<form method="post">
  <label>名前：</label>
  <select name="name" required>
    <option value="">-- 選択してください --</option>
    {% for m in members %}
      <option value="{{ m }}">{{ m }}</option>
    {% endfor %}
  </select>

  <label>日付を選択：</label>
  <input type="date" name="date" required>

  <div class="checkbox">
    <label><input type="checkbox" name="morning" value="1"> 朝食 欠食</label>
    <label><input type="checkbox" name="evening" value="1"> 夕食 欠食</label>
  </div>

  <button type="submit">申請する</button>
</form>

<br><a href="/list">📅 欠食一覧を見る</a> ｜ <a href="/weeks">📁 CSV一覧</a> ｜ <a href="/delete_skip">🗑 欠食申請の削除</a> ｜ <a href="/comments">📝 お知らせ管理</a>
</body></html>
"""
TEMPLATE_LIST = """
<!doctype html>
<html>
<head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>欠食者一覧</title>
<style>
  body { font-family: sans-serif; background-color: #f5f9f5; color: #004225; padding: 20px; }
  h2 { color: #004225; border-bottom: 2px solid #004225; }
  h3 { margin-top: 20px; }
  ul { list-style-type: square; }
  a { color: #004225; font-weight: bold; }
</style>
</head>
<body>
<h2>📋 欠食者一覧（日付と時間別）</h2>
{% for key, names in skips.items() %}
  <h3>{{ key }}</h3>
  <ul>{% for name in names %}<li>{{ name }}</li>{% endfor %}</ul>
{% endfor %}
<br><a href='/'>◀ 戻る</a> ｜ <a href='/download'>📥 CSVダウンロード</a>
</body></html>
"""

TEMPLATE_DELETE = """
<!doctype html>
<html>
<head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>欠食申請削除</title>
<style>
  body { font-family: sans-serif; background-color: #f5f9f5; color: #004225; padding: 20px; }
  h2 { color: #004225; }
  label, select, input[type="date"] { font-size: 1.1em; margin-bottom: 10px; display: block; }
  .checkbox-group { display: flex; flex-wrap: wrap; gap: 10px; }
  .checkbox-item { border: 1px solid #004225; padding: 10px; border-radius: 5px; background-color: white; }
  button { font-size: 1em; padding: 8px 16px; background-color: #004225; color: white; border: none; border-radius: 4px; margin-top: 10px; }
  a { color: #004225; font-weight: bold; }
</style>
</head>
<body>
<h2>🗑 欠食申請を削除</h2>
<form method="post">
<label>名前：</label>
<select name="name" required>
  <option value="">-- 選択 --</option>
  {% for member in members %}<option value="{{ member }}">{{ member }}</option>{% endfor %}
</select>
<label>削除したい日付：</label>
<input type="date" name="date" required>
<div class="checkbox-group">
  {% for meal in meals %}
    <label class="checkbox-item">
      <input type="checkbox" name="delete_{{ meal }}" value="1"> {{ meal }}
    </label>
  {% endfor %}
</div>
<button type="submit">削除する</button>
</form>
<br><a href="/">◀ 戻る</a>
</body></html>
"""

TEMPLATE_COMMENTS = """
<!doctype html>
<html>
<head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>お知らせ管理</title>
<style>
  body { font-family: sans-serif; background-color: #f5f9f5; color: #004225; padding: 20px; }
  h2 { color: #004225; }
  input, textarea, select, button { font-size: 1em; margin-bottom: 10px; width: 100%; max-width: 500px; }
  textarea { height: 80px; }
  button { background-color: #004225; color: white; border: none; border-radius: 4px; padding: 10px; }
  .notice { border: 1px solid #ccc; background: #fff; padding: 10px; margin-bottom: 10px; border-left: 4px solid #004225; }
  a { color: #004225; font-weight: bold; }
</style>
</head>
<body>
<h2>📢 お知らせ投稿・管理</h2>
<form method="post">
  <label>名前（投稿者）：</label>
  <select name="name" required>
    <option value="">-- 選択 --</option>
    {% for member in members %}<option value="{{ member }}">{{ member }}</option>{% endfor %}
  </select>
  <label>お知らせ内容：</label>
  <textarea name="content" required></textarea>
  <label>表示期間（開始日）：</label>
  <input type="date" name="start_date" required>
  <label>表示期間（終了日）：</label>
  <input type="date" name="end_date" required>
  <button type="submit">送信</button>
</form>

<h3>📋 現在のお知らせ</h3>
{% for comment in comments %}
  <div class="notice">
    <strong>{{ comment.start }} ～ {{ comment.end }} by {{ comment.name }}</strong><br>
    {{ comment.content }}
    <form method="post" style="margin-top:5px;">
      <input type="hidden" name="delete" value="{{ loop.index0 }}">
      <button type="submit">このお知らせを削除</button>
    </form>
  </div>
{% endfor %}
<br><a href="/">◀ 戻る</a>
</body></html>
"""

TEMPLATE_WEEKS = """
<!doctype html>
<html>
<head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>週別CSV一覧</title>
<style>
  body { font-family: sans-serif; background-color: #f5f9f5; color: #004225; padding: 20px; }
  h2 { color: #004225; }
  ul { list-style-type: circle; }
  a { color: #004225; font-weight: bold; }
</style>
</head>
<body>
<h2>📁 過去の欠食記録CSV</h2>
<ul>
{% for file in files %}
  <li>{{ file }} — <a href="/download/{{ file }}">📥 ダウンロード</a></li>
{% endfor %}
</ul>
<br><a href="/">◀ 戻る</a>
</body></html>
"""

