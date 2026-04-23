import requests
from bs4 import BeautifulSoup

url = "https://www1.pu.edu.tw/~tcyang/course.html"
Data = requests.get(url)
Data.encoding = "utf-8"
#print(Data.text)
sp = BeautifulSoup(Data.text, "html.parser")
result=sp.find(id = "h2text")
for item in result:
	print(item.get("src"))
	print()
