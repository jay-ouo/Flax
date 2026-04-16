import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

keyword = input("輸入名字關鍵字")
collection_ref = db.document("靜宜資管/jay_ouo")
doc = collection_ref.get()
for doc in docs:
	teacher = doc.to_dict()
	if keyword in teacher ["name"]:
		print(doc.to_dict())