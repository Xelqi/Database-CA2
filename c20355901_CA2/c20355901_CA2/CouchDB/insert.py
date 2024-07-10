import couchdb
import mariadb
from decimal import Decimal
import datetime
import json

# Initialize lists for accumulating documents
fact_documents = []
dimviewer_documents = []

# Connect to CouchDB
couch = couchdb.Server("http://admin:couchdb@127.0.0.1:5984")
db_name = "c20355901_milosz_lewandowski"  # Replace with your desired database name

try:
    db = couch[db_name]
except couchdb.http.ResourceNotFound:
    print(f"Error: Database '{db_name}' not found. Please create the database or check the name.")
    
# Connect to your MariaDB relational database
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "mariadb",
    "database": "MusicDimDB",  # Replace with the name of your database
}
conn = mariadb.connect(**db_config)
cursor = conn.cursor()

# Retrieve the data from FACT table
fact_query = "SELECT VOTEDATE, VIEWERSK, PARTSK, FACTSK, VOTE, VOTECATEGORY, VOTEMODE, VOTECOST FROM FACT"
cursor.execute(fact_query)
fact_data = cursor.fetchall()

# Creating a single document, merging 2 dimensions into each FACT document
for row in fact_data:
    vote_date_sk=(row[0].strftime('%Y/%m/%d'))
    viewer_sk=int(row[1])
    part_sk=int(row[2])
    
    # Retrieve the DIMDATE details
    cursor.execute("SELECT DIMMONTH FROM DIMDATE WHERE DIMDATE = %s", (vote_date_sk,))
    month = cursor.fetchone()
    date_month = month[0]

    cursor.execute("SELECT DIMYEAR FROM DIMDATE WHERE DIMDATE = %s", (vote_date_sk,))
    year = cursor.fetchone()
    date_year=year[0]
    
    cursor.execute("SELECT DIMDAYOFWEEK FROM DIMDATE WHERE DIMDATE = %s", (vote_date_sk,))
    day = cursor.fetchone()
    date_day = day[0]

    # Retreive the DIMPART details
    cursor.execute("SELECT PARTNAME FROM DIMPART WHERE DIMPARTSK = %s", (part_sk,))
    part_name = cursor.fetchone()
    participant_name = part_name[0]
    
    cursor.execute("SELECT COUNTYNAME FROM DIMPART WHERE DIMPARTSK = %s", (part_sk,))
    part_county = cursor.fetchone()
    participant_county = part_county[0]
    
    # Create a document from the data extracted
    document = {
        "_id": f"{participant_county.lower()}:{row[3]}",  # County Partition and Primary key of Fact Table
        "type": "fact",
        "data": {
            "VOTE": row[4],
            "VOTECATEGORY": row[5],
            "VOTEMODE": row[6],
            "VOTECOST": float(row[7]),
            "VOTEDATE": row[0].strftime('%Y/%m/%d'),
            "DIMYEAR": date_year,
            "DIMMONTH": date_month,
            "DIMDAYOFWEEK": date_day,
            "PARTSK": row[2],
            "PARTNAME": participant_name,
            "COUNTYNAME": participant_county,
            "VIEWERSK": row[1], # Viewer Dimension Link to seperate doc 
        }
    }

    # Insert the document into CouchDB
    # Check if the document_id starts with an underscore and if the county is "Cork" or "Galway"
    if participant_county == "Cavan" or participant_county == "Galway":
        # Insert the document into CouchDB
        db.save(document)
        print("Added FACT document:", document["_id"])
        fact_documents.append(document)

# Adding Dim Viewer Document Below
# Retrieve the data from FACT table
dim_query = "SELECT * FROM DIMVIEWER"
cursor.execute(dim_query)
DIMVIEWER_data = cursor.fetchall()

for row in DIMVIEWER_data:
# Create a document from the data extracted
    DIMVIEWER_document = {
        "_id": f"viewer:{str(row[0])}",
        "type": "dim",
        "dim_data": {
            "DIMVIEWER_SK": row[0],
            "COUNTYNAME": row[1],
            "AGE_GROUP_DESC": row[2],
        }
    }
    # Insert the document into CouchDB
    db.save(DIMVIEWER_document)
    print("Added DIMVIEWER document:" + DIMVIEWER_document["_id"])
    dimviewer_documents.append(DIMVIEWER_document)

# Close database connections
cursor.close()
conn.close()


# Combine all documents into a single list for bulk upload
all_documents = fact_documents + dimviewer_documents
bulk_docs_payload = {"docs": all_documents}

# Write to JSON file
with open("exported_data.json", "w") as file:
    json.dump(bulk_docs_payload, file, indent=4)

print("Exported data to exported_data.json")