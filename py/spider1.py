import requests
from bs4 import BeautifulSoup

url = "https://www1.pu.edu.tw/~tcyang/course.html"
Data = requests.get(url)
#print(Data.text)
sp = BeautifulSoup(Data.text, "html.parser")
result=sp.find("td")
for item in requests:
	print(item.text)
	print()
