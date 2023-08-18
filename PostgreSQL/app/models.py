CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS example (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);
"""
CREATE_TABLE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100)
);
"""
CREATE_TABLE_ORDERS = """
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount NUMERIC
);
"""
CREATE_TABLE_EVENTS = """
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    event_date DATE,
    event_name VARCHAR(100)
);
"""
INSERT_NAME = "INSERT INTO example (name) VALUES (%s) RETURNING id;"

SELECT_ALL_NAMES = "SELECT * FROM example ORDER BY name;"

DELETE_NAME_BY_ID = "DELETE FROM example WHERE id = %s;"

DELETE_BY_REF_ID = "DELETE FROM another_example WHERE ref_id = %s;"

CREATE_ANOTHER_TABLE = """
CREATE TABLE IF NOT EXISTS another_example (
    ref_id INT REFERENCES example(id) ON DELETE SET NULL,
    description TEXT
);
"""

INSERT_DESCRIPTION = "INSERT INTO another_example (ref_id, description) VALUES (%s, %s) RETURNING ref_id;"

LEFT_JOIN_ON_ID = """
SELECT example.name, another_example.description
FROM example
LEFT JOIN another_example ON example.id = another_example.ref_id;
"""
UPDATE_NAME_BY_ID = "UPDATE example SET name = %s WHERE id = %s;"

INNER_JOIN_ON_ID = """
SELECT example.name, another_example.description
FROM example
INNER JOIN another_example ON example.id = another_example.ref_id;
"""

RIGHT_JOIN_ON_ID = """
SELECT example.name, another_example.description
FROM example
RIGHT JOIN another_example ON example.id = another_example.ref_id;
"""

FULL_OUTER_JOIN_ON_ID = """
SELECT example.name, another_example.description
FROM example
FULL OUTER JOIN another_example ON example.id = another_example.ref_id;
"""

ADD_FOREIGN_KEY_CONSTRAINT = """
                ALTER TABLE another_example 
                ADD CONSTRAINT another_example_ref_id_fkey 
                FOREIGN KEY (ref_id) REFERENCES example(id);
                """

REMOVE_FOREIGN_KEY_CONSTRAINT = (
    "ALTER TABLE another_example DROP CONSTRAINT another_example_ref_id_fkey;"
)

INVALID_JOIN_QUERY = (
    "SELECT * FROM users INNER JOIN orders ON users.nonexistent_column = orders.user_id"
)
INSERT_INVALID_FOREIGN_KEY = "INSERT INTO orders VALUES (4, 5, 200.5);"
INSERT_INVALID_DATE_FORMAT = "INSERT INTO events (event_date, event_name) VALUES ('invalid-date-format', 'Launch');"
INSERT_DUPLICATE_USER = "INSERT INTO users (name) VALUES ('duplicate_name')"
