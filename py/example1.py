def Split(x):
	x = x.split(",")
	school = x[0].replace("我是","")
	print(f"學校:{school}")
	print(f"姓名:{x[2]}")
	
if __name__ == "__main__":
	Name = "我是靜宜大學,資管二B,周英智,Ian"
	Split(Name)