# C20355901 Milosz Lewandowski CA2 #
***STEP BY STEP RUN*** <Br>
To start docker compose up -d <br>
Then run **DimensionalModelSetup** in dbeaver to populate mariadb<br>
Go into CouchDB and Create a partioned database called **c20355901_milosz_lewandowski** <br>
CD into CouchDB folder run **insert.py** make sure you have the imports or use **exported_data.json** with bulk_docs<br>
Use the **replica.json** to create the master - ***slave - replication*** with a ***selector porting only County Cavan Docs for Fact Doc and Dim Doc***<br>
Run **global_query.py** and **part_query.py** and read PARTIONED.READ.MD to add view for **Fact** and **Dim** on partions<br>
CD into Cassandra make sure its running and run **insert_data.py** to create keyspace and populate it.<br>
Open two terminals in the first do **docker exec -it cassandra1 bash -c  'cqlsh'** <br>
In the second do **docker exec -it cassandra2 bash -c  'cqlsh'** <br>
Now make a change in one of the terminals e.g <br>
```
INSERT INTO fact_data (
    factsk,
    vote,
    votecategory,
    votemode,
    votecost,
    votedate,
    partsk,
    viewersk,
    viewer_countyname,
    age_group_desc,
    dimdate,
    dim_month,
    dim_year,
    dim_dayofweek,
    dimpartsk,
    dim_partname,
    part_countyname
) VALUES (
    1,
    5,
    'Jury',
    'Facebook',
    0.2,
    '2023-01-14',
    1001,
    2001,
    'Galway',
    '18-24',
    '2023-01-14',
    1,
    2023,
    4,
    1001,
    'John Doe',
    'Galway County'
);

```
Now do a select on the fact_data table and it should be present in both terminals <br>
Also describe keyspace to see details


``` sql
use c20355901;
select * from fact_data;
describe c20355901;
```

Then to do indexes use index.sql inside a cqlsh terminal.<br>
The data from query 1 is in ***tracing.txt*** and query 2 - ***tracing2.txt*** <br>
Indexing.pdf contains the speeds before and after and % speed increase.<br>
For the table with a collection datatype run ***collection_datatype.py*** or use ***collectionDatatype.sql*** in the terminal.
For the materialised view ***materialised_view.sql*** and run the commands within.





## Setup and populate CouchDB implementing replication and partitioning ##

1. &emsp; Create a partioned DB in the CouchDB interface.
2. &emsp; The file needed to populate the couch db is  **insert.py**
3. &emsp; It creates a partioned fact table with partions on County Name 'Cavan' and 'Galway' with a SK link to DIMVIEWER
4. &emsp; It creates a dim document for Viewer its linked to Fact doc with ViewerSK

``` json
"_id": "viewer:100594758472614011",
                "_rev": "1-0aef116355c197aab93534dcdec061f3",
                "type": "dim",
                "dim_data": {
                    "DIMVIEWER_SK": 100594758472614020,
                    "COUNTYNAME": "Cavan",
                    "AGE_GROUP_DESC": "18-24"
                }

                "_id": "galway:100594758472630808",
                "_rev": "1-4deda9665d3859b101601428433cc1a5",
                "type": "fact",
                "data": {
                    "VOTE": 4,
                    "VOTECATEGORY": "Audience",
                    "VOTEMODE": "Phone",
                    "VOTECOST": 1,
                    "VOTEDATE": "2016/01/03",
                    "DIMYEAR": 2016,
                    "DIMMONTH": 1,
                    "DIMDAYOFWEEK": 1,
                    "PARTSK": 100594758472613920,
                    "PARTNAME": "Anthony Jimenez",
                    "COUNTYNAME": "Galway",
                    "VIEWERSK": 100594758472615100
                }
```
           
                
## Implement master slave replication on this database. ##

