# 欠食管理 Flaskアプリ（最新版）
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
        new_row = [name] + [request.form.get(f"{day}_{meal}") for day in days for meal in meals] + [comment]

        rows = []
        if os.path.exists(csv_file):
            with open(csv_file, newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))
            header = rows[0]
            rows = [r for r in rows[1:] if r[0] != name]  # remove old row
        else:
            header = ["名前"] + [f"{d}_{m}" for d in days for m in meals] + ["コメント"]

        rows.append(new_row)
        with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
        return redirect("/")
    return render_template_string("TEMPLATE_FORM", members=members, days=days, meals=meals)

@app.route("/list")
def skip_list():
    today = datetime.now()
    current_week = get_csv_filename_by_date(today.strftime("%Y-%m-%d"))
    skips_by_day = defaultdict(list)
    base_date = datetime.strptime(current_week[12:22], "%Y-%m-%d")

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

    return render_template_string("TEMPLATE_LIST", skips=skips_by_day, notices=comments_display)

@app.route("/comment", methods=["GET", "POST"])
def comment_page():
    if request.method == "POST":
        text = request.form.get("comment")
        start = request.form.get("start_date")
        end = request.form.get("end_date")
        save_comment(text, start, end)
        return redirect("/list")
    return render_template_string("TEMPLATE_COMMENT")

import os
PORT = int(os.environ.get("PORT", 10000))
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=PORT)
