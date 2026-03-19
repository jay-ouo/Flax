def square(y):
  print(f"{y} 的平方為 {y**2}") 





x = int(input("請輸入整數:"))
#x += 10
#print("您輸入的是:",x)

if (x<=0):
	print(f"你輸入的數字{x},小於等於0")
else:
	print(f"你輸入的數字{x},大於0")
	for i in range(1,x+1):
		#print(i, end="; ")
		square(i)
