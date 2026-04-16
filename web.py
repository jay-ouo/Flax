import requests
from bs4 import BeautifulSoup

from flask import Flask,render_template,request
from datetime import datetime

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    fcred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

firebase_admin.initialize_app(cred)



app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>歡迎進入周英智的網站20260409aaa</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>現在日期時間</a><hr>"
    link += "<a href=/me>關於我</a><hr>"
    link += "<a href=/welcome?u=周英智&d=靜宜資管&c=資訊管理學系二B>Post傳值</a><hr>"
    link += "<a href=/account>Post傳值</a><hr>"
    link += "<a href=/math>次方與根號計算</a><hr>"
    link += "<a href=/read>讀取Firestore資料</a><hr>"
    link += "<a href=/read2>查詢老師研究室</a><hr>"
    link += "<a href=/spider>爬取子青老師本學期課程</a><hr>"

    return link

@app.route("/spider")
def spider():
    R = ""
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    #print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".team-box a")

    for i in result:
        R += i.text + i.get("href") + "<br>"
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
        <br>
        <a href="/">返回首頁</a>
        """
        return html_form

    db = firestore.client()
    collection_ref = db.collection("靜宜資管2026B")
    docs = collection_ref.stream()
   
    Result = f"<h3>您搜尋的關鍵字：{keyword}</h3>"
    found_data = False
   
    for doc in docs:
        teacher = doc.to_dict()
        if "name" in teacher and keyword in teacher["name"]:
            Result += str(teacher) + "<br><br>"
            found_data = True

    if not found_data:
        Result += "抱歉，找不到符合的老師資料。<br><br>"
       
    Result += '<br><a href="/read2">返回重新搜尋</a>'
   
    return Result

	
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

@app.route("/welcome", methods=["Get"])
def welcome(): 
	user = request.values.get("u") 
	d = request.values.get("d") 
	c = request.values.get("c")
	return render_template("welcome.html", name= user, dep = d, cos= c)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
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
                if y == 0:
                    result = "錯誤：不能開0次方根"
                else:
                    result = x ** (1/y)
            else:
                result = "運算符號錯誤"
            return f"計算結果為：{result} <br><a href='/math'>回計算機</a>"
        except:
            return "請輸入正確的數字！<br><a href='/math'>返回</a>"
    else:
    	
        return render_template("math.html")



if __name__ == "__main__":
	app.run(debug=True)