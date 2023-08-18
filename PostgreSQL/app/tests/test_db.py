import os
import psycopg2
import pytest
from app.main import (
    create_another_example,
    create_example,
    update_example_by_id,
    list_examples,
    delete_example_by_id,
    get_full_outer_join_on_id,
    get_left_join_on_id,
    get_right_join_on_id,
    get_inner_join_on_id,
    add_foreign_key_constraint,
    remove_foreign_key_constraint,
    delete_another_example_by_ref_id,
    execute_invalid_join_query,
    insert_invalid_foreign_key,
    insert_invalid_date_format,
    insert_duplicate_user,
)
from app.models import (
    CREATE_ANOTHER_TABLE,
    CREATE_TABLE,
    CREATE_TABLE_EVENTS,
    CREATE_TABLE_USERS,
    CREATE_TABLE_ORDERS,
)

DATABASE_URL = os.environ["DATABASE_URL"]


@pytest.fixture(scope="module")
def db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE)
    cursor.execute(CREATE_ANOTHER_TABLE)
    cursor.execute(CREATE_TABLE_USERS)
    cursor.execute(CREATE_TABLE_ORDERS)
    cursor.execute(CREATE_TABLE_EVENTS)
    conn.commit()

    yield conn

    cursor.execute("DROP TABLE IF EXISTS another_example;")
    cursor.execute("DROP TABLE IF EXISTS example;")
    conn.commit()
    conn.close()


@pytest.fixture(autouse=True)
def run_around_tests(db_connection):
    trans = db_connection.cursor()

    yield

    db_connection.rollback()
    trans.close()


class TestBasicDatabaseOperations:
    @pytest.mark.parametrize("name", ["Alice", 123, 45.67, "2023-08-15"])
    def test_insert_and_select(self, name, db_connection):
        id = create_example(str(name))
        assert id > 0
        results = list_examples()
        names = [row[1] for row in results]
        assert str(name) in names

    def test_update(self, db_connection):
        name = "Dennis"
        id = create_example(name)
        updated_name = "UpdatedDennis"
        update_example_by_id(id, updated_name)
        results = list_examples()
        names = [row[1] for row in results]
        assert updated_name in names
        assert name not in names

    def test_delete(self, db_connection):
        name = "Charlie"
        id = create_example(name)
        delete_example_by_id(id)
        results = list_examples()
        names = [row[1] for row in results]
        assert name not in names


class TestJoinOperations:
    @pytest.mark.parametrize(
        "description", ["Description for Bob", 123, 45.67, "2023-08-15"]
    )
    def test_left_join(self, description, db_connection):
        id = create_example("Bob")
        create_another_example(id, str(description))
        results = get_left_join_on_id()
        descriptions = [row[1] for row in results if row[0] == "Bob"]
        assert str(description) in descriptions

    def test_inner_join(self, db_connection):
        name = "Grace"
        id = create_example(name)

        description = "Description for Grace"
        create_another_example(id, description)

        results = get_inner_join_on_id()
        descriptions = [row[1] for row in results if row[0] == name]
        assert description in descriptions

    def test_right_join(self, db_connection):
        name = "Hannah"
        id = create_example(name)

        description_for_hannah = "Description for Hannah"
        create_another_example(id, description_for_hannah)

        temp_name = "Temp Name"
        temp_id = create_example(temp_name)

        remove_foreign_key_constraint()

        non_existent_ref_id = 99999
        temp_description = "Description for non-existent ref"
        create_another_example(non_existent_ref_id, temp_description)

        results = get_right_join_on_id()

        assert any(row[0] is None and row[1] == temp_description for row in results)

        delete_another_example_by_ref_id(non_existent_ref_id)

        add_foreign_key_constraint()

    def test_full_outer_join(self, db_connection):
        name_1 = "Irene"
        id_1 = create_example(name_1)

        name_2 = "Jack"
        id_2 = create_example(name_2)

        description = "Description for Jack"
        create_another_example(id_2, description)

        results = get_full_outer_join_on_id()
        descriptions_1 = [row[1] for row in results if row[0] == name_1]
        descriptions_2 = [row[1] for row in results if row[0] == name_2]

        assert descriptions_1[0] is None
        assert description in descriptions_2


class TestCRUDOperationsForAnotherExample:
    @pytest.mark.parametrize(
        "description", ["Description for Eve", 123, 45.67, "2023-08-15"]
    )
    def test_insert_description(self, description, db_connection):
        name = "Eve"
        id = create_example(name)
        create_another_example(id, str(description))
        results = get_left_join_on_id()
        descriptions = [row[1] for row in results if row[0] == name]
        assert str(description) in descriptions

    def test_delete_description(self, db_connection):
        name = "Frank"
        id = create_example(name)

        description = "Description for Frank"
        create_another_example(id, description)

        delete_example_by_id(id)

        results = get_left_join_on_id()
        descriptions = [row[1] for row in results if row[0] == name]
        assert description not in descriptions


class TestErrorCases:
    @pytest.mark.parametrize(
        "non_existent_id, new_name",
        [(99999, "UpdatedName"), (88888, "AnotherUpdatedName")],
    )
    def test_update_non_existent_record(self, non_existent_id, new_name, db_connection):
        with pytest.raises(Exception) as excinfo:
            update_example_by_id(non_existent_id, new_name)
        assert "Record not found" in str(excinfo.value)

    @pytest.mark.parametrize("non_existent_id", [99999, 88888])
    def test_delete_non_existent_record(self, non_existent_id, db_connection):
        with pytest.raises(Exception) as excinfo:
            delete_example_by_id(non_existent_id)
        assert "Record not found" in str(excinfo.value)


class TestErrorQueries:
    @pytest.mark.parametrize(
        "function, expected_error_message, expected_exception",
        [
            (
                execute_invalid_join_query,
                "column users.nonexistent_column does not exist",
                psycopg2.Error,
            ),
            (
                insert_invalid_foreign_key,
                "violates foreign key constraint",
                psycopg2.IntegrityError,
            ),
            (
                insert_invalid_date_format,
                "invalid input syntax for type date",
                psycopg2.DataError,
            ),
            (
                insert_duplicate_user,
                "duplicate key value violates unique constraint",
                psycopg2.IntegrityError,
            ),
        ],
    )
    def test_error_queries(
        self, function, expected_error_message, expected_exception, db_connection
    ):
        with pytest.raises(expected_exception) as excinfo:
            function(db_connection)
        print(str(excinfo.value))
        assert expected_error_message in str(excinfo.value)
