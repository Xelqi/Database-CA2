import couchdb
import json

# Load your JSON data
with open('exported_data.json', 'r') as file:
    data = json.load(file)

# Connect to CouchDB
couch = couchdb.Server("http://admin:couchdb@127.0.0.1:5984")
db = couch['c20355901_milosz_lewandowski']

# Perform bulk upload
response = db.update(data['docs'])

# Check response for success or failure of each document
for doc in response:
    print(doc)