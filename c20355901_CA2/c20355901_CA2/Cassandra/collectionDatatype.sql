-- Creating a table including collection datatype
-- CSQL Terminal


CREATE TABLE IF NOT EXISTS dogs (
dog_id UUID PRIMARY KEY,
dog_name TEXT,
toys MAP<TEXT, INT>
);


INSERT INTO dogs (dog_id, dog_name, toys) VALUES (uuid(), 'Luna', {'Ball': 2, 'Bone': 1, 'Soft Ball': 3});

INSERT INTO dogs (dog_id, dog_name, toys) VALUES (uuid(), 'Bobby', {'Ball': 5, 'Bone': 10, 'Soft Ball': 1});

DESCRIBE dogs;

SELECT dog_id, dog_name, toys['Ball'] FROM dogs;

