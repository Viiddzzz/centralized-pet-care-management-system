import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# 1. Initialize the Admin SDK
# Provide path to your service account key JSON file
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)

# 2. Create a Firestore client
db = firestore.client()

# 3. Fetch all top-level collections
collections = db.collections()

# 4. Iterate and print collection IDs (names)
collectionnames=[]
for collection in collections:
    print(f"Collection ID: {collection.id}")
    collectionnames.append(collection.id)
    
for x in collectionnames:    
    newdata_ref = db.collection(x)
    newdata = newdata_ref.get()
    data=[]
    print("Collection Name : ", x)
    for doc in newdata:
        temp=doc.to_dict()
        #print("\t",temp['id'])
        print("\t",temp)
        data.append(temp['id'])
    
    for y in data:
        db.collection(x).document(y).delete()