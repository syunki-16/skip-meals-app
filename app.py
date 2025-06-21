from flask import Flask, render_template, request, redirect, url_for
import os
import csv
from datetime import datetime

app = Flask(__name__)

DATA_FILE = 'skip_data.csv'
MEMBERS = ["徳本監督", "岡田コーチ", "内山壽頼", "大森隼人", "菊池笙", "國井優仁", "佐竹響", "長谷川琉斗", "本田伊吹", "横尾皓",
           "石井達也", "植田航生", "宇野利希", "小坂悠太", "澤田悠斗", "塩崎浩貴", "新城陽", "丹野暁翔", "永田覇人", "米原大祐",
           "上原駿希", "太田直希", "熊井康太", "小林圭吾", "酒井忠久", "高橋柊", "中川成弥", "水戸瑛太", "宮本大心",
           "赤繁咲多", "岩瀬駿介", "大沼亮太", "奥村心", "後藤秀波", "高松桜太", "竹中友規", "森尻悠翔", "渡邊義仁"]

@app.route("/")
def home():
    return redirect("/form")

@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("dates")
        times = request.form.getlist("time")

        with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for t in times:
                writer.writerow([date, t, name])

        return redirect("/list")

    return render_template("form.html", members=MEMBERS)

@app.route("/list")
def list_skips():
    skips = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
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

        rows = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = [row for row in reader if row != [date, time, name]]

        with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        return redirect("/list")

    return render_template("delete.html", members=MEMBERS)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
