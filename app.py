from flask import Flask, render_template, request, redirect
import csv
import os
import json
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "skip_data.csv"
ANNOUNCE_FILE = "announcements.json"
MEMBERS = [
    "徳本監督", "岡田コーチ", "内山壽頼", "大森隼人", "菊池笙", "國井優仁", "佐竹響", "長谷川琉斗", "本田伊吹", "横尾皓",
    "石井達也", "植田航生", "宇野利希", "小坂悠太", "澤田悠斗", "塩崎浩貴", "新城陽", "丹野暁翔", "永田覇人", "米原大祐",
    "上原駿希", "太田直希", "熊井康太", "小林圭吾", "酒井忠久", "高橋柊", "中川成弥", "水戸瑛太", "宮本大心",
    "赤繁咲多", "岩瀬駿介", "大沼亮太", "奥村心", "後藤秀波", "高松桜太", "竹中友規", "森尻悠翔", "渡邊義仁"
]

@app.route("/")
def index():
    return redirect("/form")

@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("date")
        times = request.form.getlist("time")

        if not name or not date or not times:
            return "情報が不足しています", 400

        with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for time in times:
                writer.writerow([date, time, name])

        return redirect("/list")

    announcements = load_announcements()
    today = datetime.now().date()
    active_announcements = [a for a in announcements if a['start'] <= str(today) <= a['end']]
    return render_template("form.html", members=MEMBERS, announcements=active_announcements)

@app.route("/list")
def list_skips():
    skips = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) != 3:
                    continue
                date, time, name = row
                if date not in skips:
                    skips[date] = {"朝": [], "夜": []}
                skips[date][time].append(name)
    return render_template("list.html", skips=skips)

@app.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("date")
        time = request.form.get("time")

        if not os.path.exists(DATA_FILE):
            return redirect("/list")

        new_rows = []
        with open(DATA_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 3 and not (row[0] == date and row[1] == time and row[2] == name):
                    new_rows.append(row)

        with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(new_rows)

        return redirect("/list")

    return render_template("delete.html", members=MEMBERS)

@app.route("/announce", methods=["GET", "POST"])
def announce():
    if request.method == "POST":
        author = request.form.get("author")
        message = request.form.get("message")
        start = request.form.get("start")
        end = request.form.get("end")

        if not all([author, message, start, end]):
            return "すべての項目を入力してください", 400

        announcements = load_announcements()
        announcements.append({
            "author": author,
            "message": message,
            "start": start,
            "end": end
        })
        save_announcements(announcements)

        return redirect("/announce")

    announcements = load_announcements()
    return render_template("announce.html", announcements=announcements)

@app.route("/announce/delete", methods=["POST"])
def delete_announcement():
    ann_id = int(request.form.get("id"))
    announcements = load_announcements()
    if 0 <= ann_id < len(announcements):
        announcements.pop(ann_id)
    save_announcements(announcements)
    return redirect("/announce")

def load_announcements():
    if os.path.exists(ANNOUNCE_FILE):
        with open(ANNOUNCE_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []

def save_announcements(data):
    with open(ANNOUNCE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
