from flask import Flask, render_template, request
from datetime import datetime
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from bs4 import BeautifulSoup

# --- 1. Firebase 初始化邏輯 ---
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
            raise ValueError("找不到 Firebase 配置環境變數，請確認 serviceAccountKey.json 或 FIREBASE_CONFIG")
    firebase_admin.initialize_app(cred)

db = firestore.client()
app = Flask(__name__)

# --- 2. 路由設定 ---

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
    link += "<a href=/spiderMovie>爬取即將上映電影,存到資料庫</a><hr>"
    link += "<a href=/movie>爬取即將上映電影並搜尋介面</a><hr>"
    link += "<a href=/road>台中十大肇事路口</a><hr>"
    link += "<a href=/weather>天氣預報查詢</a><hr>"
    return link



@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    # 取得 Dialogflow 傳來的分級參數
    rate = req["queryResult"]["parameters"].get("rate")
   
    # 簡單轉換：對應你資料庫存入的中文名稱
    if rate == "P": rate = "保護級"
    elif rate == "G": rate = "普遍級"

    # 設定開頭語，加上你的名字
    info = f"我是林哲旭設計的機器人。關於您查詢「{rate}」的電影：\n"

    db = firestore.client()
    # 提醒：名稱需與 /rate 存入時的 "本週新片含分級" 一致
    docs = db.collection("本週新片含分級").get()
   
    result = ""
    for doc in docs:
        m = doc.to_dict()
        if rate in m.get("rate", ""):
            result += m.get("title") + "\n"

    if result == "":
        info += "目前資料庫中查無此級別的電影。"
    else:
        info += result

    return jsonify({"fulfillmentText": info})

