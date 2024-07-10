Global Query
http://admin:couchdb@127.0.0.1:5984/c20355901_milosz_lewandowski/_design/my_global_query/_view/global_view?include_docs=true

Curl Bulk Docs
curl -X POST -H "Content-Type: application/json" http://admin:couchdb@127.0.0.1:5984/test/_bulk_docs -d exported_data.json
