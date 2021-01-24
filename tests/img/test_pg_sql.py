# Tests for the PostgreSQL manager class.
#   Written by: Tom Hicks. 1/13/2021.
#   Last Modified: Use sia_table_size as minimum only.
#
import pytest

from cuts.blueprints.img.exceptions import ImageNotFound, RequestException, ServerError, NotYetImplemented
from cuts.blueprints.img.pg_sql import PostgreSQLManager
from tests import TEST_RESOURCES_DIR, TEST_DBCONFIG_FILEPATH


class TestPostgreSQLManager(object):

    bad_path = '/bad/path'
    m13_path = '/vos/images/XTRAS/m13.fits'
    dc19_path = '/vos/images/DC19/F090W.fits'
    dc20_path = '/vos/images/DC20/F356W.fits'
    jades_path = '/vos/images/JADES/goods_s_F277W_2018_08_29.fits'
    irods_path = '/iplant/fake/nosuchfile.fits'

    dc19_size = 9
    dc20_size = 9
    jades_size = 9
    sia_tables_size = 10

    dbconfig = PostgreSQLManager.load_sql_db_config(TEST_DBCONFIG_FILEPATH)
    dbconfig.update({'debug': True})        # add arguments for testing

    db_schema_name = dbconfig.get('db_schema_name')
    im_table = dbconfig.get('sql_img_md_table')

    pgmgr = PostgreSQLManager(dbconfig)     # instance of class under test


    def test_clean_table_name_default(self):
        tname = self.pgmgr.clean_table_name()
        print(tname)
        assert f"{self.db_schema_name}.{self.im_table}" == tname


    def test_clean_table_name_schema(self):
        schema = 'schemer'
        tname = self.pgmgr.clean_table_name(schema_name=schema)
        print(tname)
        assert f"{schema}.{self.im_table}" == tname


    def test_clean_table_name_table(self):
        tbl = 'tabler'
        tname = self.pgmgr.clean_table_name(table_name=tbl)
        print(tname)
        assert f"{self.db_schema_name}.{tbl}" == tname


    def test_clean_table_name_both(self):
        tbl = 'tabler'
        schema = 'schemer'
        tname = self.pgmgr.clean_table_name(schema_name=schema, table_name=tbl)
        print(tname)
        assert f"{schema}.{tbl}" == tname



    def test_image_path_from_id_noid(self):
        path = self.pgmgr.image_path_from_id()
        print(path)
        assert path is None


    def test_image_path_from_id_badid(self):
        path = self.pgmgr.image_path_from_id(uid=9999)
        print(path)
        assert path is None


    def test_image_path_from_id(self):
        path = self.pgmgr.image_path_from_id(uid=1)
        print(path)
        assert path is not None
        assert path.startswith('/vos/images/JADES')



    def test_image_metadata_badid(self):
        """ No record with given ID. """
        res = self.pgmgr.image_metadata(uid=9999)
        print(res)
        assert res is None


    def test_image_metadata(self):
        """ Valid ID. """
        res = self.pgmgr.image_metadata(1)
        print(res)
        assert res is not None
        assert res.get('id') == 1
        assert res.get('obs_collection') == 'JADES'


    def test_image_metadata_select(self):
        """ Valid ID, select non-default fields """
        res = self.pgmgr.image_metadata(uid=1, select=['id', 'obs_creator_name'])
        print(res)
        assert res is not None
        assert res.get('id') == 1
        assert res.get('obs_creator_name') == 'JWST'
        assert res.get('file_name') is None
        assert res.get('obs_collection') is None



    def test_image_metadata_by_path_badpath(self):
        """ No image with given path. """
        res = self.pgmgr.image_metadata_by_path(self.bad_path)
        print(res)
        assert res is not None
        assert len(res) == 0


    def test_image_metadata_by_path(self):
        """ Valid path. """
        res = self.pgmgr.image_metadata_by_path(self.dc19_path)
        print(res)
        assert res is not None
        assert len(res) == 1
        assert res[0].get('file_path') == self.dc19_path
        assert res[0].get('obs_collection') == 'DC19'


    def test_image_metadata_by_path_badcoll(self):
        """ Path good but collection bad. """
        res = self.pgmgr.image_metadata_by_path(self.dc20_path, collection='BADcoll')
        print(res)
        assert res is not None
        assert len(res) == 0


    def test_image_metadata_by_path_goodcoll(self):
        """ Valid path. """
        res = self.pgmgr.image_metadata_by_path(self.dc20_path, collection='DC20')
        print(res)
        assert res is not None
        assert len(res) == 1
        assert res[0].get('file_path') == self.dc20_path
        assert res[0].get('obs_collection') == 'DC20'




    def test_image_metadata_by_query_badcoll(self):
        """ No image with given collection. """
        res = self.pgmgr.image_metadata_by_query(collection='BADcoll')
        print(res)
        assert res is not None
        assert len(res) == 0


    def test_image_metadata_by_query_badfilt(self):
        """ No image with given filter. """
        res = self.pgmgr.image_metadata_by_query(filt='BADfilt')
        print(res)
        assert res is not None
        assert len(res) == 0


    def test_image_metadata_by_query_goodcoll(self):
        """ Good collection. """
        res = self.pgmgr.image_metadata_by_query(collection='DC20')
        print(res)
        assert res is not None
        assert len(res) == self.dc20_size
        collrecs = [rec.get('collection') for rec in res]
        print(collrecs)
        assert len(set(collrecs)) == 1


    def test_image_metadata_by_query_goodfilt(self):
        """ Good filter, no collection. """
        res = self.pgmgr.image_metadata_by_query(filt='F200W')
        print(res)
        assert res is not None
        assert len(res) == 3
        filtrecs = [rec.get('filter') for rec in res]
        print(filtrecs)
        assert len(set(filtrecs)) == 1


    def test_image_metadata_by_query_goodcoll_badfilt(self):
        """ Good collection but bad filter. """
        res = self.pgmgr.image_metadata_by_query(filt='BADfilt', collection='DC19')
        print(res)
        assert res is not None
        assert len(res) == 0


    def test_image_metadata_by_query_goodfilt_badcoll(self):
        """ Good filter but bad collection. """
        res = self.pgmgr.image_metadata_by_query(filt='F444W', collection='BADcoll')
        print(res)
        assert res is not None
        assert len(res) == 0


    def test_image_metadata_by_query_goodboth(self):
        """ Good filter, good collection. """
        res = self.pgmgr.image_metadata_by_query(filt='F444W', collection='DC20')
        print(res)
        assert res is not None
        assert len(res) == 1
        assert res[0].get('filter') == 'F444W'
        assert res[0].get('obs_collection') == 'DC20'


    def test_image_metadata_by_query_select(self):
        """ Good filter, good collection. """
        flds = ['id', 'filter', 'obs_collection', 'obs_creator_name']
        res = self.pgmgr.image_metadata_by_query(filt='F444W', collection='DC20', select=flds)
        print(res)
        assert res is not None
        assert len(res) == 1
        assert res[0].get('filter') == 'F444W'
        assert res[0].get('obs_collection') == 'DC20'
        assert res[0].get('obs_creator_name') == 'JWST'
        assert res[0].get('file_name') is None
        assert res[0].get('s_ra') is None



    def test_list_catalog_tables(self):
        lst = self.pgmgr.list_catalog_tables()
        print(lst)
        assert lst is not None
        assert len(lst) >= self.sia_tables_size
        assert 'sia.eazy' in lst
        assert 'sia.jtest' in lst
        assert 'sia.jwst' in lst
        assert 'tap_schema.tables' not in lst



    def test_list_collections(self):
        lst = self.pgmgr.list_collections()
        print(lst)
        assert lst is not None
        assert len(lst) > 0
        assert 'DC19' in lst
        assert 'DC20' in lst
        assert 'JADES' in lst



    def test_list_filters(self):
        lst = self.pgmgr.list_filters()
        print(lst)
        assert lst is not None
        assert len(lst) > 0
        assert 'F090W' in lst
        assert 'F335M' in lst
        assert 'F444W' in lst


    def test_list_filters_goodcoll(self):
        lst = self.pgmgr.list_filters(collection='DC19')
        print(lst)
        assert lst is not None
        assert len(lst) == self.dc19_size
        assert 'F200W' in lst
        assert 'F356W' in lst
        assert 'F410M' in lst



    def test_list_image_paths(self):
        lst = self.pgmgr.list_image_paths()
        print(lst)
        assert lst is not None
        assert len(lst) > 0
        assert self.m13_path in lst
        assert self.dc19_path in lst
        assert self.dc20_path in lst


    def test_list_image_paths_goodcoll(self):
        lst = self.pgmgr.list_image_paths(collection='DC20')
        print(lst)
        assert lst is not None
        assert len(lst) == self.dc20_size
        assert self.dc20_path in lst


    def test_list_image_paths_badcoll(self):
        lst = self.pgmgr.list_image_paths(collection='BADcoll')
        print(lst)
        assert lst is not None
        assert len(lst) == 0



    def test_list_table_names(self):
        lst = self.pgmgr.list_table_names()
        print(lst)
        assert lst is not None
        assert len(lst) >= self.sia_tables_size
        assert 'eazy' in lst
        assert 'jtest' in lst
        assert 'jwst' in lst
        assert 'tables' not in lst



    def test_query_cone_1sec(self):
        """ Basic query: center point, no filter, no collection. """
        lst = self.pgmgr.query_cone(53.157662568, -27.8075199236, 0.00027777)
        assert lst is not None
        print([ (md['id'], md['file_name'], md['obs_collection']) for md in lst])
        assert len(lst) == self.dc19_size


    def test_query_cone_90sec(self):
        """ Basic query: center point, no filter, no collection. """
        lst = self.pgmgr.query_cone(53.157662568, -27.8075199236, 0.025)
        assert lst is not None
        print([ (md['id'], md['file_name'], md['obs_collection']) for md in lst])
        assert len(lst) == self.dc19_size + self.dc20_size


    def test_query_cone_2min(self):
        """ Basic query: center point, no filter, no collection. """
        lst = self.pgmgr.query_cone(53.157662568, -27.8075199236, 0.033333333)
        assert lst is not None
        print([ (md['id'], md['file_name'], md['obs_collection']) for md in lst])
        assert len(lst) == self.jades_size + self.dc19_size + self.dc20_size


    def test_query_cone_badcoll(self):
        """ Center point, no filter, bad collection. """
        lst = self.pgmgr.query_cone(53.157662568, -27.8075199236, 0.00027777, collection='BADcoll')
        assert lst is not None
        assert len(lst) == 0


    def test_query_cone_badfilt(self):
        """ Center point, bad filter, no collection. """
        lst = self.pgmgr.query_cone(53.157662568, -27.8075199236, 0.00027777, filt='BADfilt')
        assert lst is not None
        assert len(lst) == 0


    def test_query_cone_badboth(self):
        """ Center point, bad filter, bad collection. """
        lst = self.pgmgr.query_cone(53.157662568, -27.8075199236, 0.00027777,
                                    filt='BADfilt', collection='BADcoll')
        assert lst is not None
        assert len(lst) == 0


    def test_query_cone_coll(self):
        """ Center point, no filter, good collection. """
        lst = self.pgmgr.query_cone(53.157662568, -27.8075199236, 0.00027777, collection='DC19')
        assert lst is not None
        print([ (md['id'], md['file_name'], md['obs_collection']) for md in lst])
        assert len(lst) == self.dc19_size


    def test_query_cone_filt(self):
        """ Center point, good filter, no collection. """
        lst = self.pgmgr.query_cone(53.157662568, -27.8075199236, 0.00027777, filt='F277W')
        assert lst is not None
        print([ (md['id'], md['file_name'], md['obs_collection']) for md in lst])
        assert len(lst) == 1


    def test_query_cone_both(self):
        """ Center point, good filter, good collection. """
        lst = self.pgmgr.query_cone(53.157662568, -27.8075199236, 0.00027777,
                                    filt='F356W', collection='DC19')
        assert lst is not None
        print([ (md['id'], md['file_name'], md['obs_collection']) for md in lst])
        assert len(lst) == 1



    def test_query_coordinates_jades(self):
        """ Basic query: JADES center point, no filter, no collection. """
        lst = self.pgmgr.query_coordinates(53.16468333333, -27.78311111111)
        assert lst is not None
        print([ (md['id'], md['file_name'], md['obs_collection']) for md in lst])
        assert len(lst) == self.jades_size + self.dc20_size


    def test_query_coordinates_dc19(self):
        """ Basic query: DC19 center point, no filter, no collection. """
        lst = self.pgmgr.query_coordinates(53.157662568, -27.8075199236)
        assert lst is not None
        print([ (md['id'], md['file_name'], md['obs_collection']) for md in lst])
        assert len(lst) == self.jades_size + self.dc19_size + self.dc20_size


    def test_query_coordinates_dc20(self):
        """ Basic query: DC20 center point, no filter, no collection. """
        lst = self.pgmgr.query_coordinates(53.155277381023, -27.787295217953)
        assert lst is not None
        print([ (md['id'], md['file_name'], md['obs_collection']) for md in lst])
        assert len(lst) == self.jades_size + self.dc19_size + self.dc20_size


    def test_query_coordinates_badcoll(self):
        """ Center point, no filter, bad collection. """
        lst = self.pgmgr.query_coordinates(53.157662568, -27.8075199236, collection='BADcoll')
        assert lst is not None
        assert len(lst) == 0


    def test_query_coordinates_badfilt(self):
        """ Center point, bad filter, no collection. """
        lst = self.pgmgr.query_coordinates(53.157662568, -27.8075199236, filt='BADfilt')
        assert lst is not None
        assert len(lst) == 0


    def test_query_coordinates_badboth(self):
        """ Center point, bad filter, bad collection. """
        lst = self.pgmgr.query_coordinates(53.157662568, -27.8075199236,
                                    filt='BADfilt', collection='BADcoll')
        assert lst is not None
        assert len(lst) == 0


    def test_query_coordinates_coll(self):
        """ Center point, no filter, good collection. """
        lst = self.pgmgr.query_coordinates(53.157662568, -27.8075199236, collection='DC19')
        assert lst is not None
        print([ (md['id'], md['file_name'], md['obs_collection']) for md in lst])
        assert len(lst) == self.dc19_size


    def test_query_coordinates_filt(self):
        """ Center point, good filter, no collection. """
        lst = self.pgmgr.query_coordinates(53.157662568, -27.8075199236, filt='F277W')
        assert lst is not None
        print([ (md['id'], md['file_name'], md['obs_collection']) for md in lst])
        assert len(lst) == 3


    def test_query_coordinates_both(self):
        """ Center point, good filter, good collection. """
        lst = self.pgmgr.query_coordinates(53.157662568, -27.8075199236,
                                    filt='F356W', collection='DC19')
        assert lst is not None
        print([ (md['id'], md['file_name'], md['obs_collection']) for md in lst])
        assert len(lst) == 1



    def test_query_image_noargs(self):
        """ No filter, no collection. """
        lst = self.pgmgr.query_image()
        assert lst is not None
        assert len(lst) == 0


    def test_query_image_badcoll(self):
        """ No filter, bad collection. """
        lst = self.pgmgr.query_image(collection='BADcoll')
        assert lst is not None
        assert len(lst) == 0


    def test_query_image_badfilt(self):
        """ Bad filter, no collection. """
        lst = self.pgmgr.query_image(filt='BADfilt')
        assert lst is not None
        assert len(lst) == 0


    def test_query_image_badboth(self):
        """ Bad filter, bad collection. """
        lst = self.pgmgr.query_image(filt='BADfilt', collection='BADcoll')
        assert lst is not None
        assert len(lst) == 0


    def test_query_image_coll(self):
        """ No filter, good collection. """
        lst = self.pgmgr.query_image(collection='DC20')
        assert lst is not None
        assert len(lst) == self.dc20_size


    def test_query_image_filt(self):
        """ Good filter, no collection. """
        lst = self.pgmgr.query_image(filt='F115W')
        assert lst is not None
        assert len(lst) == 3


    def test_query_image_both(self):
        """ Good filter, good collection. """
        lst = self.pgmgr.query_image(filt='F150W', collection='DC19')
        assert lst is not None
        assert len(lst) == 1
