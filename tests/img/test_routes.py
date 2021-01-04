import os
import pytest

from cuts.blueprints.img.exceptions import ImageNotFound, RequestException, ServerError

class TestRoutes(object):

    id_emsg = "A record ID must be specified"
    id_nf_emsg = "Image with image ID '{0}' not found in database"
    filt_emsg = "An image filter must be specified"
    filt_nf_emsg = "Image with filter '{0}' {1} not found in database"
    filt_coll_nf_emsg = "Image with filter '{0}' and collection '{1}' not found in database"
    path_emsg = "A valid image path must be specified, via the 'path' argument"
    path_nf_emsg = "Specified image file '{}' not found"


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


    def test_fetch_image_noid(self, client):
        """ No ID argument. """
        resp = client.get('/img/fetch')
        assert resp is not None
        assert resp.status_code == 400
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        assert self.id_emsg in resp_msg


    def test_fetch_image_badid(self, client):
        """ No such record with given ID. """
        resp = client.get('/img/fetch?id=99999')
        assert resp is not None
        assert resp.status_code == 404
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        errmsg = self.id_nf_emsg.format('99999')
        assert errmsg in resp_msg


    # def test_fetch_image(self, client):
    #     """ Valid ID given: might succeed. """
    #     args = { 'id': '250' }
    #     with client:
    #         istream = client.get("/img/fetch?id=250")
    #         print(istream)
    #         print(type(istream))
    #         assert istream is not None


    def test_fetch_image_by_filter_nofilt(self, client):
        """ No filter argument. """
        resp = client.get('/img/fetch_by_filter')
        assert resp is not None
        assert resp.status_code == 400
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        assert self.filt_emsg in resp_msg


    def test_fetch_image_by_filter_badfilt(self, client):
        """ No such filter value. """
        filt = 'BAD1'
        coll = ''
        errmsg = self.filt_nf_emsg.format(filt, coll)
        resp = client.get(f"/img/fetch_by_filter?filter={filt}")
        assert resp is not None
        assert resp.status_code == 404
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        assert errmsg in resp_msg


    def test_fetch_image_by_filter_badcoll(self, client):
        """ Valid filter value but no such collection value. """
        filt = 'JADES'
        coll = 'BADColl'
        errmsg = self.filt_coll_nf_emsg.format(filt, coll)
        resp = client.get(f"/img/fetch_by_filter?filter={filt}&collection={coll}")
        assert resp is not None
        assert resp.status_code == 404
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        assert errmsg in resp_msg


    def test_fetch_image_by_filter_badfilt_badcoll(self, client):
        """ No such filter value and no such collection value. """
        coll = 'BADColl'
        filt = 'BADFilt'
        errmsg = self.filt_coll_nf_emsg.format(filt, coll)
        resp = client.get(f"/img/fetch_by_filter?filter={filt}&collection={coll}")
        assert resp is not None
        assert resp.status_code == 404
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        assert errmsg in resp_msg



    def test_fetch_by_path_nopath(self, client):
        """ No path argument. """
        resp = client.get('/img/fetch_by_path')
        assert resp is not None
        assert resp.status_code == 400
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        assert self.path_emsg in resp_msg


    def test_fetch_by_path_emptypath(self, client):
        """ No value for path argument. """
        resp = client.get('/img/fetch_by_path?path=')
        assert resp is not None
        assert resp.status_code == 400
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        assert self.path_emsg in resp_msg


    def test_fetch_by_path_badpath(self, client):
        """ No such path as given. """
        badpath = '/bad/path'
        resp = client.get(f"/img/fetch_by_path?path={badpath}")
        assert resp is not None
        assert resp.status_code == 404
        resp_msg = str(resp.data, encoding='UTF-8') or ''
        errmsg = self.path_nf_emsg.format(badpath)
        assert errmsg in resp_msg
