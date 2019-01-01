import json
import ujson

import pytest

from band.lib import response
from band.lib.response import BandResponceData, BandResponceError, BandResponcePixel, BandResponceRedirect, create_response



def test_response():
    with pytest.raises(TypeError):
          BandResponceData()


def test_response_hash():

    pix_res = BandResponcePixel()
    assert str(pix_res) == "Pixel"

def test_response_json():

    pix_res = BandResponcePixel()
    assert pix_res.to_json() == '{"type__":"pixel","data":{}}'

    err = BandResponceError('Wrong way')
    assert err.to_json() == '{"type__":"error","statusCode":500,"errorMessage":"Wrong way","data":{}}'


def test_response_attrs():
    response = BandResponceData({'mydata': '123'})
    
    assert response.mydata == '123'
    assert response.type__ == 'data'
    assert response['mydata'] == '123'
    with pytest.raises(KeyError):
        type__ = response['type__']


def test_response_restore():
    err = BandResponceError('Wrong way')
    
    assert err.error_message == 'Wrong way'
    assert isinstance(err, BandResponceError)

    js = err.to_json()
    err = create_response(**ujson.loads(js))

    assert err.error_message == 'Wrong way'
    assert isinstance(err, BandResponceError)