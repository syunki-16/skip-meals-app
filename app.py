from flask import Flask, render_template_string, request, redirect, send_file
from datetime import datetime, timedelta
import csv
import os
from collections import defaultdict

app = Flask(__name__)

# 部員リスト
members = [
    "徳本監督", "岡田コーチ",
    "内山壽頼", "大森隼人", "菊池笙", "國井優仁", "佐竹響", "長谷川琉斗", "本田伊吹", "横尾皓",
    "石井達也", "植田航生", "宇野利希", "小坂悠太", "澤田悠斗", "塩崎浩貴", "新城陽", "丹野暁翔", "永田覇人", "米原大祐",
    "上原駿希", "太田直希", "熊井康太", "小林圭吾", "酒井忠久", "高橋柊", "中川成弥", "水戸瑛太", "宮本大心",
    "赤繁咲多", "岩瀬駿介", "大沼亮太", "奥村心", "後藤秀波", "高松桜太", "竹中友規", "森尻悠翔", "渡邊義仁"
]

# 今週の日付リストを生成（日曜始まり）
def get_current_week_dates():
    today = datetime.today()
    sunday = today - timedelta(days=today.weekday() + 1 if today.weekday() < 6 else 0)
    return [(sunday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

meals = ["朝", "夜"]

# CSVファイル名（日付ごと）
def get_csv_filename(date_str):
    return f"skip_{date_str}.csv"

# コメント保存ファイル
COMMENT_FILE = "comments.csv"
NOTICE_FILE = "notices.csv"
# 欠食申請フォームと送信処理
@app.route("/", methods=["GET", "POST"])
def index():
    dates = get_current_week_dates()

    if request.method == "POST":
        name = request.form.get("name")
        for date in dates:
            for meal in meals:
                key = f"{date}_{meal}"
                if request.form.get(key):
                    filename = get_csv_filename(date)
                    file_exists = os.path.exists(filename)
                    with open(filename, "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        if not file_exists:
                            writer.writerow(["名前", "日付", "食事"])
                        writer.writerow([name, date, meal])
        return redirect("/")

    notices = load_notices()
    return render_template_string(TEMPLATE_FORM, members=members, dates=dates, meals=meals, notices=notices)

# 欠食削除ページ
@app.route("/delete", methods=["GET", "POST"])
def delete():
    dates = get_current_week_dates()
    deleted = False

    if request.method == "POST":
        name = request.form.get("name")
        for date in dates:
            for meal in meals:
                filename = get_csv_filename(date)
                if not os.path.exists(filename):
                    continue
                with open(filename, "r", encoding="utf-8") as f:
                    rows = list(csv.reader(f))
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    for row in rows:
                        if row and not (row[0] == name and row[1] == date and row[2] == meal and request.form.get(f"{date}_{meal}")):
                            writer.writerow(row)
                deleted = True

    return render_template_string(TEMPLATE_DELETE, members=members, dates=dates, meals=meals, deleted=deleted)
# 欠食一覧ページ
@app.route("/list")
def skip_list():
    dates = get_current_week_dates()
    skips_by_day = defaultdict(list)

    for date in dates:
        filename = get_csv_filename(date)
        if os.path.exists(filename):
            with open(filename, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    skips_by_day[f"{row['日付']} {row['食事']}"].append(row["名前"])

    return render_template_string(TEMPLATE_LIST, skips=skips_by_day)

# CSVダウンロード
@app.route("/download/<date>")
def download(date):
    filename = get_csv_filename(date)
    return send_file(filename, as_attachment=True)

# お知らせ読み込み
def load_notices():
    notices = []
    today = datetime.today().date()
    if os.path.exists(NOTICE_FILE):
        with open(NOTICE_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                expire = datetime.strptime(row["期限"], "%Y-%m-%d").date()
                if expire >= today:
                    notices.append(row)
    return notices

# お知らせ投稿・削除
@app.route("/notice", methods=["POST"])
def notice():
    message = request.form.get("message")
    expire = request.form.get("expire")
    if message and expire:
        file_exists = os.path.exists(NOTICE_FILE)
        with open(NOTICE_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["内容", "期限"])
            if not file_exists:
                writer.writeheader()
            writer.writerow({"内容": message, "期限": expire})
    return redirect("/")

@app.route("/notice/delete_all")
def delete_notice():
    if os.path.exists(NOTICE_FILE):
        os.remove(NOTICE_FILE)
    return redirect("/")
# 欠食申請フォーム
TEMPLATE_FORM = """
<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>欠食申告フォーム</title>
<style>
  body { font-family: sans-serif; background-color: #e9f1ec; color: #004225; padding: 20px; }
  h2 { color: #004225; }
  label, select, input[type="date"] { font-size: 1em; margin-bottom: 10px; }
  .checkbox-group { display: flex; flex-wrap: wrap; gap: 10px; }
  .checkbox-item { background: #fff; padding: 8px; border: 2px solid #004225; border-radius: 8px; }
  button { background: #004225; color: white; padding: 10px 20px; border: none; border-radius: 5px; font-size: 1em; }
  textarea { width: 100%; height: 60px; }
</style>
</head><body>

<h2>📣 お知らせ</h2>
<ul>
{% for n in notices %}
  <li>{{ n["内容"] }}（～{{ n["期限"] }}）</li>
{% endfor %}
</ul>
<form action="/notice" method="post">
  <label>コメント（全員が見られます）：</label>
  <input type="text" name="message" required>
  <label>期限：</label>
  <input type="date" name="expire" required>
  <button type="submit">追加</button>
  <a href="/notice/delete_all">🗑 全削除</a>
</form>

<hr>
<h2>欠食申告フォーム（不要な時だけチェック）</h2>
<form method="post">
<label>名前：</label>
<select name="name" required>
  <option value="">--選択--</option>
  {% for member in members %}<option value="{{ member }}">{{ member }}</option>{% endfor %}
</select>
<div class="checkbox-group">
  {% for date in dates %}
    {% for meal in meals %}
      <label class="checkbox-item">
        <input type="checkbox" name="{{ date }}_{{ meal }}" value="1"> {{ date }} {{ meal }}
      </label>
    {% endfor %}
  {% endfor %}
</div>
<button type="submit">提出</button>
</form>
<br><a href="/list">▶ 欠食一覧を見る</a>｜<a href="/delete">❌ 申請削除</a>
</body></html>
"""

# 欠食一覧ページ
TEMPLATE_LIST = """
<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>欠食一覧</title>
<style>
  body { font-family: sans-serif; background-color: #e9f1ec; color: #004225; padding: 20px; }
  h2 { color: #004225; }
  ul { list-style-type: square; }
</style>
</head><body>
<h2>欠食者一覧（日付と食事ごと）</h2>
{% for key, names in skips.items() %}
  <h3>{{ key }}</h3>
  <ul>{% for name in names %}<li>{{ name }}</li>{% endfor %}</ul>
{% endfor %}
<br><a href="/">◀ 戻る</a>
</body></html>
"""

# 欠食削除ページ
TEMPLATE_DELETE = """
<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>欠食削除</title>
<style>
  body { font-family: sans-serif; background-color: #e9f1ec; color: #004225; padding: 20px; }
  h2 { color: #004225; }
  .checkbox-group { display: flex; flex-wrap: wrap; gap: 10px; }
  .checkbox-item { padding: 6px; border: 1px solid #004225; background: #fff; border-radius: 6px; }
  button { background: #004225; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
</style>
</head><body>
<h2>❌ 欠食申請の削除</h2>
{% if deleted %}<p>削除しました。</p>{% endif %}
<form method="post">
<label>名前：</label>
<select name="name" required>
  <option value="">--選択--</option>
  {% for member in members %}<option value="{{ member }}">{{ member }}</option>{% endfor %}
</select>
<div class="checkbox-group">
  {% for date in dates %}
    {% for meal in meals %}
      <label class="checkbox-item">
        <input type="checkbox" name="{{ date }}_{{ meal }}" value="1"> {{ date }} {{ meal }}
      </label>
    {% endfor %}
  {% endfor %}
</div>
<button type="submit">削除する</button>
</form>
<br><a href="/">◀ 戻る</a>
</body></html>
"""

# アプリ起動
if __name__ == "__main__":
    app.run(debug=True, port=5000)
