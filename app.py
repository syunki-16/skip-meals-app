from flask import Flask, render_template, request, redirect, send_file
import os
import csv
from datetime import datetime, timedelta
import pandas as pd

app = Flask(__name__)

# メンバーリスト（選択欄に使用）
members = [
    "徳本監督", "岡田コーチ", "内山壽頼", "大森隼人", "菊池笙", "國井優仁", "佐竹響", "長谷川琉斗", "本田伊吹", "横尾皓",
    "石井達也", "植田航生", "宇野利希", "小坂悠太", "澤田悠斗", "塩崎浩貴", "新城陽", "丹野暁翔", "永田覇人", "米原大祐",
    "上原駿希", "太田直希", "熊井康太", "小林圭吾", "酒井忠久", "高橋柊", "中川成弥", "水戸瑛太", "宮本大心",
    "赤繁咲多", "岩瀬駿介", "大沼亮太", "奥村心", "後藤秀波", "高松桜太", "竹中友規", "森尻悠翔", "渡邊義仁"
]

# 欠食保存ファイル（週単位）
def get_csv_filename_for_week(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
    except:
        d = datetime.now()
    monday = d - timedelta(days=d.weekday())
    return f"skip_meals_{monday.strftime('%Y-%m-%d')}.csv"

# お知らせファイル
ANNOUNCE_FILE = "announcements.csv"

@app.route("/")
def home():
    return redirect("/form")

@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form.get("name")
        date_values = request.form.getlist("dates")

        for val in date_values:
            date_str, time_slot = val.split("_")
            csv_file = get_csv_filename_for_week(date_str)
            row = {"名前": name, "日付": date_str, "曜日": datetime.strptime(date_str, "%Y-%m-%d").strftime("%a"), "朝": "", "夜": ""}
            if time_slot == "朝":
                row["朝"] = "○"
            elif time_slot == "夜":
                row["夜"] = "○"

            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                df = df[~((df["名前"] == name) & (df["日付"] == date_str))]  # 同名・同日を削除
                df = pd.concat([df, pd.DataFrame([row])])
            else:
                df = pd.DataFrame([row])
            df.to_csv(csv_file, index=False, encoding="utf-8")

        return redirect("/list")

    # お知らせ読み込み（現在表示すべきものだけ）
    announcements = []
    if os.path.exists(ANNOUNCE_FILE):
        df = pd.read_csv(ANNOUNCE_FILE)
        today = datetime.now().date()
        for _, row in df.iterrows():
            start = datetime.strptime(row["start"], "%Y-%m-%d").date()
            end = datetime.strptime(row["end"], "%Y-%m-%d").date()
            if start <= today <= end:
                announcements.append(row.to_dict())

    return render_template("form.html", members=members, announcements=announcements, now=datetime.now(), timedelta=timedelta)

@app.route("/list")
def list_skips():
    skips = []
    today = datetime.now().date()
    for file in sorted(os.listdir(".")):
        if file.startswith("skip_") and file.endswith(".csv"):
            df = pd.read_csv(file)
            df["日付"] = pd.to_datetime(df["日付"]).dt.date
            df = df[df["日付"] >= today]
            skips.extend(df.to_dict(orient="records"))
    skips.sort(key=lambda x: x["日付"])
    return render_template("list.html", skips=skips)

@app.route("/delete", methods=["GET", "POST"])
def delete_entry():
    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("date")

        csv_file = get_csv_filename_for_week(date)
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            df = df[~((df["名前"] == name) & (df["日付"] == date))]
            df.to_csv(csv_file, index=False, encoding="utf-8")

        return redirect("/list")

    entries = []
    for file in sorted(os.listdir(".")):
        if file.startswith("skip_") and file.endswith(".csv"):
            df = pd.read_csv(file)
            for _, row in df.iterrows():
                entries.append({"name": row["名前"], "date": row["日付"]})
    return render_template("delete.html", entries=entries)

@app.route("/announce", methods=["GET", "POST"])
def manage_announce():
    if request.method == "POST":
        author = request.form.get("author")
        message = request.form.get("message")
        start = request.form.get("start")
        end = request.form.get("end")
        if os.path.exists(ANNOUNCE_FILE):
            df = pd.read_csv(ANNOUNCE_FILE)
        else:
            df = pd.DataFrame(columns=["author", "message", "start", "end"])
        df.loc[len(df)] = [author, message, start, end]
        df.to_csv(ANNOUNCE_FILE, index=False, encoding="utf-8")
        return redirect("/announce")

    announcements = []
    if os.path.exists(ANNOUNCE_FILE):
        df = pd.read_csv(ANNOUNCE_FILE)
        announcements = df.to_dict(orient="records")
    return render_template("announce.html", announcements=announcements)

@app.route("/announce/delete", methods=["POST"])
def delete_announcement():
    index = int(request.form.get("index"))
    if os.path.exists(ANNOUNCE_FILE):
        df = pd.read_csv(ANNOUNCE_FILE)
        if 0 <= index < len(df):
            df = df.drop(index)
            df.to_csv(ANNOUNCE_FILE, index=False, encoding="utf-8")
    return redirect("/announce")
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