@app.route("/weather")
def weather():
    # 1. 取得使用者搜尋的縣市 (預設為空字串，這樣一進網頁就不會先抓台中)
    city = request.args.get("city", "")
    
    # 2. 搜尋介面 (表單)
    R = """
    <form action="/weather" method="get">
        請輸入縣市：<input type="text" name="city" placeholder="例如：台北市">
        <input type="submit" value="查詢">
    </form>
    <hr>
    """
    
    # 3. 判斷：如果使用者有輸入東西才去抓 API
    if city:
        city = city.replace("台", "臺")
        
        # 提醒：Authorization 記得要換成你申請到的正確金鑰喔！
        auth_key = "rdec-key-123-45678-011121314"
        url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={auth_key}&format=JSON&locationName={city}"
        
        try:
            Data = requests.get(url, verify=False)
            JsonData = json.loads(Data.text)
            
            # 檢查 API 是否有抓到這個縣市的資料
            if JsonData["records"]["location"]:
                loc_name = JsonData["records"]["location"][0]["locationName"]
                Weather = JsonData["records"]["location"][0]["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
                Rain = JsonData["records"]["location"][0]["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
                
                R += f"<h2>{loc_name} 最新天氣預報</h2>"
                R += f"天氣狀況：{Weather}<br>"
                R += f"降雨機率：{Rain}%"
            else:
                R += f"<b style='color:orange;'>找不到「{city}」的資料，請確認名稱是否正確。</b>"
                
        except Exception as e:
            R += f"<b style='color:red;'>連線失敗或 API 金鑰錯誤。</b>"
    else:
        # 如果沒輸入東西，就顯示歡迎文字
        R += "<h1>歡迎使用天氣預報系統 作者:周英智</h1>"
        R += "請在上方輸入框輸入想要查詢的縣市名稱。"

    return R

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/road")
def road():
    R= "<h1>台中十大肇事路口(113年10月)作者:周英智</h1>"

    url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
    Data = requests.get(url,verify=False)
    #print(Data.text)

    JsonData = json.loads(Data.text)
    for item in JsonData:
        R += item["路口名稱"] + "原因:" + item["主要肇因"] + ",件數" + item["總件數"] + "<br>"
        
    return R




# 整合後的電影搜尋與同步系統
@app.route("/movie")
def movie_system():
    q = request.args.get("q")
    url = "http://www.atmovies.com.tw/movie/next/"
    data = requests.get(url)
    data.encoding = "utf-8"
    sp = BeautifulSoup(data.text, "html.parser")
    
    lastUpdate_tag = sp.find(class_="smaller09")
    lastUpdate = lastUpdate_tag.text.replace("更新時間：", "").strip() if lastUpdate_tag else "未知"
    
    result = sp.select(".filmListAllX li")
    total_saved = 0
    
    html_content = "<h1>即將上映電影系統</h1>"
    html_content += f"<p style='color: gray;'>資料庫最近更新日期：{lastUpdate}</p>"
    html_content += """
        <form action="/movie" method="get">
            <input type="text" name="q" placeholder="請輸入片名關鍵字" value="{}">
            <button type="submit">搜尋</button>
        </form>
        <hr>
    """.format(q if q else "")
    
    movie_list_html = ""
    count = 0 
    
    for item in result:
        try:
            title = item.find(class_="filmtitle").text
            movie_id = item.find("a").get("href").replace("/movie/", "").replace("/", "")
            picture = "https://www.atmovies.com.tw/" + item.find("img").get("src")
            hyperlink = "https://www.atmovies.com.tw/" + item.find("a").get("href")
            showDate = item.find(class_="runtime").text[5:15]

            doc = {
                "title": title,
                "picture": picture,
                "hyperlink": hyperlink,
                "showDate": showDate,
                "lastUpdate": lastUpdate
            }
            db.collection("電影2B").document(movie_id).set(doc)
            total_saved += 1

            if not q or q in title:
                count += 1
                movie_list_html += f'<h3><a href="{hyperlink}">{title}</a></h3>'
                movie_list_html += f'<p>電影編號：{movie_id}</p>'
                movie_list_html += f'<p>上映日期：{showDate}</p>'
                movie_list_html += f'<img src="{picture}" width="200"><br><br><hr>'

        except Exception as e:
            print(f"處理電影時發生錯誤: {e}")

    if count == 0 and q:
        movie_list_html = f"<p>很抱歉，找不到包含「{q}」的電影。</p>"
    
    summary = f"<p>系統訊息：本次同步更新了 {total_saved} 部電影到 Firebase 資料庫。</p>"
    return html_content + summary + movie_list_html

# 獨立的爬蟲同步功能
@app.route("/spiderMovie")
def spiderMovie():
    R = ""
    url = "http://www.atmovies.com.tw/movie/next/"
    data = requests.get(url)
    data.encoding = "utf-8"
    sp = BeautifulSoup(data.text, "html.parser")
    
    lastUpdate_tag = sp.find(class_="smaller09")
    lastUpdate = lastUpdate_tag.text.replace("更新時間：", "").strip() if lastUpdate_tag else "未知"
    
    result = sp.select(".filmListAllX li")
    total = 0
    for item in result:
        try:
            movie_id = item.find("a").get("href").replace("/movie/", "").replace("/", "")
            title = item.find(class_="filmtitle").text
            picture = "https://www.atmovies.com.tw" + item.find("img").get("src")
            hyperlink = "https://www.atmovies.com.tw" + item.find("a").get("href")
            showDate = item.find(class_="runtime").text[5:15]

            doc = {
                "title": title, "picture": picture, "hyperlink": hyperlink,
                "showDate": showDate, "lastUpdate": lastUpdate
            }
            db.collection("電影2B").document(movie_id).set(doc)
            total += 1
        except:
            continue

    R += f"網站最近更新日期：{lastUpdate}<br>"
    R += f"總共爬取 {total} 部電影到資料庫"
    return R

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

@app.route("/read3", methods=["GET", "POST"])
def read3():
    if request.method == "POST":
        keyword = request.values.get("keyword")
        Result = f"<h2>查詢姓名關鍵字：{keyword}</h2>"
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
        </form>
        <br><a href="/">回首頁</a>
        """
        return html

@app.route("/spider")
def spider():
    Result="<h2>子青老師本學期課程</h2>"
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".team-box a")
    for i in result:
        Result += f"{i.text} -> <a href='{i.get('href')}'>{i.get('href')}</a><br>"
    return Result + "<br><a href='/'>回首頁</a>"

# --- 3. 程式進入點 (放在最後面) ---
if __name__ == "__main__":
    app.run(debug=True)