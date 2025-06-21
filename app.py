from flask import Flask, render_template, request, redirect, send_file
import os
import csv
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

# 部員リスト（名前欄）
members = [
    "徳本監督", "岡田コーチ",
    "内山壽頼", "大森隼人", "菊池笙", "國井優仁", "佐竹響", "長谷川琉斗", "本田伊吹", "横尾皓",
    "石井達也", "植田航生", "宇野利希", "小坂悠太", "澤田悠斗", "塩崎浩貴", "新城陽", "丹野暁翔", "永田覇人", "米原大祐",
    "上原駿希", "太田直希", "熊井康太", "小林圭吾", "酒井忠久", "高橋柊", "中川成弥", "水戸瑛太", "宮本大心",
    "赤繁咲多", "岩瀬駿介", "大沼亮太", "奥村心", "後藤秀波", "高松桜太", "竹中友規", "森尻悠翔", "渡邊義仁"
]

meals = ["朝", "夜"]
DATA_FOLDER = "data"
COMMENTS_FILE = os.path.join(DATA_FOLDER, "comments.csv")
os.makedirs(DATA_FOLDER, exist_ok=True)
@app.route("/delete", methods=["GET", "POST"])
def delete_entry():
    if request.method == "POST":
        name = request.form["name"]
        keep_rows = []
        removed = set()
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline="", encoding="utf-8") as f:
                reader = list(csv.reader(f))
                header = reader[0]
                for row in reader[1:]:
                    if row[0] == name and f"{row[1]}_{row[2]}" not in request.form:
                        keep_rows.append(row)
                    else:
                        removed.add((row[1], row[2]))
            with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(keep_rows)
        return redirect("/")
    today = datetime.today().isoformat()
    options = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["日付"] >= today:
                    options.append(row)
    return render_template_string(TEMPLATE_DELETE, members=MEMBERS, options=options)

@app.route("/announce", methods=["GET", "POST"])
def announce():
    announcements = load_announcements()
    if request.method == "POST":
        author = request.form["author"]
        message = request.form["message"]
        start = request.form["start"]
        end = request.form["end"]
        announcements.append({"author": author, "message": message, "start": start, "end": end})
        save_announcements(announcements)
        return redirect("/")
    return render_template_string(TEMPLATE_ANNOUNCE, announcements=announcements)

@app.route("/announce/delete/<int:index>")
def delete_announce(index):
    announcements = load_announcements()
    if 0 <= index < len(announcements):
        del announcements[index]
        save_announcements(announcements)
    return redirect("/announce")

def load_announcements():
    if not os.path.exists(ANNOUNCE_FILE): return []
    with open(ANNOUNCE_FILE, encoding="utf-8") as f:
        return json.load(f)

def save_announcements(data):
    with open(ANNOUNCE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
TEMPLATE_FORM = """
<!doctype html>
<html><head><meta charset="utf-8"><title>芝浦工業大学駅伝部 欠食フォーム</title>
<style>
body { background: repeating-linear-gradient(45deg, #e9f1ec, #e9f1ec 20px, white 20px, white 40px); font-family: 'Yu Mincho', serif; color: #004225; padding: 20px; }
h1 { font-size: 2em; font-weight: bold; }
form { background: white; padding: 20px; border-radius: 10px; }
textarea, input, select { font-size: 1em; margin: 5px 0; width: 100%; }
button { background: #004225; color: white; padding: 10px; font-size: 1.1em; border: none; border-radius: 5px; margin-top: 10px; }
a { color: #004225; font-weight: bold; }
</style></head>
<body>
<h1>芝浦工業大学駅伝部 欠食申請フォーム</h1>

{% if announcements %}
<div style="border:2px solid #004225;padding:10px;margin-bottom:20px;background:#f5fff5;">
  <h2>📢 お知らせ</h2>
  {% for ann in announcements %}
    {% if ann.start <= now <= ann.end %}
    <p><strong>{{ ann.author }}</strong>：{{ ann.message }}（{{ ann.start }}〜{{ ann.end }}）
    <a href="/announce/delete/{{ loop.index0 }}">❌削除</a></p>
    {% endif %}
  {% endfor %}
</div>
{% endif %}

<form method="post">
  <label>名前：</label>
  <select name="name" required>
    <option value="">-- 選択 --</option>
    {% for m in members %}<option value="{{ m }}">{{ m }}</option>{% endfor %}
  </select>
  <label>欠食したい日付：</label>
  <input type="date" name="date" required>
  <label>朝食：</label><input type="checkbox" name="breakfast" value="1">
  <label>夕食：</label><input type="checkbox" name="dinner" value="1"><br>
  <button type="submit">提出</button>
</form>
<br><a href="/list">▶ 欠食者一覧</a>｜<a href="/weeks">📅 CSVダウンロード</a>｜<a href="/delete">🗑️ 申請削除</a>｜<a href="/announce">📢 お知らせ投稿</a>
</body></html>
"""

TEMPLATE_LIST = """
<!doctype html>
<html><head><meta charset="utf-8"><title>欠食一覧</title></head>
<body style="background:#e9f1ec;font-family:'Yu Mincho';color:#004225;padding:20px;">
<h2>📋 現在の欠食者一覧</h2>
{% for key, names in skips.items() %}
<h3>{{ key }}</h3>
<ul>
  {% for name in names %}<li>{{ name }}</li>{% endfor %}
</ul>
{% endfor %}
<a href="/">◀ 戻る</a>
</body></html>
"""

TEMPLATE_DELETE = """
<!doctype html>
<html><head><meta charset="utf-8"><title>欠食削除</title></head>
<body style="background:#e9f1ec;font-family:'Yu Mincho';color:#004225;padding:20px;">
<h2>🗑️ 欠食申請を削除</h2>
<form method="post">
<label>名前：</label>
<select name="name">
  {% for m in members %}<option value="{{ m }}">{{ m }}</option>{% endfor %}
</select>
<p>削除したい申請（該当するものに✔）：</p>
{% for row in options %}
  <label><input type="checkbox" name="{{ row['日付'] }}_{{ row['食事'] }}"> {{ row['日付'] }} {{ row['食事'] }}</label><br>
{% endfor %}
<button type="submit">削除</button>
</form>
<a href="/">◀ 戻る</a>
</body></html>
"""

TEMPLATE_ANNOUNCE = """
<!doctype html>
<html><head><meta charset="utf-8"><title>お知らせ</title></head>
<body style="background:#e9f1ec;font-family:'Yu Mincho';color:#004225;padding:20px;">
<h2>📢 お知らせ投稿</h2>
<form method="post">
<label>名前：</label><input name="author" required><br>
<label>お知らせ：</label><textarea name="message" required></textarea><br>
<label>開始日：</label><input type="date" name="start" required><br>
<label>終了日：</label><input type="date" name="end" required><br>
<button type="submit">投稿</button>
</form>
<h3>現在のお知らせ</h3>
{% for a in announcements %}
  <p><strong>{{ a.author }}</strong>：{{ a.message }}（{{ a.start }}〜{{ a.end }}）<a href="/announce/delete/{{ loop.index0 }}">❌削除</a></p>
{% endfor %}
<a href="/">◀ 戻る</a>
</body></html>
"""

# 最後にアプリを起動
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
