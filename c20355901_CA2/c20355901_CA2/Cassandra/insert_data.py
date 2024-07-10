import mariadb
import json
import collections
import cassandra
from cassandra.cluster import Cluster
import time
import decimal
import datetime

# Function to handle Decimal and Date types in JSON serialization
def default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

# Connect to MariaDB
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "mariadb",
    "database": "MusicDimDB"
}
conn = mariadb.connect(**db_config)
cursor = conn.cursor()

# Retrieve data from FACT, DIMDATE, DIMPART, and DIMVIEWER tables
fact_query = """
    SELECT
        f.FACTSK,
        f.VOTE,
        f.VOTECATEGORY,
        f.VOTEMODE,
        f.VOTECOST,
        f.VOTEDATE,
        f.PARTSK,
        f.VIEWERSK,
        v.COUNTYNAME AS VIEWER_COUNTYNAME,
        v.AGE_GROUP_DESC,
        d.DIMDATE,
        d.DIMMONTH AS DIM_MONTH,
        d.DIMYEAR AS DIM_YEAR,
        d.DIMDAYOFWEEK,
        p.DIMPARTSK,
        p.PARTNAME AS DIM_PARTNAME,
        p.COUNTYNAME AS PART_COUNTYNAME
    FROM FACT f
    JOIN DIMDATE d ON f.VOTEDATE = d.DIMDATE
    JOIN DIMPART p ON f.PARTSK = p.DIMPARTSK
    JOIN DIMVIEWER v ON f.VIEWERSK = v.DIMVIEWERSK
    WHERE v.COUNTYNAME IN ('Cavan', 'Galway');
"""
cursor.execute(fact_query)
fact_data = cursor.fetchall()

# Dump the data to a JSON file
objects_list = []
for row in fact_data:
    d = collections.OrderedDict()
    d["factsk"] = row[0]
    d["vote"] = row[1]
    d["votecategory"] = row[2]
    d["votemode"] = row[3]
    d["votecost"] = row[4]
    d["votedate"] = row[5]
    d["partsk"] = row[6]
    d["viewersk"] = row[7]
    d["viewer_countyname"] = row[8]
    d["age_group_desc"] = row[9]
    d["dimdate"] = row[10]
    d["dim_month"] = row[11]
    d["dim_year"] = row[12]
    d["dim_dayofweek"] = row[13]
    d["dimpartsk"] = row[14]
    d["dim_partname"] = row[15]
    d["part_countyname"] = row[16]
    objects_list.append(d)

# Use the 'default' function in json.dumps
j = json.dumps(objects_list, default=default)
with open("fact_data.json", "w") as f:
    f.write(j)

# Close connection to MariaDB
conn.close()

# Connect to Cassandra
casscluster = Cluster(['localhost'], port=9042)
casssession = casscluster.connect('c20355901')

# Create or use an existing keyspace
keyspace = "c20355901"
casssession.execute(f"CREATE KEYSPACE IF NOT EXISTS {keyspace} WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : 2 }}")
casssession.execute(f"USE {keyspace}")

# Create a table in Cassandra
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

# Insert data into Cassandra using a prepared statement
query = casssession.prepare("""
    INSERT INTO fact_data (
        factsk, vote, votecategory, votemode, votecost,
        votedate, partsk, viewersk, viewer_countyname, age_group_desc,
        dimdate, dim_month, dim_year, dim_dayofweek, dimpartsk,
        dim_partname, part_countyname
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""")
print("Inserting data into Cassandra - please wait")
with open("fact_data.json") as data_file:
    data = json.load(data_file)
    for v in data:
        casssession.execute(
            query,
            [
                v['factsk'], v['vote'], v['votecategory'], v['votemode'],
                v['votecost'], v['votedate'], v['partsk'], v['viewersk'],
                v['viewer_countyname'], v['age_group_desc'], v['dimdate'],
                v['dim_month'], v['dim_year'], v['dim_dayofweek'],
                v['dimpartsk'], v['dim_partname'], v['part_countyname']
            ]
        )

print("Waiting for 1 min to ensure data submitted...")
time.sleep(60)

# Verify data insertion
print("Here is the data....")
rows = casssession.execute("SELECT * FROM fact_data;")
for row in rows:
    print(row)
