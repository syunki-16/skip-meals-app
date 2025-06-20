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

days = ["月", "火", "水", "木", "金", "土", "日"]
meals = ["朝", "夜"]

def get_csv_filename_by_date(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
    except:
        d = datetime.now()
    sunday = d - timedelta(days=(d.weekday() + 1) % 7 - 6)  # 日曜を週の終わりとして扱う
    return f"skip_meals_{sunday.strftime('%Y-%m-%d')}.csv"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        date_str = request.form.get("week_date")
        csv_file = get_csv_filename_by_date(date_str)
        skips = []
        for day in days:
            for meal in meals:
                skips.append(request.form.get(f"{day}_{meal}"))

        # データ上書き：同じ名前があれば削除してから追加
        rows = []
        if os.path.exists(csv_file):
            with open(csv_file, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                if len(rows) > 1:
                    header = rows[0]
                    rows = [row for row in rows if row[0] != name]
                else:
                    header = ["名前"] + [f"{d}_{m}" for d in days for m in meals]
        else:
            header = ["名前"] + [f"{d}_{m}" for d in days for m in meals]

        rows.append([name] + skips)
        with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

        return redirect("/")

    return render_template_string(TEMPLATE_FORM, members=members, days=days, meals=meals)


