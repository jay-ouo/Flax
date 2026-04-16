import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from datetime import datetime
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# --- Firebase 初始化修正 ---
if not firebase_admin._apps:  # 確保不重複初始化
    if os.path.exists('serviceAccountKey.json'):
        # 本地環境
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
    else:
        # 雲端環境 (Vercel)
        # 這裡從環境變數讀取 JSON 字串
        firebase_config = os.getenv("FIREBASE_CONFIG")
        if firebase_config:
            cred_dict = json.loads(firebase_config)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        else:
            print("錯誤：找不到 Firebase 配置")

app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>歡迎進入周英智的網站20260409aaa</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>現在日期時間</a><hr>"
    link += "<a href=/me>關於我</a><hr>"
    link += "<a href='/welcome?u=周英智&d=靜宜資管&c=資訊管理學系二B'>Get傳值</a><hr>"
    link += "<a href=/account>Post傳值</a><hr>"
    link += "<a href=/math>次方與根號計算</a><hr>"
    link += "<a href=/read2>查詢老師研究室</a><hr>"
    link += "<a href=/spider>爬取子青老師本學期課程</a><hr>"
    return link

@app.route("/spider")
def spider():
    R = "<h2>子青老師本學期課程</h2>"
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    try:
        Data = requests.get(url)
        Data.encoding = "utf-8"
        sp = BeautifulSoup(Data.text, "html.parser")
        result = sp.select(".team-box a")
        for i in result:
            R += f"課程：{i.text} | <a href='{i.get('href')}'>課程大綱</a><br>"
    except:
        R = "爬蟲抓取失敗"
    return R
    
@app.route("/read2")
def read2():
    keyword = request.args.get("keyword")
    
    if not keyword:
        html_form = """
        <h2>搜尋老師系統</h2>
        <form action="/read2" method="GET">
            請輸入名字關鍵字：<input type="text" name="keyword" required>
            <input type="submit" value="開始搜尋">
        </form>
        <br><a href="/">返回首頁</a>
        """
        return html_form

    db = firestore.client()
    # 確保集合名稱與你 Firestore 一致
    collection_ref = db.collection("靜宜資管2026B")
    docs = collection_ref.stream()
    
    Result = f"<h3>您搜尋的關鍵字：{keyword}</h3>"
    found_data = False
    
    for doc in docs:
        teacher = doc.to_dict()
        if "name" in teacher and keyword in teacher["name"]:
            # 格式化輸出：藍色粗體
            name = teacher.get("name", "未知")
            lab = teacher.get("lab", "未提供")
            Result += f"<p style='color:blue; font-weight:bold;'>{name} 老師的研究是在 {lab}</p>"
            found_data = True

    if not found_data:
        Result += f"<p>抱歉，找不到關鍵字：{keyword} 的老師資料。</p>"
        
    Result += '<br><a href="/read2">返回重新搜尋</a> | <a href="/">回首頁</a>'
    return Result

# --- 其他路由保持不變 ---
@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/today")
def today():  
    now = datetime.now()
    return render_template("today.html", datetime = str(now))

@app.route("/me")
def me():  
    return render_template("mis2026.html")

@app.route("/welcome", methods=["GET"])
def welcome(): 
    user = request.args.get("u") 
    d = request.args.get("d") 
    c = request.args.get("c")
    return render_template("welcome.html", name=user, dep=d, cos=c)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        return f"您輸入的帳號是：{user}; 密碼為：{pwd} <br><a href='/'>回首頁</a>"
    return render_template("account.html")

@app.route("/math", methods=["GET", "POST"])
def math_calc():
    if request.method == "POST":
        try:
            x = float(request.form["x"])
            opt = request.form["opt"]
            y = float(request.form["y"])
            if opt == "^":
                result = x ** y
            elif opt == "√":
                result = x ** (1/y) if y != 0 else "錯誤：不能開0次方根"
            else:
                result = "運算符號錯誤"
            return f"計算結果為：{result} <br><a href='/math'>回計算機</a>"
        except:
            return "請輸入正確的數字！<br><a href='/math'>返回</a>"
    return render_template("math.html")

if __name__ == "__main__":
    app.run(debug=True)