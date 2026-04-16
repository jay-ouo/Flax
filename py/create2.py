import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "周英智",
  "mail": "videogood0405@gmail.com",
  "lab": 801
}

doc_ref = db.collection("靜宜資管2026B").document("jay_ouo")
doc_ref.set(doc)
