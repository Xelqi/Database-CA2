-- Materialized View

-- Drop the old table and create one with Frozen Map
-- Cassandra will store the collection as entire collection as a single, serialized
-- value. This is required for a materialized view involving a collection type column

DROP TABLE dogs;

CREATE TABLE IF NOT EXISTS dogs (dog_id UUID PRIMARY KEY,dog_name TEXT,toys FROZEN<MAP<TEXT, INT>>);

INSERT INTO dogs (dog_id, dog_name, toys) VALUES (uuid(), 'Luna', {'Ball': 2, 'Bone': 1, 'Soft Ball': 3});

INSERT INTO dogs (dog_id, dog_name, toys) VALUES (uuid(), 'Bobby', {'Ball': 5, 'Bone': 10, 'Soft Ball': 1});

SELECT dog_id, dog_name, toys['Ball'] FROM dogs;

-- Create the materialized view

DROP MATERIALIZED VIEW IF EXISTS dog_material_view;

-- Create a materialized view taking data from dogs specified in the select
-- Making sure dog_id and toys contains no nulls
-- Dog ID and toys being a primary key ensures they are unique and helps with efficent retrieval
-- Including toys as a Primary key ensures uniqueness based on dog and toy combinations

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
SELECT dogs['Ball'] from dog_material_view;

