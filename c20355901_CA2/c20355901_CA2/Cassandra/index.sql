-- Query 1
TRACING ON;

CAPTURE '/root/tracing.txt';

SELECT * FROM fact_data WHERE  age_group_desc = '>50' ALLOW FILTERING;

CREATE INDEX IF NOT EXISTS age_group_index ON fact_data (age_group_desc);

SELECT * FROM fact_data WHERE  age_group_desc = '>50' ALLOW FILTERING;

CAPTURE OFF;

TRACING OFF;


-- # Regular Terminal
docker cp cassandra1:/root/tracing.txt "C:\Users\milek\OneDrive -Technological University Dublin\Year-4\Advanced Databases\CA2\Cassandra\tracing1.txt"

-- Query 2

TRACING ON;

CAPTURE '/root/tracing2.txt';

SELECT * FROM fact_data WHERE  votemode = 'Facebook' ALLOW FILTERING;

CREATE INDEX IF NOT EXISTS vote_mode_index ON fact_data (votemode);

SELECT * FROM fact_data WHERE  votemode = 'Facebook' ALLOW FILTERING;

CAPTURE OFF;

TRACING OFF;

-- # Regular Terminal

docker cp cassandra1:/root/tracing2.txt "C:\Users\milek\OneDrive - Technological University Dublin\Year-4\Advanced Databases\CA2\Cassandra\tracing2.txt"
