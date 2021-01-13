import os
import pytest

import cuts.blueprints.img.tasks as tasks
from cuts.blueprints.img.exceptions import ImageNotFound, RequestException, ServerError


class TestTasks(object):

    id_emsg = "A record ID must be specified"
    id_nf_emsg = ".* Image with image ID '{0}' not found in database"


    def test_img_fetch_noid(self, client):
        """ No ID argument. """
        args = {}
        with pytest.raises(RequestException, match=self.id_emsg) as reqex:
            resp = tasks.fetch_image(args)


    def test_img_fetch_badid(self, client):
        """ No such record with given ID. """
        args = { 'id': '9999' }
        errmsg = self.id_nf_emsg.format('9999')
        with pytest.raises(ImageNotFound, match=errmsg) as reqex:
            resp = tasks.fetch_image(args)


    # def test_fetch_image_noid(self):
    #     args = {}
    #     emsg="A record ID must be specified"
    #     with pytest.raises(RequestException, match=emsg) as reqex:
    #         tasks.fetch_image(args)


    # def test_fetch_image_badid(self):
    #     args = { 'id': '9999' }
    #     emsg="Image with image ID .* not found"
    #     with pytest.raises(ImageNotFound, match=emsg) as reqex:
    #         tasks.fetch_image(args)


    def test_fetch_image_by_filter_nofilt_required(self):
        """ No filter given and filter required. """
        emsg="An image filter must be specified"
        with pytest.raises(RequestException, match=emsg) as reqex:
            tasks.fetch_image_by_filter({})
        with pytest.raises(RequestException, match=emsg) as reqex:
            tasks.fetch_image_by_filter({'filt': '  '})
