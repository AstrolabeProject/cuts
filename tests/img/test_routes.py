# Tests for the image manager module.
#   Written by: Tom Hicks. 12/28/2020.
#   Last Modified: Update for moving VOS data to /usr/local/data.
#
import os
import pytest

from flask import request, jsonify

from cuts.blueprints.img import routes
from cuts.blueprints.img import tasks
from cuts.blueprints.img.exceptions import ImageNotFound, RequestException, ServerError
from cuts.blueprints.img.exceptions import ProcessingError, UnsupportedType
from cuts.blueprints.img.fits_utils import FITS_MIME_TYPE
from cuts.blueprints.img.image_manager import ImageManager
from tests import TEST_RESOURCES_DIR, TEST_DBCONFIG_FILEPATH, VOS


class TestRoutes(object):

    co_fyl_emsg = "A cached filename must be specified, via the 'filename' argument"
    co_nf_emsg = "Cached image cutout file '{0}' not found in cutouts cache directory"
    coll_emsg = "A collection name must be specified, via the 'collection' argument"
    dec_convert_emsg = "Error trying to convert the specified DEC to a number."
    dec_emsg = "Declination must be specified, via the 'dec' argument"
    filt_coll_nf_emsg = "Image with filter '{0}' and collection '{1}' not found in database"
    filt_emsg = "An image filter must be specified"
    filt_nf_emsg = "Image with filter '{0}' {1} not found in database"
    id_emsg = "A record ID must be specified"
    id_nf_emsg = "Image with image ID '{0}' not found in database"
    md_id_nf_emsg = "Image metadata for image ID '{0}' not found in database"
    no_coords_filt_emsg = "No matching image for coordinates (in cone) with filter '{}' was found"
    path_emsg = "A valid image path must be specified, via the 'path' argument"
    path_nf_emsg = "Specified image file '{}' not found"
    ra_convert_emsg = "Error trying to convert the specified RA to a number."
    ra_emsg = "Right ascension must be specified, via the 'ra' argument"
    size_convert_emsg = "Error trying to convert the given size specification to a number."
    size_emsg = "A radius size (one of 'radius', 'sizeDeg', 'sizeArcMin', or 'sizeArcSec') must be specified."

    m13_path =  f"{VOS}/images/XTRAS/m13.fits"
    dc19_path = f"{VOS}/images/DC19/F090W.fits"
    dc20_path = f"{VOS}/images/DC20/F356W.fits"

    jades_size = 9
    dc19_size = 9
    dc20_size = 9

    test_args = {
        'debug': True,
        'dbconfig_file': TEST_DBCONFIG_FILEPATH
    }

    # The following overrides the image manager in the tasks module for testing purposes
    tasks.imgr = ImageManager(test_args)  # image manager for tests


    def test_img_fetch_noid(self, client):
        """ No ID argument. """
        resp = client.get('/img/fetch')
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.id_emsg in resp_msg


    def test_img_fetch_badid(self, client):
        """ No such record with given ID. """
        resp = client.get('/img/fetch?id=99999')
        print(resp)
        assert resp is not None
        assert resp.status_code == ImageNotFound.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        errmsg = self.id_nf_emsg.format('99999')
        assert errmsg in resp_msg



    def test_img_fetch_by_filter_nofilt(self, client):
        """ No filter argument. """
        resp = client.get('/img/fetch_by_filter')
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.filt_emsg in resp_msg


    def test_img_fetch_by_filter_badfilt(self, client):
        """ No such filter value. """
        filt = 'BAD1'
        coll = ''
        resp = client.get(f"/img/fetch_by_filter?filter={filt}")
        print(resp)
        assert resp is not None
        assert resp.status_code == ImageNotFound.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        errmsg = self.filt_nf_emsg.format(filt, coll)
        assert errmsg in resp_msg


    def test_img_fetch_by_filter_badcoll(self, client):
        """ Valid filter value but no such collection value. """
        filt = 'JADES'
        coll = 'BADColl'
        resp = client.get(f"/img/fetch_by_filter?filter={filt}&collection={coll}")
        print(resp)
        assert resp is not None
        assert resp.status_code == ImageNotFound.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        errmsg = self.filt_coll_nf_emsg.format(filt, coll)
        assert errmsg in resp_msg


    def test_img_fetch_by_filter_badfilt_badcoll(self, client):
        """ No such filter value and no such collection value. """
        coll = 'BADColl'
        filt = 'BADFilt'
        resp = client.get(f"/img/fetch_by_filter?filter={filt}&collection={coll}")
        print(resp)
        assert resp is not None
        assert resp.status_code == ImageNotFound.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        errmsg = self.filt_coll_nf_emsg.format(filt, coll)
        assert errmsg in resp_msg



    def testimg_fetch_by_path_nopath(self, client):
        """ No path argument. """
        resp = client.get('/img/fetch_by_path')
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.path_emsg in resp_msg


    def testimg_fetch_by_path_emptypath(self, client):
        """ No value for path argument. """
        resp = client.get('/img/fetch_by_path?path=')
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.path_emsg in resp_msg


    def testimg_fetch_by_path_badpath(self, client):
        """ No such path as given. """
        badpath = '/bad/path'
        resp = client.get(f"/img/fetch_by_path?path={badpath}")
        print(resp)
        assert resp is not None
        assert resp.status_code == ImageNotFound.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        errmsg = self.path_nf_emsg.format(badpath)
        assert errmsg in resp_msg



    def test_img_metadata_noid(self, client):
        """ No ID argument. """
        resp = client.get('/img/metadata')
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.id_emsg in resp_msg


    def test_img_metadata_badid(self, client):
        """ No such record with given ID. """
        resp = client.get('/img/metadata?id=99999&debug=true')
        print(resp)
        assert resp is not None
        assert resp.status_code == ImageNotFound.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        errmsg = self.md_id_nf_emsg.format('99999')
        assert errmsg in resp_msg



    def test_img_metadata_by_collection_nocoll(self, client):
        """ No collection argument. """
        resp = client.get('/img/metadata_by_collection')
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.coll_emsg in resp_msg


    def test_img_metadata_by_collection_emptycoll(self, client):
        """ No value for collection argument. """
        coll = ''
        resp = client.get(f"/img/metadata_by_collection?collection=")
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.coll_emsg in resp_msg


    def test_img_metadata_by_collection_badcoll(self, client):
        """ No such collection value. """
        coll = 'BADColl'
        resp = client.get(f"/img/metadata_by_collection?collection={coll}")
        print(resp)
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        assert '[]' in str(resp.data)



    def test_img_metadata_by_filter_nofilt(self, client):
        """ No filter argument. """
        resp = client.get('/img/metadata_by_filter')
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.filt_emsg in resp_msg


    def test_img_metadata_by_filter_emptyfilt(self, client):
        """ No value for filter argument. """
        filt = ''
        coll = ''
        resp = client.get(f"/img/metadata_by_filter?filter=")
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.filt_emsg in resp_msg


    def test_img_metadata_by_filter_badfilt(self, client):
        """ No such filter value. """
        filt = 'BAD1'
        coll = ''
        resp = client.get(f"/img/metadata_by_filter?filter={filt}")
        print(resp)
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        assert '[]' in str(resp.data)


    def test_img_metadata_by_filter_badcoll(self, client):
        """ Valid filter value but no such collection value. """
        filt = 'JADES'
        coll = 'BADColl'
        resp = client.get(f"/img/metadata_by_filter?filter={filt}&collection={coll}")
        print(resp)
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        assert '[]' in str(resp.data)


    def test_img_metadata_by_filter_badfilt_badcoll(self, client):
        """ No such filter value and no such collection value. """
        coll = 'BADColl'
        filt = 'BADFilt'
        resp = client.get(f"/img/metadata_by_filter?filter={filt}&collection={coll}")
        print(resp)
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        assert '[]' in str(resp.data)



    def testimg_img_metadata_by_path_nopath(self, client):
        """ No path argument. """
        resp = client.get('/img/metadata_by_path')
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.path_emsg in resp_msg


    def testimg_img_metadata_by_path_emptypath(self, client):
        """ No value for path argument. """
        resp = client.get('/img/metadata_by_path?path=')
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.path_emsg in resp_msg


    def testimg_img_metadata_by_path_badpath(self, client):
        """ No such path as given, so empty list returned. """
        badpath = '/bad/path'
        resp = client.get(f"/img/metadata_by_path?path={badpath}")
        print(resp)
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        assert '[]' in str(resp.data)


    def test_img_metadata_by_path_badcoll(self, client):
        """ Valid filter value but no such collection value. """
        path = f"{VOS}/images/DC20/F090W.fits"
        coll = 'BADColl'
        resp = client.get(f"/img/metadata_by_path?path={path}&collection={coll}")
        print(resp)
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        assert '[]' in str(resp.data)


    def test_img_metadata_by_path_badfilt_badcoll(self, client):
        """ No such filter value and no such collection value. """
        path = '/bad/path'
        coll = 'BADColl'
        resp = client.get(f"/img/metadata_by_path?path={path}&collection={coll}")
        print(resp)
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        assert '[]' in str(resp.data)



    def test_list_collections(self, client):
        resp = client.get("/img/list_collections")
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        jdata = resp.get_json()
        print(jdata)
        assert 'DC19' in jdata
        assert 'DC20' in jdata
        assert 'JADES' in jdata


    def test_list_filters(self, client):
        resp = client.get("/img/list_filters")
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        jdata = resp.get_json()
        print(jdata)
        assert 'F090W' in jdata
        assert 'F335M' in jdata
        assert 'F444W' in jdata


    def test_list_image_paths(self, client):
        resp = client.get("/img/list_image_paths")
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        jdata = resp.get_json()
        print(jdata)
        assert self.m13_path in jdata
        assert self.dc19_path in jdata
        assert self.dc20_path in jdata



    def test_query_cone_noargs(self, client):
        """ No CO arguments, size or coordinates, given. """
        resp = client.get(f"/img/query_cone")
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.size_emsg in resp_msg


    def test_query_cone_coll_noco(self, client):
        """ Collection but no CO arguments, size or coordinates, given. """
        coll = 'JADES'
        resp = client.get(f"/img/query_cone?collection={coll}")
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.size_emsg in resp_msg


    def test_query_cone_emptysize(self, client):
        """ Empty size, no coordinates given. """
        resp = client.get(f"/img/query_cone?sizeDeg=")
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.size_emsg in resp_msg


    def test_query_cone_size_arcsec(self, client):
        """ Good size but no coordinates given. """
        resp = client.get(f"/img/query_cone?sizeArcSec=30")
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.ra_emsg in resp_msg


    def test_query_cone_size_degree(self, client):
        """ Good size but no coordinates given. """
        resp = client.get(f"/img/query_cone?sizeDeg=0.47")
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.ra_emsg in resp_msg


    def test_query_cone_size_radius(self, client):
        """ Good size but no coordinates given. """
        resp = client.get(f"/img/query_cone?radius=0.005")
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.ra_emsg in resp_msg


    def test_query_cone_size_arcmin(self, client):
        """ Good size but no coordinates given. """
        resp = client.get(f"/img/query_cone?sizeArcMin=1")
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.ra_emsg in resp_msg


    def test_query_cone_badsize(self, client):
        """ Bad size and no coordinates given. """
        resp = client.get(f"/img/query_cone?radius=TWO")
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.size_convert_emsg in resp_msg


    def test_query_cone_badra(self, client):
        """ Good size, bad RA value given. """
        resp = client.get(f"/img/query_cone?sizeArcMin=1&ra=TWO")
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.ra_convert_emsg in resp_msg


    def test_query_cone_nodec(self, client):
        """ Good size, good RA value, but no DEC value given. """
        resp = client.get(f"/img/query_cone?sizeArcMin=1&ra=24.74")
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.dec_emsg in resp_msg


    def test_query_cone_baddec(self, client):
        """ Good size, good RA value, but bad DEC value given. """
        resp = client.get(f"/img/query_cone?sizeArcMin=1&ra=24.74&dec=one")
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.dec_convert_emsg in resp_msg


    def test_query_cone(self, client):
        """ Good values, but no such records. """
        resp = client.get(f"/img/query_cone?sizeArcSec=1&ra=-89.888&dec=0.0")
        print(resp)
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        assert '[]' in str(resp.data)



    def test_query_coordinates(self, client):
        resp = client.get("/img/query_coordinates?ra=53.155277381023&dec=-27.787295217953")
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        jdata = resp.get_json()
        print(jdata)
        print([ (md['id'], md['file_name'], md['obs_collection']) for md in jdata])
        assert len(jdata) == self.jades_size + self.dc19_size + self.dc20_size
        assert 'id' in jdata[0]
        assert 'file_name' in jdata[0]
        assert 'file_path' in jdata[0]



    def test_co_list(self, client):
        resp = client.get("/co/list")
        print(resp)
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        assert '[]' in str(resp.data)



    def test_query_image_coll(self, client):
        """ No filter, good collection. """
        resp = client.get("/img/query_image?collection=JADES")
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        jdata = resp.get_json()
        print(jdata)
        assert len(jdata) == self.jades_size


    def test_query_image_filt(self, client):
        """ Good filter, no collection. """
        resp = client.get("/img/query_image?filter=F335M")
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        jdata = resp.get_json()
        assert len(jdata) == 3


    def test_query_image_both(self, client):
        """ Good filter, good collection. """
        resp = client.get("/img/query_image?collection=JADES&filter=F090W")
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        jdata = resp.get_json()
        assert len(jdata) == 1



    def test_co_cutout(self, client):
        """ Cutout: m13 center point, no filter, no collection. """
        resp = client.get("/co/cutout?ra=250.4226&dec=36.4602&sizeArcSec=12")
        assert resp is not None
        assert resp.status_code == 200
        assert resp.mimetype == FITS_MIME_TYPE
        assert resp.data is not None



    def test_co_cutout_by_filter_badfilt(self, client):
        """ Cutout: m13 center point, bad filter, no collection. """
        resp = client.get("/co/cutout_by_filter?ra=250.4226&dec=36.4602&sizeArcSec=12&filter=BADfilt")
        assert resp is not None
        assert resp.status_code == ImageNotFound.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        errmsg = self.no_coords_filt_emsg.format('BADfilt')
        assert errmsg in resp_msg


    def test_co_cutout_by_filter(self, client):
        """ Cutout: HorseHead center point, by filter, no collection. """
        resp = client.get("/co/cutout_by_filter?ra=85.27497&dec=-2.458265&sizeArcSec=12&filter=OG590")
        assert resp is not None
        assert resp.status_code == 200
        assert resp.mimetype == FITS_MIME_TYPE
        assert resp.data is not None



    def test_co_fetch_from_cache_noname(self, client):
        """ No ID argument. """
        resp = client.get('/co/fetch_from_cache')
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.co_fyl_emsg in resp_msg


    def test_co_fetch_from_cache_emptyname(self, client):
        """ No ID argument. """
        resp = client.get('/co/fetch_from_cache?filename=')
        print(resp)
        assert resp is not None
        assert resp.status_code == RequestException.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        assert self.co_fyl_emsg in resp_msg


    def test_co_fetch_from_cache_badname(self, client):
        """ No such record with given ID. """
        nosuch = 'NoSuchFile'
        resp = client.get(f"/co/fetch_from_cache?filename={nosuch}")
        print(resp)
        assert resp is not None
        assert resp.status_code == ImageNotFound.ERROR_CODE
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        print(resp_msg)
        errmsg = self.co_nf_emsg.format(nosuch)
        assert errmsg in resp_msg



    def test_echo_empty(self, client):
        resp = client.get("/echo")
        print(resp)
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        assert '{}' in str(resp.data)


    def test_echo_nonempty(self, client):
        resp = client.get("/echo?arg1=1&arg2=other")
        print(resp)
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        respstr = str(resp.data)
        assert '"arg1":"1"' in respstr
        assert '"arg2":"other"' in respstr



    def test_handle_processing_error(self):
        errMsg = 'Test ProcessingError'
        tup = routes.handle_processing_error(ProcessingError(errMsg))
        assert tup[0] == errMsg
        assert tup[1] == ProcessingError.ERROR_CODE


    def test_handle_image_not_found(self):
        errMsg = 'Test ImageNotFound'
        tup = routes.handle_processing_error(ImageNotFound(errMsg))
        assert tup[0] == errMsg
        assert tup[1] == ImageNotFound.ERROR_CODE


    def test_handle_request_exception(self):
        errMsg = 'Test RequestException'
        tup = routes.handle_processing_error(RequestException(errMsg))
        assert tup[0] == errMsg
        assert tup[1] == RequestException.ERROR_CODE


    def test_handle_server_error(self):
        errMsg = 'Test ServerError'
        tup = routes.handle_server_error(ServerError(errMsg))
        assert tup[0] == errMsg
        assert tup[1] == ServerError.ERROR_CODE


    def test_handle_unsupported_type(self):
        errMsg = 'Test UnsupportedType'
        tup = routes.handle_unsupported_type(UnsupportedType(errMsg))
        assert tup[0] == errMsg
        assert tup[1] == UnsupportedType.ERROR_CODE
