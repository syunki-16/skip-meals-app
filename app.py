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

TEMPLATE_FORM = """<!DOCTYPE html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>欠食申告</title><style>
body { background:#e9f1ec; color:#004225; font-family:sans-serif; padding:20px; }
h2 { color:#004225; } .comment { background:#fff; padding:10px; margin:10px 0; border-left:5px solid #004225; }
</style></head><body>
<h2>欠食申告フォーム</h2>
{% for a in announcements %}
<div class='comment'><strong>{{ a.author }}</strong>：{{ a.message }}（{{ a.start }}〜{{ a.end }}）</div>
{% endfor %}
<form method="post">
<label>名前：</label><select name="name" required>
<option value="">--選択--</option>{% for m in members %}<option>{{ m }}</option>{% endfor %}
</select><br>
<label>欠食したい日付：</label><input type="date" name="dates" multiple required><br>
<label>朝・夜：</label>
<label><input type="checkbox" name="meals" value="朝">朝</label>
<label><input type="checkbox" name="meals" value="夜">夜</label><br>
<button type="submit">提出</button>
</form><br>
<a href="/list">📋 欠食一覧</a> | <a href="/delete">❌ 申請削除</a> | <a href="/announce">📢 お知らせ管理</a>
</body></html>"""

TEMPLATE_LIST = """<!DOCTYPE html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>欠食一覧</title><style>
body { background:#e9f1ec; color:#004225; font-family:sans-serif; padding:20px; }
</style></head><body>
<h2>欠食者一覧（今日以降）</h2>
{% for key, people in skips.items() %}
<h3>{{ key }}</h3>
<ul>{% for p in people %}<li>{{ p }}</li>{% endfor %}</ul>
{% endfor %}
<a href="/">◀ 戻る</a></body></html>"""

TEMPLATE_DELETE = """<!DOCTYPE html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>欠食削除</title><style>
body { background:#e9f1ec; color:#004225; font-family:sans-serif; padding:20px; }
</style></head><body>
<h2>欠食申告削除</h2>
<form method="post">
<label>名前：</label><select name="name" required>
<option value="">--選択--</option>{% for m in members %}<option>{{ m }}</option>{% endfor %}
</select><br><br>
{% for row in options %}
<label><input type="checkbox" name="{{ row['日付'] }}_{{ row['区分'] }}"> {{ row['日付'] }} {{ row['区分'] }}</label><br>
{% endfor %}
<button type="submit">削除</button></form><br>
<a href="/">◀ 戻る</a>
</body></html>"""

TEMPLATE_ANNOUNCE = """<!DOCTYPE html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>お知らせ管理</title><style>
body { background:#e9f1ec; color:#004225; font-family:sans-serif; padding:20px; }
.comment { background:#fff; padding:10px; margin:10px 0; border-left:5px solid #004225; }
</style></head><body>
<h2>お知らせ管理</h2>
<form method="post">
<label>名前（誰が投稿）：</label><input name="author" required><br>
<label>内容：</label><input name="message" required><br>
<label>表示開始：</label><input type="date" name="start" required><br>
<label>表示終了：</label><input type="date" name="end" required><br>
<button type="submit">投稿</button>
</form><hr>
<h3>投稿済みのお知らせ</h3>
{% for a in announcements %}
<div class="comment">
<strong>{{ a.author }}</strong>：{{ a.message }}（{{ a.start }}〜{{ a.end }}）
<a href="/announce/delete/{{ loop.index0 }}">❌ 削除</a>
</div>
{% endfor %}
<a href="/">◀ 戻る</a></body></html>"""

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)