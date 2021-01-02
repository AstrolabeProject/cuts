import os
import pytest

import cuts.blueprints.img.arg_utils as autils
from cuts.blueprints.img.exceptions import ImageNotFound, RequestException, ServerError


class TestArgUtils(object):

    coll_emsg = "A collection name must be specified"
    filt_emsg = "An image filter must be specified"
    id_emsg = "A record ID must be specified"
    path_emsg = "A valid image path must be specified"
    ra_emsg = "Right ascension must be specified, via the 'ra' argument"
    dec_emsg = "Declination must be specified, via the 'dec' argument"

    def dump_exception (self, xcpt):
        # xcpt is an instance of pytest.ExceptionInfo
        print(f"XCPT={xcpt}")
        print(f"XCPT.type={xcpt.type}")
        print(f"XCPT.typename={xcpt.typename}")
        print(f"XCPT.value={str(xcpt.value)}")
        # print(f"dir(XCPT)={dir(xcpt)}")


    def test_parse_collection_arg_nocoll(self):
        """ No collection given, but not required. """
        coll = autils.parse_collection_arg({})
        assert coll is None


    def test_parse_collection_arg_none(self):
        """ None given, but not required. """
        coll = autils.parse_collection_arg({'collection': None})
        assert coll is None


    def test_parse_collection_arg_empty(self):
        """ Empty collection given, but not required. """
        coll = autils.parse_collection_arg({'collection': '  '})
        assert coll is None


    def test_parse_collection_arg_empty2(self):
        """ Empty coll given, but not required. """
        coll = autils.parse_collection_arg({'coll': '  '})
        assert coll is None


    def test_parse_collection_arg_nocoll_req(self):
        """ No collection argument and collection required. """
        with pytest.raises(RequestException, match=self.coll_emsg) as reqex:
            autils.parse_collection_arg({}, required=True)


    def test_parse_collection_arg_none_req(self):
        """ None given and collection required. """
        with pytest.raises(RequestException, match=self.coll_emsg) as reqex:
            autils.parse_collection_arg({'collection': None}, required=True)


    def test_parse_collection_arg_empty_req(self):
        """ Empty collection given and collection required. """
        with pytest.raises(RequestException, match=self.coll_emsg) as reqex:
            autils.parse_collection_arg({'collection': '  '}, required=True)


    def test_parse_collection_arg_empty_req2(self):
        """ Empty collection given and collection required. """
        with pytest.raises(RequestException, match=self.coll_emsg) as reqex:
            autils.parse_collection_arg({'coll': '  '}, required=True)


    def test_parse_collection_arg(self):
        """ Collection given. """
        coll = autils.parse_collection_arg({'collection': 'XXX'}, required=True)
        assert coll is not None
        assert coll == 'XXX'
        coll2 = autils.parse_collection_arg({'collection': 'horde'}, required=True)
        assert coll2 is not None
        assert coll2 == 'horde'



    def test_parse_coord_args_nora(self):
        """ No RA given. """
        with pytest.raises(RequestException, match=self.ra_emsg) as reqex:
            autils.parse_coordinate_args({})


    def test_parse_coord_args_nodec(self):
        """ No DEC given. """
        with pytest.raises(RequestException, match=self.dec_emsg) as reqex:
            autils.parse_coordinate_args({'ra': '45.0'})


    def test_parse_coord_args(self):
        """ Both RA and DEC given. """
        co_args = autils.parse_coordinate_args({ 'ra': '45.0', 'dec': '-8.2222' })
        assert co_args is not None
        assert 'ra' in co_args
        assert 'dec' in co_args
        assert 'center' in co_args



    def test_parse_filter_arg_nofilt(self):
        """ No filter given, but not required. """
        filt = autils.parse_filter_arg({})
        assert filt is None


    def test_parse_filter_arg_empty(self):
        """ Empty filter given, but not required. """
        filt = autils.parse_filter_arg({'filter': '  '})
        assert filt is None


    def test_parse_filter_arg_none(self):
        """ None given, but filter not required. """
        filt = autils.parse_filter_arg({'filter': None})
        assert filt is None


    def test_parse_filter_arg_nofilt_req(self):
        """ No filter given and filter required. """
        with pytest.raises(RequestException, match=self.filt_emsg) as reqex:
            autils.parse_filter_arg({}, required=True)


    def test_parse_filter_arg_none_req(self):
        """ None given and filter required. """
        with pytest.raises(RequestException, match=self.filt_emsg) as reqex:
            autils.parse_filter_arg({'filter': None}, required=True)


    def test_parse_filter_arg_empty_req(self):
        """ Empty filter given and filter required. """
        with pytest.raises(RequestException, match=self.filt_emsg) as reqex:
            autils.parse_filter_arg({'filter': '  '}, required=True)


    def test_parse_filter_arg(self):
        """ No filter given and filter required. """
        filt = autils.parse_filter_arg({'filter': 'XXX'}, required=True)
        assert filt is not None
        assert filt == 'XXX'
        filt = autils.parse_filter_arg({'filter': 'shhh'}, required=True)
        assert filt is not None
        assert filt == 'shhh'



    def test_parse_id_arg_noid(self):
        """ No id given, but not required. """
        uid = autils.parse_id_arg({}, required=False)
        assert uid is None


    def test_parse_id_arg_empty(self):
        """ Empty id given, but not required. """
        uid = autils.parse_id_arg({'id': '  '}, required=False)
        assert uid is None


    def test_parse_id_arg_none(self):
        """ None given, but ID not required. """
        uid = autils.parse_id_arg({'id': None}, required=False)
        assert uid is None


    def test_parse_id_arg_badnum(self):
        """ ID given but ID not a valid number. """
        uid = autils.parse_id_arg({'id': 'Ninety'}, required=False)
        assert uid is None


    def test_parse_id_arg_noid_req(self):
        """ No id given and id required. """
        with pytest.raises(RequestException, match=self.id_emsg) as reqex:
            autils.parse_id_arg({}, required=True)


    def test_parse_id_arg_none_req(self):
        """ None given and ID required. """
        with pytest.raises(RequestException, match=self.id_emsg) as reqex:
            autils.parse_id_arg({'id': None}, required=True)


    def test_parse_id_arg_empty_req(self):
        """ Empty ID given and ID required. """
        with pytest.raises(RequestException, match=self.id_emsg) as reqex:
            autils.parse_id_arg({'id': '  '}, required=True)


    def test_parse_id_arg_badnum_req(self):
        """ ID given but ID not a valid number. """
        with pytest.raises(RequestException, match=self.id_emsg) as reqex:
            autils.parse_id_arg({'id': 'Ninety'}, required=True)



    def test_parse_ipath_arg_nopath(self):
        """ No ipath given, but not required. """
        path = autils.parse_ipath_arg({})
        assert path is None


    def test_parse_ipath_arg_empty(self):
        """ Empty ipath given, but not required. """
        path = autils.parse_ipath_arg({'path': '  '})
        assert path is None


    def test_parse_ipath_arg_none(self):
        """ None given, but ipath not required. """
        path = autils.parse_ipath_arg({'path': None})
        assert path is None


    def test_parse_ipath_arg_nopath_req(self):
        """ No ipath given and ipath required. """
        with pytest.raises(RequestException, match=self.path_emsg) as reqex:
            autils.parse_ipath_arg({}, required=True)


    def test_parse_ipath_arg_none_req(self):
        """ None given and ipath required. """
        with pytest.raises(RequestException, match=self.path_emsg) as reqex:
            autils.parse_ipath_arg({'path': None}, required=True)


    def test_parse_ipath_arg_empty_req(self):
        """ Empty ipath given and ipath required. """
        with pytest.raises(RequestException, match=self.path_emsg) as reqex:
            autils.parse_ipath_arg({'path': '  '}, required=True)


    def test_parse_ipath_arg(self):
        """ No ipath given and ipath required. """
        path = autils.parse_ipath_arg({'path': '/tmp'}, required=True)
        assert path is not None
        assert path == '/tmp'
        path = autils.parse_ipath_arg({'path': 'shhh'}, required=True)
        assert path is not None
        assert path == 'shhh'
