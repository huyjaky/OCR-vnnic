import pyodbc
import uuid
from dotenv import load_dotenv
from querys.preprocessing import (
    preprocessing_ben_giao,
    preprocessing_ben_nhan,
    preprocessing_ho_so,
)

load_dotenv()
import os


def connect_to_db():
    """
    Connect to the SQL Server database and return the connection object.
    """
    # try:
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={str(os.getenv('DTB_SERVER'))};"
        f"DATABASE={str(os.getenv('DTB_NAME'))};"
        f"UID={str(os.getenv('DTB_UID'))};"
        f"PWD={str(os.getenv('DTB_PWD'))};",
        autocommit=True,
    )
    print("Connection successful")
    return conn
    # except Exception as e:
    #     print(f"Error connecting to database: {e}")
    #     return None


def insert_multiple_records(conn, table_name: str, data_list: list[dict]):
    """
    Insert multiple records into the database.
    :param conn: Database connection object.
    :param records: List of tuples containing the records to insert.
    :param table_name: Name of the table to insert records into.
    :param columns: List of column names corresponding to the records.
    """
    cursor = conn.cursor()
    # try:

    columns = ", ".join(data_list[0].keys())  # pyright:ignore
    placeholders = ", ".join(["?" for _ in data_list[0]])

    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    cursor.executemany(sql, [tuple(record.values()) for record in data_list])

    print(f"{cursor.rowcount} records inserted successfully.")

    # except Exception as e:
    #     print(f"Error inserting records: {e}")
    # finally:
    cursor.close()


def insert_single_record(conn, table_name: str, data: dict):
    """
    Insert a single record into the database.
    :param conn: Database connection object.
    :param data: Dictionary containing the record to insert.
    :param table_name: Name of the table to insert the record into.
    """
    cursor = conn.cursor()
    # try:
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data])
    values = list(data.values())

    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    cursor.execute(sql, values)
    conn.commit()

    print("Record inserted successfully.")
    # except Exception as e:
    #     print(f"Error inserting record: {e}")
    # finally:
    cursor.close()


def insert_records_from_json(json_input):
    """
    Insert records into the database from a JSON input.
    :param json_input: JSON object containing the data to insert.
    """
    ho_so_id = uuid.uuid4()

    ho_so = preprocessing_ho_so(ho_so=json_input, ho_so_id=ho_so_id)
    ben_giao = preprocessing_ben_giao(ben_giao=json_input["BenGiao"], ho_so_id=ho_so_id)
    ben_nhan = preprocessing_ben_nhan(ben_nhan=json_input["BenNhan"], ho_so_id=ho_so_id)

    conn = connect_to_db()
    insert_single_record(conn=conn, table_name="HoSoTemp", data=ho_so)

    if len(json_input["BenGiao"]) != 0:
        insert_multiple_records(conn=conn, table_name="BenGiaoTemp", data_list=ben_giao)

    if len(json_input["BenNhan"]) != 0:
        insert_multiple_records(conn=conn, table_name="BenNhanTemp", data_list=ben_nhan)


if __name__ == "__main__":
    from test_data import data
    from preprocessing import (
        preprocessing_ben_giao,
        preprocessing_ben_nhan,
        preprocessing_ho_so,
    )

    json_input = data
    ho_so_id = uuid.uuid4()
    ho_so = preprocessing_ho_so(ho_so=json_input, ho_so_id=ho_so_id)
    ben_giao = preprocessing_ben_giao(ben_giao=json_input["BenGiao"], ho_so_id=ho_so_id)
    ben_nhan = preprocessing_ben_nhan(ben_nhan=json_input["BenNhan"], ho_so_id=ho_so_id)
    conn = connect_to_db()
    insert_single_record(conn=conn, table_name="HoSoTemp", data=ho_so)
    insert_multiple_records(conn=conn, table_name="BenGiaoTemp", data_list=ben_giao)
    insert_multiple_records(conn=conn, table_name="BenNhanTemp", data_list=ben_nhan)
