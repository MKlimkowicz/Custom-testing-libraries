CREATE TABLE example (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);


CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100),
);


CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id), 
    amount NUMERIC
);

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_date DATE,
    event_name VARCHAR(100)
);


ALTER TABLE users ADD CONSTRAINT unique_name UNIQUE(username);
