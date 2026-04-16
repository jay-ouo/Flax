from flask import Flask, render_template, request
from datetime import datetime
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from bs4 import BeautifulSoup

# --- Firebase 初始化邏輯 ---
if not firebase_admin._apps:
    if os.path.exists('serviceAccountKey.json'):
        # 本地環境
        cred = credentials.Certificate('serviceAccountKey.json')
    else:
        # 雲端環境 (Vercel)
        firebase_config = os.getenv('FIREBASE_CONFIG')
        if firebase_config:
            cred_dict = json.loads(firebase_config)
            cred = credentials.Certificate(cred_dict)
        else:
            raise ValueError("找不到 Firebase 配置環境變數")
    firebase_admin.initialize_app(cred)

db = firestore.client()
app = Flask(__name__)

# --- 路由設定 ---

@app.route("/")
def index():
    link = "<h1>歡迎進入周英智的網站20260409</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>現在日期時間</a><hr>"
    link += "<a href=/me>關於我</a><hr>"
    link += "<a href='/welcome?u=英智&d=靜宜資管&c=資訊管理導論'>Get傳值</a><hr>"
    link += "<a href=/account>Post傳值(帳密)</a><hr>"
    link += "<a href=/math>次方與根號計算</a><hr>"
    link += "<a href=/read>讀取Firestore資料</a><hr>"
    link += "<a href=/read2>讀取Firestore資料(固定關鍵字:楊)</a><hr>"
    link += "<a href=/read3>讀取Firestore資料(動態輸入關鍵字)</a><hr>"
    link += "<a href=/spider>爬取子青老師本學期課程</a><hr>"
    return link

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime=str(now))

@app.route("/me")
def me():  
    return render_template("mis2026.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    user = request.values.get("u")
    d = request.values.get("d")
    c = request.values.get("c")
    return render_template("welcome.html", name=user, dep=d, course=c)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        return f"您輸入的帳號是：{user}; 密碼為：{pwd} <br><a href='/'>回首頁</a>"
    return render_template("account.html")

@app.route("/math", methods=["GET", "POST"])
def math():
    result = ""
    if request.method == "POST":
        try:
            x = float(request.form.get("x"))
            y = float(request.form.get("y"))
            opt = request.form.get("opt")
            if opt == "∧":
                result = x ** y
            elif opt == "√":
                result = "錯誤：不能開 0 次方根" if y == 0 else x ** (1 / y)
        except:
            result = "請輸入有效數字"
    return render_template("math.html", final_result=result)

@app.route("/read")
def read():
    Result = "<h2>所有老師資料：</h2>"
    collection_ref = db.collection("靜宜資管2026B")    
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).get()    
    for doc in docs:         
        Result += str(doc.to_dict()) + "<br><hr>"    
    return Result + "<a href=/>回首頁</a>"

@app.route("/read2")
def read2():
    Result = "<h2>搜尋關鍵字：楊</h2>"
    keyword = "楊"
    collection_ref = db.collection("靜宜資管2026B")    
    docs = collection_ref.get()    
    found = False
    for doc in docs:
        teacher = doc.to_dict()
        if keyword in teacher.get("name", ""):         
            Result += str(teacher) + "<br>"
            found = True
    if not found:
        Result += "抱歉，查無資料"
    return Result + "<br><a href=/>回首頁</a>"

# --- 修改後的 read3：結合表單輸入與 Firestore 查詢 ---
@app.route("/read3", methods=["GET", "POST"])
def read3():
    if request.method == "POST":
        # 抓取 account.html 裡面 name="user" 的欄位當作關鍵字
        keyword = request.values.get("keyword")
        Result = f"<h2>查詢姓名關鍵字：{keyword}</h2>"
        db=firestore.client()
        collection_ref = db.collection("靜宜資管2026B")
        docs = collection_ref.get()
        
        found = False
        for doc in docs:
            teacher = doc.to_dict()
            if keyword in teacher.get("name", ""):
                Result += f"老師：{teacher.get('name')}, 研究室：{teacher.get('lab')}<br>"
                found = True
        
        if not found:
            Result += "抱歉，查無此關鍵字之老師資料。"


        return Result + "<br><a href='/read3'>重新查詢</a> | <a href='/'>回首頁</a>"
    else:
        html="""
        <h2>老師查詢</h2>
        <form action="/read3" method="POST">
            請輸入老師姓名關鍵字
            <input type="text" name="keyword">
            <button type="submit">查詢</button>
        </from>
        <br><a href="/">回首頁</a>
        """
        # GET 請求時，顯示輸入表單
        return html


@app.route("/spider")
def spider():
    Result=""
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    #print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".team-box a")
    for i in result:
        Result+=str(i.text)+str(i.get("href"))+"<br>"
    return Result


if __name__ == "__main__":
    app.run(debug=True)