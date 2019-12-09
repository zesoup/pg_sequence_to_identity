import os
import pytest
import psycopg2

from pg_sequence_to_identity.pg_sti import get_connection

def _insert_in_all():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO pgsti.seq_1 ( payload ) SELECT 'XX' from generate_series(1,100) ")
        cursor.execute(
            """INSERT INTO pgsti."seq 2" ( payload ) SELECT 'XX' from generate_series(1,100) """)
        cursor.execute(
            "INSERT INTO pgsti.seq_big ( payload ) SELECT 'XX' from generate_series(1,100) ")
        cursor.execute(
            "INSERT INTO pgsti.seq_identity ( payload ) SELECT 'XX' from generate_series(1,100) ")
        cursor.execute(
            "INSERT INTO pgsti.seq_identity_big ( payload ) SELECT 'XX' from generate_series(1,100) ")
        cursor.execute(
            "INSERT INTO pgsti.seq_share_1 ( payload ) SELECT 'XX' from generate_series(1,100) ")
        cursor.execute(
            "INSERT INTO pgsti.seq_share_2 ( payload ) SELECT 'XX' from generate_series(1,100) ")
        connection.commit()

def setup_schema(connection):
    with connection.cursor() as cursor:
        try:
            cursor.execute("DROP SCHEMA pgsti cascade")
        except:
            pass
        finally:
            connection.commit()
        cursor.execute("CREATE SCHEMA pgsti")
        cursor.execute(
            "CREATE TABLE pgsti.seq_1 ( id serial primary key, payload text )")
        cursor.execute(
            """CREATE TABLE pgsti."seq 2" ( "id _" serial primary key, idd serial, payload text )""")
        cursor.execute(
            "CREATE TABLE pgsti.seq_big ( id bigserial primary key, payload text )")
        cursor.execute(
            "CREATE TABLE pgsti.seq_identity ( id int generated always as identity primary key, payload text )")
        cursor.execute(
            "CREATE TABLE pgsti.seq_identity_big ( id bigint generated always as identity primary key, payload text )")

        cursor.execute(
            "CREATE TABLE pgsti.seq_share_1 ( id bigserial primary key, payload text )")
        cursor.execute(
            "CREATE TABLE pgsti.seq_share_2 ( id bigint    primary key, payload text )")
        cursor.execute(
            "ALTER TABLE pgsti.seq_share_2 ALTER COLUMN id set default nextval('pgsti.seq_share_1_id_seq'::regclass)")

        connection.commit()
        _insert_in_all( )



@pytest.fixture(scope='session')
def env():
    conn = get_connection()
    setup_schema(conn)
    conn.commit()
    conn.close()
