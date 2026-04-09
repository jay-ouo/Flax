from flask import Flask,render_template,request
from datetime import datetime
app = Flask(__name__)

@app.route("/")
def index():
	link = "<h1>歡迎進入周英智的網站20260409</h1>"
	link += "<a href=/mis>課程</a><hr>"
	link += "<a href=/today>現在日期時間</a><hr>"
	link += "<a href=/me>關於我</a><hr>"
	link += "<a href=/welcome?u=周英智&d=靜宜資管&c=資訊管理導論>Get傳值</a><hr>"
	link += "<a href=/account>Post傳值</a><hr>"
	link +="<a href=/math>次方與根號計算</a><hr>"
	return link
	
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