1. &emsp; This is the ***replica.json*** file it has the selector to only get **fact** table of county 'Cavan' and **dim** tables of county 'Cavan'
```json
{
    "_id": "8221ed8a0318db0f38cd7dbd6c01611e",
    "user_ctx": {
      "name": "admin",
      "roles": ["_admin", "_reader", "_writer"]
    },
    "source": {
      "url": "http://localhost:5984/c20355901_milosz_lewandowski",
      "headers": {
        "Authorization": "Basic YWRtaW46Y291Y2hkYg=="
      }
    },
    "target": {
      "url": "http://localhost:5984/c20355901_replica",
      "headers": {
        "Authorization": "Basic YWRtaW46Y291Y2hkYg=="
      }
    },
    "create_target": true,
    "continuous": true,
    "create_target_params": {
      "partitioned": true
    },
    "owner": "admin",
    "selector": {
      "$or": [
        {"data.COUNTYNAME": "Cavan"},
        {"dim_data.COUNTYNAME": "Cavan"}
      ]
    }
  }
  ```

## Create a design document and view to execute a global query against this database to access data in both the fact and dimension documents ##

1. &emsp; **global_query.py** creates this global query to retrieve all document data ***both fact and dim data***
2. &emsp; Use the **globaldoc.json** to manually add and check
3. &emsp; Global Query http://admin:couchdb@127.0.0.1:5984/c20355901_milosz_lewandowski/_design/my_global_query/_view/global_view?include_docs=true


```json
{
  "_id": "_design/my_global_query",
  "language": "javascript",
  "options": {
    "partitioned": false
  },
  "views": {
    "global_view": {
      "map": "function(doc) { \r\n if (doc.type === 'fact') { emit(['fact', doc._id], doc); } else if (doc.type === 'dim') { emit(['dim', doc._id], doc); } }"
    }
  }
}
```

## Create a design document and view to execute a query against a partition to access data in one of the document types. ##

1. &emsp; View viewers over 50 query
2. &emsp; **partitionedDoc.json** holds the partioned document for viewer >50
3. &emsp; **partv2.json** has doc for diff partions of fact and dim giving jury for fact tables only and for viewer >50 users
4. &emsp; Execture in CouchDB UI and type "viewer" or "cavan" or "galway" to see diff partitioned queries.

*partionedDoc.json*
```json
{
    "_id": "_design/my_partitioned_query",
    "language": "javascript",
    "options": {
      "partitioned": true  
    },
    "views": {
      "view_over_50": {
        "map": "function(doc) { \r\n if ((doc.type === 'dim') && doc.dim_data.AGE_GROUP_DESC === '>50') { emit(doc._id, doc); } }"
      }
    }
  }
  
```

*partv2.json*
```json
{
    "_id": "_design/my_partitioned_query",
    "language": "javascript",
    "options": {
        "partitioned": true
    },
    "views": {
        "view_over_50": {
            "map": "function(doc) { \n if (doc.type === 'dim' && doc.dim_data.AGE_GROUP_DESC === '>50') { emit(doc._id, doc); } else if (doc.type === 'fact' && doc.data.VOTECATEGORY === 'Jury') { emit(doc._id, doc); } }"
        }
    }
}

```


### Cassandra Tasks ###

1. &emsp; Run *insert_data.py* It **creates the Keyspace** if not made and **inserts the data using the json file** *fact_data.json* which it makes also.
The data is partioned using countyname so 'Cavan' and 'Galway'
2. &emsp; Check -  **fact_data.csv** 

 *Code to make keyspace included in **insert file***
```py
# Create or use an existing keyspace
keyspace = "c20355901"
casssession.execute(f"CREATE KEYSPACE IF NOT EXISTS {keyspace} WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : 2 }}")
casssession.execute(f"USE {keyspace}")
```

