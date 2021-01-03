import cuts.blueprints.img.exceptions as xcpt
import os
import pytest


class TestExceptions(object):

    BAD_REQUEST = 'Bad Request'
    BAD_FILE = 'Image XXX.bad Not Found'
    FAULT = 'Something went wrong'

    def test_processing_error_default(self):
        reqex = xcpt.ProcessingError(self.FAULT)
        print(reqex)
        print(type(reqex))
        assert reqex.error_code == xcpt.ProcessingError.ERROR_CODE
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.FAULT
        rtup = reqex.to_tuple()
        assert rtup[0] == self.FAULT
        assert rtup[1] == xcpt.ProcessingError.ERROR_CODE


    def test_processing_error(self):
        reqex = xcpt.ProcessingError(self.FAULT, 100)
        print(reqex)
        print(type(reqex))
        assert reqex.error_code == 100
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.FAULT
        rtup = reqex.to_tuple()
        assert rtup[0] == self.FAULT
        assert rtup[1] == 100


    def test_image_not_found(self):
        reqex = xcpt.ImageNotFound(self.BAD_FILE)
        print(reqex)
        print(type(reqex))
        assert reqex.error_code == xcpt.ImageNotFound.ERROR_CODE
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.BAD_FILE
        rtup = reqex.to_tuple()
        assert rtup[0] == self.BAD_FILE
        assert rtup[1] == xcpt.ImageNotFound.ERROR_CODE


    def test_image_not_found_withcode(self):
        reqex= xcpt.ImageNotFound(self.BAD_FILE, 99)
        assert reqex.error_code == 99
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.BAD_FILE
        rtup = reqex.to_tuple()
        assert rtup[0] == self.BAD_FILE
        assert rtup[1] == 99


    def test_request_exception(self):
        reqex = xcpt.RequestException(self.BAD_REQUEST)
        print(reqex)
        print(type(reqex))
        assert reqex.error_code == xcpt.RequestException.ERROR_CODE
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.BAD_REQUEST
        rtup = reqex.to_tuple()
        assert rtup[0] == self.BAD_REQUEST
        assert rtup[1] == xcpt.RequestException.ERROR_CODE


    def test_request_exception_withcode(self):
        reqex= xcpt.RequestException(self.BAD_REQUEST, 555)
        assert reqex.error_code == 555
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.BAD_REQUEST
        rtup = reqex.to_tuple()
        assert rtup[0] == self.BAD_REQUEST
        assert rtup[1] == 555


    def test_server_exception(self):
        reqex = xcpt.ServerError(self.FAULT)
        print(reqex)
        print(type(reqex))
        assert reqex.error_code == xcpt.ServerError.ERROR_CODE
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.FAULT
        rtup = reqex.to_tuple()
        assert rtup[0] == self.FAULT
        assert rtup[1] == xcpt.ServerError.ERROR_CODE


    def test_server_exception_withcode(self):
        reqex= xcpt.ServerError(self.FAULT, 7)
        assert reqex.error_code == 7
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.FAULT
        rtup = reqex.to_tuple()
        assert rtup[0] == self.FAULT
        assert rtup[1] == 7


    def test_unsupported_type(self):
        reqex = xcpt.UnsupportedType(self.FAULT)
        print(reqex)
        print(type(reqex))
        assert reqex.error_code == xcpt.UnsupportedType.ERROR_CODE
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.FAULT
        rtup = reqex.to_tuple()
        assert rtup[0] == self.FAULT
        assert rtup[1] == xcpt.UnsupportedType.ERROR_CODE


    def test_unsupported_type_withcode(self):
        reqex= xcpt.UnsupportedType(self.FAULT, 77)
        assert reqex.error_code == 77
        rdict = reqex.to_dict()
        assert 'message' in rdict
        assert rdict.get('message') == self.FAULT
        rtup = reqex.to_tuple()
        assert rtup[0] == self.FAULT
        assert rtup[1] == 77
