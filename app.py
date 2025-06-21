from flask import Flask, render_template_string, request, redirect, send_file
import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

@app.route("/")
def home():
    return redirect("/form")

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
    with open(filename, mode="a+", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["名前", "日付"] + meals)
        writer.writerow([name, date] + meals_checked)

def load_skips():
    skips = defaultdict(lambda: {"朝": [], "夜": []})
    now = datetime.now().date()
    for fname in os.listdir(DATA_FOLDER):
        if fname.startswith("skip_") and fname.endswith(".csv"):
            date_str = fname[5:-4]
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                if date_obj < now:
                    continue
                with open(os.path.join(DATA_FOLDER, fname), encoding="utf-8") as f:
                    reader = csv.reader(f)
                    next(reader, None)
                    for row in reader:
                        name, _, *meals_checked = row
                        for m, val in zip(meals, meals_checked):
                            if val == "1":
                                skips[date_str][m].append(name)
            except:
                continue
    return skips
@app.route("/")
def index():
    skips = load_skips()
    today = datetime.now().date()
    filtered_skips = {
        date: data for date, data in skips.items()
        if datetime.strptime(date, "%Y-%m-%d").date() >= today
    }

    comments = load_comments()
    comments.sort(key=lambda x: x["start"], reverse=True)

    return render_template_string(TEMPLATE_FORM,
        members=members,
        skips=filtered_skips,
        meals=meals,
        today=today.strftime("%Y-%m-%d"),
        comments=comments
    )

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    date = request.form["date"]
    selected_meals = [meal for meal in meals if meal in request.form]
    if selected_meals:
        save_skip(name, date, selected_meals)
    return redirect("/")

@app.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        name = request.form["name"]
        date = request.form["date"]
        filename = get_csv_filename_by_date(date)
        if os.path.exists(filename):
            with open(filename, newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for row in rows:
                    if row and row[0] != name:
                        writer.writerow(row)
        return redirect("/")
    else:
        return render_template_string(TEMPLATE_DELETE, members=members)
TEMPLATE_FORM = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>芝浦工業大学駅伝部 欠食フォーム</title>
  <style>
    body {
      font-family: "Hiragino Mincho Pro", serif;
      background: repeating-linear-gradient(
        45deg,
        #004225,
        #004225 40px,
        #f5f5f5 40px,
        #f5f5f5 80px
      );
      padding: 20px;
      color: #004225;
    }
    h1 {
      font-size: 32px;
      text-align: center;
    }
    .form-box {
      background: white;
      padding: 20px;
      border-radius: 12px;
      max-width: 600px;
      margin: 20px auto;
    }
    label, select, input[type="checkbox"] {
      display: block;
      margin-top: 10px;
    }
  </style>
</head>
<body>
  <h1>芝浦工業大学駅伝部 欠食申請フォーム</h1>
  <div class="form-box">
    <form action="/submit" method="post">
      <label>名前:
        <select name="name" required>
          {% for name in members %}
            <option value="{{ name }}">{{ name }}</option>
          {% endfor %}
        </select>
      </label>
      <label>日付:
        <input type="date" name="date" required>
      </label>
      <label><input type="checkbox" name="朝"> 朝食</label>
      <label><input type="checkbox" name="夜"> 夕食</label>
      <button type="submit">申請</button>
    </form>
  </div>

  <h2>📢 お知らせ</h2>
  {% for comment in comments %}
    {% if comment["start"] <= today <= comment["end"] %}
      <div style="border-left: 5px solid #004225; padding-left: 10px; margin-bottom: 8px;">
        <strong>{{ comment["author"] }}</strong>：{{ comment["text"] }}
        （{{ comment["start"] }}～{{ comment["end"] }}）
        <a href="/delete_comment?index={{ loop.index0 }}">❌削除</a>
      </div>
    {% endif %}
  {% endfor %}

  <h2>📋 欠食者一覧</h2>
  {% for date, entries in skips.items() %}
    <h3>{{ date }}</h3>
    <ul>
    {% for entry in entries %}
      <li>{{ entry[0] }} - {{ entry[1:] }}</li>
    {% endfor %}
    </ul>
  {% endfor %}

  <a href="/delete">欠食申請の削除はこちら</a><br>
  <a href="/comments">📢 お知らせを書く</a><br>
  <a href="/csv">📂 過去の欠食記録CSV</a>
</body>
</html>
"""

TEMPLATE_DELETE = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>欠食削除</title></head>
<body>
  <h1>欠食削除フォーム</h1>
  <form method="POST">
    <label>名前:
      <select name="name" required>
        {% for name in members %}
          <option value="{{ name }}">{{ name }}</option>
        {% endfor %}
      </select>
    </label><br>
    <label>日付:
      <input type="date" name="date" required>
    </label><br>
    <button type="submit">削除</button>
  </form>
  <a href="/">戻る</a>
</body>
</html>
"""
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
