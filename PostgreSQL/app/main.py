import psycopg2
import os
from .models import (
    ADD_FOREIGN_KEY_CONSTRAINT,
    DELETE_BY_REF_ID,
    INSERT_DUPLICATE_USER,
    INSERT_INVALID_DATE_FORMAT,
    INSERT_INVALID_FOREIGN_KEY,
    INSERT_NAME,
    INVALID_JOIN_QUERY,
    REMOVE_FOREIGN_KEY_CONSTRAINT,
    SELECT_ALL_NAMES,
    DELETE_NAME_BY_ID,
    INSERT_DESCRIPTION,
    LEFT_JOIN_ON_ID,
    UPDATE_NAME_BY_ID,
    INNER_JOIN_ON_ID,
    RIGHT_JOIN_ON_ID,
    FULL_OUTER_JOIN_ON_ID,
)

DATABASE_URL = os.environ["DATABASE_URL"]


def connect():
    return psycopg2.connect(DATABASE_URL)


def remove_foreign_key_constraint():
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(REMOVE_FOREIGN_KEY_CONSTRAINT)
            conn.commit()


def add_foreign_key_constraint():
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(ADD_FOREIGN_KEY_CONSTRAINT)
            conn.commit()


def delete_another_example_by_ref_id(ref_id):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(DELETE_BY_REF_ID, (ref_id,))
            conn.commit()


def create_example(name):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(INSERT_NAME, (name,))
            id_of_new_row = cursor.fetchone()[0]
            conn.commit()
    return id_of_new_row


def list_examples():
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(SELECT_ALL_NAMES)
            result = cursor.fetchall()
    return result


def create_another_example(ref_id, description):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(INSERT_DESCRIPTION, (ref_id, description))
            conn.commit()


def get_left_join_on_id():
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(LEFT_JOIN_ON_ID)
            results = cursor.fetchall()
    return results


def update_example_by_id(id, new_name):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(UPDATE_NAME_BY_ID, (new_name, id))
            if cursor.rowcount == 0:
                raise Exception("Record not found")
            conn.commit()


def delete_example_by_id(id):
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(DELETE_BY_REF_ID, (id,))
            cursor.execute(DELETE_NAME_BY_ID, (id,))
            if cursor.rowcount == 0:
                raise Exception("Record not found")
            conn.commit()


def get_inner_join_on_id():
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(INNER_JOIN_ON_ID)
            results = cursor.fetchall()
    return results


def get_right_join_on_id():
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(RIGHT_JOIN_ON_ID)
            results = cursor.fetchall()
    return results


def get_full_outer_join_on_id():
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(FULL_OUTER_JOIN_ON_ID)
            results = cursor.fetchall()
    return results


def execute_invalid_join_query(conn):
    with conn.cursor() as cursor:
        cursor.execute(INVALID_JOIN_QUERY)
    conn.commit()


def insert_invalid_foreign_key(conn):
    with conn.cursor() as cursor:
        cursor.execute(INSERT_INVALID_FOREIGN_KEY)
    conn.commit()


def insert_invalid_date_format(conn):
    with conn.cursor() as cursor:
        cursor.execute(INSERT_INVALID_DATE_FORMAT)
    conn.commit()


def insert_duplicate_user(db_connection):
    cursor = db_connection.cursor()

    cursor.execute(
        "INSERT INTO users (username, email) VALUES ('testuser', 'test@email.com');"
    )

    cursor.execute(
        "INSERT INTO users (username, email) VALUES ('testuser', 'test2@email.com');"
    )
