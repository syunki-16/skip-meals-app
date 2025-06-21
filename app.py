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
        dates = request.form.getlist("dates")
        if not name or not dates:
            return redirect("/form")

        # 保存処理（週単位でCSV保存）
        for date_str in dates:
            csv_file = get_csv_filename_for_week(date_str)
            day = datetime.strptime(date_str, "%Y-%m-%d").strftime("%a")  # 曜日
            row = {"名前": name, "日付": date_str, "曜日": day}
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                df = df[df["名前"] != name]  # 同名削除（重複防止）
                df = pd.concat([df, pd.DataFrame([row])])
            else:
                df = pd.DataFrame([row])
            df.to_csv(csv_file, index=False, encoding="utf-8")
        return redirect("/list")

    return render_template("form.html", members=members)
@app.route("/list")
def list_skips():
    # 本日以降の日付の申請のみ表示（過去は自動で非表示）
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

        # 指定日のファイルから削除
        csv_file = get_csv_filename_for_week(date)
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            df = df[~((df["名前"] == name) & (df["日付"] == date))]
            df.to_csv(csv_file, index=False, encoding="utf-8")

        return redirect("/list")

    # フォーム表示用：最新の欠食データ取得
    entries = []
    for file in sorted(os.listdir(".")):
        if file.startswith("skip_") and file.endswith(".csv"):
            df = pd.read_csv(file)
            for _, row in df.iterrows():
                entries.append({"name": row["名前"], "date": row["日付"]})
    return render_template("delete.html", entries=entries)
