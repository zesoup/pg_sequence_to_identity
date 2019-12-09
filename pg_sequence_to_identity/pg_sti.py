import argparse
import psycopg2
import psycopg2.extras
import sys

def get_connection():
    return psycopg2.connect("")


def is_alive():
    con = psycopg2.connect("")
    curs = con.cursor()
    curs.execute("SELECT 1")
    return curs.fetchone()


def _get_affected_text(with_sequences=True, with_identity=False):
    for row in _get_affected(with_sequences, with_identity):
        yield '%-10s %-32s  (Is_Identity %-3s)' % (row['column'], "%s.%s"%(row['schema'], row['table']), row['is_identity'])


def _get_affected(with_sequences=True, with_identity=False):
    connection = get_connection()
    with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
        curs.execute('''
        select  table_schema    as schema,
                table_name      as table, 
                column_name     as column, 
                is_identity     as is_identity,
                substring(column_default,10, length(column_default)-12-9) as column_default 
            FROM information_schema.columns 
                WHERE ( is_identity = 'YES'  and %s )
                OR    ( column_default LIKE 'nextval(%%::regclass)' AND %s );''' % ('True' if with_identity else 'False', 'True' if with_sequences else 'False'))
        entries = []
        for row in curs.fetchall():
            entries.append(row)
        for outer in entries:
            is_valid = True
            for inner in entries:
                if outer['is_identity'] == 'NO' and inner['column_default'] == outer['column_default'] and (
                        inner['schema'] != outer['schema'] or inner['table'] != outer['table'] or inner['column'] != outer['column']):
                        print("Sequences with multiple owners not yet supported %s via %s.%s"%( outer['column_default'], outer['schema'],outer['table'] ), file=sys.stderr)
                        is_valid = False
                        break
            if is_valid:
                yield outer


def _migrate_to_identity(schema, table, column, sql_only=False):
    connection = get_connection()
    connection.set_session(autocommit=False)
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def print_if_sql_only(SQL):
        if sql_only:
            print(SQL)

    def exec_if_not_sql_only(SQL):
        if not sql_only:
            cursor.execute(SQL)
            try:
                return cursor.fetchall()
            except Exception as e:
                # print(e)
                return None

    # BEGIN TX // actually done implicitly with psycopg
    print_if_sql_only('------------------------------')
    print_if_sql_only('-- CHANGING %s.%s TO IDENTITY  --' % (table, column))
    print_if_sql_only('------------------------------')
    print_if_sql_only('BEGIN;')

    # LOCK TABLE IN ACCESS EXCLUSIVE MODE
    SQL = 'LOCK TABLE "%s"."%s" IN ACCESS EXCLUSIVE MODE;' % (schema, table)
    print_if_sql_only(SQL)
    exec_if_not_sql_only(SQL)

    SQL = """ 
    SELECT a.attname,
    pg_catalog.format_type(a.atttypid, a.atttypmod),
    (SELECT substring(pg_catalog.pg_get_expr(d.adbin, d.adrelid) for 128) default_value
        FROM pg_catalog.pg_attrdef d
        WHERE d.adrelid = a.attrelid AND d.adnum = a.attnum AND a.atthasdef)
    FROM pg_catalog.pg_attribute a
    WHERE a.attrelid = '"%s"."%s"'::regclass::oid AND a.attnum > 0 AND NOT a.attisdropped
    and attname = '%s'
    ORDER BY a.attnum;
    """ % (schema, table, column)
    cursor.execute(SQL)
    seqname = cursor.fetchone()['default_value']
    seqname = seqname[9:-12]  # There should be a prettier way

    # AQUIRE CURRENT COUNTER FOR SEQUENCE
    # DELETE DEFAULT
    SQL = '''alter table only "%s"."%s" alter COLUMN "%s" set default null;''' % (
        schema, table, column)
    print_if_sql_only(SQL)
    exec_if_not_sql_only(SQL)

    # ADD IDENTITY
    SQL = '''alter table only "%s"."%s" alter COLUMN "%s" ADD GENERATED by default as identity ;''' % (
        schema, table, column)
    print_if_sql_only(SQL)
    exec_if_not_sql_only(SQL)

    # UPDATE IDENTITY TO LAST KNOWN VALUE
    #"SELECT last_value FROM %s"%( seqname )
    SQL = """do
$F$
    declare
        new_max int;
        new_sequence text;
    begin
        select last_value+1 into new_max FROM %s ;
        SELECT pg_get_serial_sequence( '"%s"."%s"', '%s' ) into new_sequence;
        DROP SEQUENCE %s;
        -- It seems wise to keep the last counter of the sequence. For this reason we're logging out to
        -- postgresql's logfile.

        RAISE LOG 'Sequence %s.%s.%s is being migrated to Identity. The old value was %s ', new_max ;
        execute format('alter sequence %s RESTART %s', new_sequence, new_max) ;
    end
$F$;""" % (seqname,
           schema, table, column,
           seqname,
           schema, table, column, '%',
           '%s', '%s')

    print_if_sql_only(SQL)
    exec_if_not_sql_only(SQL)


    if not sql_only:
        connection.commit()
    else:
        print_if_sql_only('COMMIT;')
        connection.rollback()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "method", help="UPGRADE Sequences to Identity, DOWNGRADE Identity to Sequences")
    parser.add_argument("--list", action="store_true",
                        help="return affected columns and tables")
    parser.add_argument("--sql", action="store_true", default=False,
                        help="return sql-only")
    parser.add_argument("--debug",  action="store_true",
                        help="increase output verbosity")
    args = parser.parse_args()
    if args.method.lower() == 'upgrade':
        if args.list:
            for line in _get_affected_text(with_sequences=True, with_identity=False):
                print(line)
        else:
            for x in _get_affected(with_sequences=True, with_identity=False):
                print("-- %s.%s.%s" %
                      (x['schema'], x['table'], x['column']))
                _migrate_to_identity(
                    x['schema'], x['table'], x['column'], sql_only=args.sql)

    elif args.method.lower() == 'downgrade':
        print("TODO")
        sys.exit(1)
    else:
        print("Unsupported Method")
        sys.exit(1)
    return


if __name__ == '__main__':
    main()
