import pg_sti
from tests.conftest import _insert_in_all

def test_get_aliveness_and_reset(env):
    """ Simple Ping tzo ensure the DB is reachable via conftest.py settings."""
    assert pg_sti.is_alive()

def test_listing(env):
    """ Testcase is currently defined to contain 6 - relevant Columns"""
    assert len([x for x in pg_sti._print_affected(with_sequences=True,  with_identity=True )]) == 6
    assert len([x for x in pg_sti._print_affected(with_sequences=True,  with_identity=False)]) == 4
    assert len([x for x in pg_sti._print_affected(with_sequences=False, with_identity=True )]) == 2
    

def test_upgrade(env):
    """ 
    """
    for i, x in enumerate(pg_sti._get_affected(with_sequences=True, with_identity=False)):
        pg_sti._migrate_to_identity(x['schema'], x['table'], x['column'], sql_only=True)
        pg_sti._migrate_to_identity(x['schema'], x['table'], x['column'], sql_only=False)
    assert i <= 3  # There are exactly 4 NonSequences
    _insert_in_all()  # Won't work if we forgot to update the sequence-counter or remove the old sequence
    assert len([x for x in pg_sti._print_affected(with_sequences=True, with_identity=False)]) == 0
    assert len([x for x in pg_sti._print_affected(with_sequences=False,  with_identity=True )]) == 6


