import couchdb

# CouchDB connection details
couchdb_url = 'http://localhost:5984/'
admin_user = 'admin'
admin_password = 'couchdb'

# Connect to CouchDB
couch = couchdb.Server(couchdb_url)
couch.resource.credentials = (admin_user, admin_password)

# Database name
db_name = 'c20355901_milosz_lewandowski' 

# Access the database
db = couch[db_name]

# Design document ID and view name
design_doc_id = '_design/over_50_check'
view_name = 'viewers_over_50'

# Design document with map function to find viewers in the age range ">50"
design_doc = {
    '_id': design_doc_id,
    'views': {
        view_name: {
            'map': '''
                function(doc) {
                    if ((doc.type === 'dim') && doc.dim_data.AGE_GROUP_DESC === '>50') {
                        emit(doc._id, doc);
                    }
                }
            '''
        }
    }
}

# Save the design document
if design_doc_id in db:
    existing_doc = db[design_doc_id]
    design_doc['_rev'] = existing_doc.rev
db.save(design_doc)

print(f"Design document {design_doc_id} with view {view_name} created.")