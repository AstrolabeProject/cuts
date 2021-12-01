# Tests for the PostgreSQL base class.
#   Written by: Tom Hicks. 1/13/2021.
#   Last Modified: Update tests to not use jtest table.
#
import pytest

from cuts.blueprints.img.exceptions import ImageNotFound, RequestException, ServerError, NotYetImplemented
from cuts.blueprints.img.pg_sql_base import PostgreSQLBase
from tests import TEST_RESOURCES_DIR, TEST_DBCONFIG_FILEPATH


class TestPostgreSQLBase(object):

    test_args = {
        'debug': True,
        'dbconfig_file': TEST_DBCONFIG_FILEPATH
    }

    dbconfig_tstfyl = TEST_DBCONFIG_FILEPATH
    empty_dbconfig_tstfyl   = f"{TEST_RESOURCES_DIR}/test-dbconfig-empty.ini"
    noprops_dbconfig_tstfyl = f"{TEST_RESOURCES_DIR}/test-dbconfig-no-props.ini"
    nouri_dbconfig_tstfyl   = f"{TEST_RESOURCES_DIR}/test-dbconfig-no-uri.ini"
    nosuch_tstfyl           = f"{TEST_RESOURCES_DIR}/NOSUCHFILE"

    cleanid_emsg = "Identifier to be cleaned cannot be empty or None."


    base = PostgreSQLBase(test_args)        # instance of class under tests


    def test_load_sql_db_config_bad(self):
        with pytest.raises(ServerError, match='not found or not readable'):
            PostgreSQLBase.load_sql_db_config(self.nosuch_tstfyl)


    def test_load_sql_db_config_no_props(self):
        with pytest.raises(ServerError, match='no database parameters .* found'):
            PostgreSQLBase.load_sql_db_config(self.noprops_dbconfig_tstfyl)


    def test_load_sql_db_config_empty(self):
        with pytest.raises(ServerError, match='no database parameters .* found'):
            PostgreSQLBase.load_sql_db_config(self.empty_dbconfig_tstfyl)


    def test_load_sql_db_config_no_uri(self):
        with pytest.raises(ServerError, match='no database URI .* found'):
            PostgreSQLBase.load_sql_db_config(self.nouri_dbconfig_tstfyl)


    def test_load_sql_db_config(self):
        dbconf = PostgreSQLBase.load_sql_db_config(TEST_DBCONFIG_FILEPATH)
        print(dbconf)
        assert dbconf is not None
        assert len(dbconf) >= 7               # specific to this test file



    def test_clean_id_badargs(self):
        with pytest.raises(ServerError, match=self.cleanid_emsg):
            self.base.clean_id(None)

        with pytest.raises(ServerError, match=self.cleanid_emsg):
            self.base.clean_id('')

        with pytest.raises(ServerError, match=self.cleanid_emsg):
            self.base.clean_id('', '')


    def test_clean_id(self):
        assert self.base.clean_id('abc') == 'abc'
        assert self.base.clean_id('_') == '_'
        assert self.base.clean_id('a') == 'a'
        assert self.base.clean_id('_a_') == '_a_'
        assert self.base.clean_id('_ABC_') == '_ABC_'
        assert self.base.clean_id('A_B_C') == 'A_B_C'
        assert self.base.clean_id('abc_') == 'abc_'
        assert self.base.clean_id('ABCxyz') == 'ABCxyz'
        assert self.base.clean_id('coll22') == 'coll22'


    def test_clean_id_remove(self):
        assert self.base.clean_id('ABC xyz') == 'ABCxyz'
        assert self.base.clean_id('*ABC;xyz') == 'ABCxyz'
        assert self.base.clean_id('*ABC;xyz') == 'ABCxyz'
        assert self.base.clean_id('Robert;drop all tables;') == 'Robertdropalltables'


    def test_clean_id_allow(self):
        letvec = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
        assert self.base.clean_id('ABC xyz', letvec) == ''
        assert self.base.clean_id('xyz; ABC', letvec) == ''
        assert self.base.clean_id('abc xyz', letvec) == 'abc'
        assert self.base.clean_id('XYZ; abc', letvec) == 'abc'
        assert self.base.clean_id('Robert;drop all tables;', letvec) == 'bedaabe'



    def test_execute_sql(self):
        self.base.execute_sql('SELECT (%s)', [1])


    def test_fetch_row(self):
        row = self.base.fetch_row('SELECT id, obs_creator_name from sia.jwst where id = (%s)', [1])
        assert row is not None
        assert row != []
        assert row[0] == 1
        assert row[1] == 'JWST'



    def test_fetch_rows(self):
        rows = self.base.fetch_rows('SELECT id, obs_creator_name from sia.jwst where obs_collection = (%s)', ['XTRAS'])
        assert rows is not None
        assert rows != []
        assert len(rows) == 2
        assert len(rows[0]) == 2
        assert rows[0][1] == 'JWST'



    def test_fetch_rows_2dicts(self):
        rows = self.base.fetch_rows_2dicts('SELECT id, obs_creator_name from sia.jwst where obs_collection = (%s)', ['XTRAS'])
        assert rows is not None
        assert rows != []
        assert len(rows) == 2
        assert rows[0] != {}
        assert 'id' in rows[0]
        assert 'obs_creator_name' in rows[0]
        assert rows[0].get('obs_creator_name') == 'JWST'


    def test_sql4_selected_fields(self):
        assert self.base.sql4_selected_fields() == '*'
        assert self.base.sql4_selected_fields([]) == ''
        assert self.base.sql4_selected_fields(['a', 'b', 'c']) == 'a,b,c'
