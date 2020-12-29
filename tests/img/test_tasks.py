import os
import pytest

import cuts.blueprints.img.tasks as tasks
from cuts.blueprints.img.exceptions import ImageNotFound, RequestException, ServerException


class TestTasks(object):

    def test_fetch_image_noid(self):
        args = {}
        emsg="A record ID must be specified"
        with pytest.raises(RequestException, match=emsg) as reqex:
            tasks.fetch_image(args)


    def test_fetch_image_badid(self):
        args = { 'id': '9999' }
        emsg="Image with image ID .* not found"
        with pytest.raises(ImageNotFound, match=emsg) as reqex:
            tasks.fetch_image(args)


    # # FAILS: working outside of context
    # def test_fetch_image(self):
    #     args = { 'id': '250' }
    #     emsg="Image with image ID .* not found"
    #     istream = tasks.fetch_image(args)
    #     print(istream)
    #     print(type(istream))
    #     assert istream is not None

    #     assert False

    def test_fetch_image_by_filter_nofilt_required(self):
        """ No filter given and filter required. """
        emsg="An image filter must be specified"
        with pytest.raises(RequestException, match=emsg) as reqex:
            tasks.fetch_image_by_filter({})
        with pytest.raises(RequestException, match=emsg) as reqex:
            tasks.fetch_image_by_filter({'filt': '  '})
