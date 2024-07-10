from cassandra.cluster import Cluster
import uuid

# Function to safely execute Cassandra operations
def execute_cassandra_operations():
    # Connect to Cassandra
    casscluster = Cluster(['localhost'], port=9042)
    casssession = casscluster.connect('c20355901')  # Replace with your desired keyspace

    try:
        # Drop the dogs table if it exists
        casssession.execute("DROP TABLE IF EXISTS dogs;")

        # Create a table for dogs with a collection datatype (toys)
        casssession.execute("""
            CREATE TABLE dogs (
                dog_id UUID PRIMARY KEY,
                dog_name TEXT,
                toys MAP<TEXT, INT>
            )
        """)

        # Prepare data to be inserted into the dogs table
        data_to_insert = [
            (uuid.uuid4(), 'Luna', {'Ball': 2, 'Bone': 1, 'Soft Ball': 3}),
            (uuid.uuid4(), 'Bobby', {'Ball': 5, 'Bone': 10, 'Soft Ball': 1}),
            # Add more data as needed
        ]

        # Prepare an INSERT statement with placeholders for the data
        insert_query = casssession.prepare("""
            INSERT INTO dogs (dog_id, dog_name, toys)
            VALUES (?, ?, ?)
        """)

        # Execute the insert statement for each item in the data list
        for item in data_to_insert:
            casssession.execute(insert_query, item)

        # Query the dogs table to retrieve and print the data
        rows = casssession.execute("SELECT dog_id, dog_name, toys['Ball'] FROM dogs;")
        for row in rows:
            print(row)

        # Additional code for other operations can be added here

    finally:
        # Ensure the Cassandra session and cluster are closed properly
        casssession.shutdown()
        casscluster.shutdown()

# Execute the Cassandra operations
execute_cassandra_operations()