*Table Structure in Cassandra Denormalised*
``` py
casssession.execute('DROP TABLE IF EXISTS fact_data;')
casssession.execute("""
    CREATE TABLE fact_data (
        factsk BIGINT,
        vote INT,
        votecategory TEXT,
        votemode TEXT,
        votecost DECIMAL,
        votedate DATE,
        partsk BIGINT,
        viewersk BIGINT,
        viewer_countyname TEXT,
        age_group_desc TEXT,
        dimdate DATE,
        dim_month INT,
        dim_year INT,
        dim_dayofweek INT,
        dimpartsk BIGINT,
        dim_partname TEXT,
        part_countyname TEXT,
        PRIMARY KEY (viewer_countyname, factsk)
    )
""")
```

### Comands for Index's ###

*Query 1 Index*

``` sql
# CSQL Terminal
docker exec -it cassandra1 bash -c  'cqlsh'

TRACING ON;

CAPTURE '/root/tracing.txt';

SELECT * FROM fact_data WHERE  age_group_desc = '>50' ALLOW FILTERING;

CREATE INDEX IF NOT EXISTS age_group_index ON fact_data (age_group_desc);

SELECT * FROM fact_data WHERE  age_group_desc = '>50' ALLOW FILTERING;

CAPTURE OFF;

TRACING OFF;

# Regular Terminal

docker cp cassandra1:/root/tracing.txt "C:\Users\milek\OneDrive -Technological University Dublin\Year-4\Advanced Databases\CA2\Cassandra\tracing1.txt"

```

*Query 2 Index*

``` sql

# CSQL Terminal

TRACING ON;

CAPTURE '/root/tracing2.txt';

SELECT * FROM fact_data WHERE  votemode = 'Facebook' ALLOW FILTERING;

CREATE INDEX IF NOT EXISTS vote_mode_index ON fact_data (votemode);

SELECT * FROM fact_data WHERE  votemode = 'Facebook' ALLOW FILTERING;

CAPTURE OFF;

TRACING OFF;

# Regular Terminal

docker cp cassandra1:/root/tracing2.txt "C:\Users\milek\OneDrive - Technological University Dublin\Year-4\Advanced Databases\CA2\Cassandra\tracing2.txt"
```



### Collection Datatype and Materialised View

*Create table of collection datatype*

``` sql
# CSQL Terminal

CREATE TABLE IF NOT EXISTS dogs (
dog_id UUID PRIMARY KEY,
dog_name TEXT,
toys MAP<TEXT, INT>
);

INSERT INTO dogs (dog_id, dog_name, toys) VALUES (uuid(), 'Luna', {'Ball': 2, 'Bone': 1, 'Soft Ball': 3});

INSERT INTO dogs (dog_id, dog_name, toys) VALUES (uuid(), 'Bobby', {'Ball': 5, 'Bone': 10, 'Soft Ball': 1});

SELECT dog_id, dog_name, toys['Ball'] FROM dogs;
```



*Materialized View*

``` sql
DROP TABLE dogs;

CREATE TABLE IF NOT EXISTS dogs (dog_id UUID PRIMARY KEY,dog_name TEXT,toys FROZEN<MAP<TEXT, INT>>);

INSERT INTO dogs (dog_id, dog_name, toys) VALUES (uuid(), 'Luna', {'Ball': 2, 'Bone': 1, 'Soft Ball': 3});

INSERT INTO dogs (dog_id, dog_name, toys) VALUES (uuid(), 'Bobby', {'Ball': 5, 'Bone': 10, 'Soft Ball': 1});

SELECT dog_id, dog_name, toys['Ball'] FROM dogs;


DROP MATERIALIZED VIEW IF EXISTS dog_material_view;

CREATE MATERIALIZED VIEW IF NOT EXISTS dog_material_view AS
SELECT
    dog_id,
    dog_name,
    toys
FROM dogs
WHERE dog_id IS NOT NULL AND toys IS NOT NULL
PRIMARY KEY ((dog_id), toys);

-- Query the materialized view
SELECT * FROM dog_material_view;
```
