pg_sequence_to_identity ( pg_sti ) is a tool to help you upgrade postgresql sequences to identity.
-

Roadmap:
* Support Downgrade ( Identity to Sequence )
* Support Limiters ( Upgrade by Regex/Glob/(White/Black)list )
* Support Inheritance / Multiple-Owners of a Sequence
* Support _the-usual_ arguments for db-centric tools like host/port/database ( environment-only atm )
* Ensure there are no sql-injections.

Requirements: psycopg2

Installation:

```
python3 setup.py install

```

```
usage: pg_sti [-h] [--list] [--sql] [--debug] method

positional arguments:
  method      UPGRADE Sequences to Identity, DOWNGRADE Identity to Sequences
              FIX to reset sequences to the current max +1

optional arguments:
  -h, --help  show this help message and exit
  --list      return affected columns and tables
  --sql       return sql-only
  --debug     increase output verbosity
```


Example UPGRADE:
---
```
PGDATABASE='somedatabase' pg_sti Upgrade
-- pgsti.seq_1.id
-- pgsti.seq 2.id _
-- pgsti.seq 2.idd
-- pgsti.seq_big.id
```

Example LIST:
---
```
PGDATABASE='somedatabase' pg_sti --list UPGRADE
id         pgsti.seq_1                       (Is_Identity NO )
id _       pgsti.seq 2                       (Is_Identity NO )
idd        pgsti.seq 2                       (Is_Identity NO )
id         pgsti.seq_big                     (Is_Identity NO )
Sequences with multiple owners not yet supported pgsti.seq_share_1_id_seq via pgsti.seq_share_1
Sequences with multiple owners not yet supported pgsti.seq_share_1_id_seq via pgsti.seq_share_2
```
Example SQL:
---
```
PGDATABASE='somedatabase' pg_sti --sql UPGRADE
-- pgsti.seq_big.id
------------------------------
-- CHANGING seq_big.id TO IDENTITY  --
------------------------------
BEGIN;
LOCK TABLE "pgsti"."seq_big" IN ACCESS EXCLUSIVE MODE;
alter table only "pgsti"."seq_big" alter COLUMN "id" set default null;
alter table only "pgsti"."seq_big" alter COLUMN "id" ADD GENERATED by default as identity ;
do
$F$
    declare
        new_max int;
        new_sequence text;
    begin
        select last_value+1 into new_max FROM pgsti.seq_big_id_seq ;
        SELECT pg_get_serial_sequence( '"pgsti"."seq_big"', 'id' ) into new_sequence;
        execute format('alter sequence %s RESTART %s', new_sequence, new_max) ;
    end
$F$;
DROP SEQUENCE pgsti.seq_big_id_seq ;
COMMIT;
...
```
