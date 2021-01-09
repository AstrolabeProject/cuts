import os
import pytest

from cuts.blueprints.img.exceptions import ImageNotFound, RequestException, ServerError

class TestRoutes(object):

    id_emsg = "A record ID must be specified"
    id_nf_emsg = "Image with image ID '{0}' not found in database"
    filt_emsg = "An image filter must be specified"
    filt_nf_emsg = "Image with filter '{0}' {1} not found in database"
    filt_coll_nf_emsg = "Image with filter '{0}' and collection '{1}' not found in database"
    coll_emsg = "A collection name must be specified, via the 'collection' argument"
    path_emsg = "A valid image path must be specified, via the 'path' argument"
    path_nf_emsg = "Specified image file '{}' not found"
    md_id_nf_emsg = "Image metadata for image ID '{0}' not found in database"
    co_fyl_emsg = "A cached filename must be specified, via the 'filename' argument"
    co_nf_emsg = "Cached image cutout file '{0}' not found in cutouts cache directory"
    size_emsg = "A radius size (one of 'radius', 'sizeDeg', 'sizeArcMin', or 'sizeArcSec') must be specified."
    size_convert_emsg = "Error trying to convert the given size specification to a number."
    ra_emsg = "Right ascension must be specified, via the 'ra' argument"
    ra_convert_emsg = "Error trying to convert the specified RA to a number."
    dec_emsg = "Declination must be specified, via the 'dec' argument"
    dec_convert_emsg = "Error trying to convert the specified DEC to a number."


    # def dump_exception (self, xcpt):
    #     # xcpt is an instance of pytest.ExceptionInfo
    #     print(f"XCPT={xcpt}")
    #     print(f"XCPT.type={xcpt.type}")
    #     print(f"XCPT.typename={xcpt.typename}")
    #     print(f"XCPT.value={str(xcpt.value)}")
    #     # print(f"dir(XCPT)={dir(xcpt)}")

    # def test_xray_response(self, client):
    #     emsg="Image with image ID .* not found"
    #     rv = client.get('/img/fetch?id=9999')
    #     print(f"dir(RV)={dir(rv)}")
    #     print(f"RV={rv}")
    #     print(f"type(RV)={type(rv)}")
    #     print(f"RV.status={rv.status}")
    #     print(f"RV.status_code={rv.status_code}")
    #     print(f"RV.data={str(rv.data,encoding='UTF-8')}")
    #     assert False


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
        path = '/vos/images/DC20/F090W.fits'
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



    def test_co_list(self, client):
        resp = client.get("/co/list")
        print(resp)
        assert resp is not None
        assert resp.status_code == 200
        assert resp.data is not None
        assert '[]' in str(resp.data)



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
