import couchdb

# CouchDB connection details
couchdb_url = "http://localhost:5984/"
admin_user = "admin"
admin_password = "couchdb"

# Connect to CouchDB
couch = couchdb.Server(couchdb_url)
couch.resource.credentials = (admin_user, admin_password)

# Database name
db_name = "c20355901_milosz_lewandowski"

# Access the database
db = couch[db_name]

# Design document ID and view name
design_doc_id = "_design/my_global_query"
view_name = "global_view"

# Design document with map function to emit facts and dims
design_doc = {
    "_id": design_doc_id,
    "language": "javascript",
    "options": {"partitioned": False},
    "views": {
        view_name: {
            "map": """
                function(doc) { 
                    if (doc.type === 'fact') { 
                        emit(['fact', doc._id], doc); 
                    } else if (doc.type === 'dim') { 
                        emit(['dim', doc._id], doc); 
                    } 
                }
            """
        }
    },
}

# Save the design document
if design_doc_id in db:
    existing_doc = db[design_doc_id]
    design_doc["_rev"] = existing_doc.rev
db.save(design_doc)

print(f"Design document {design_doc_id} with view {view_name} created.")
