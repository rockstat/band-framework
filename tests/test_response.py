import pytest

from band.lib.json import json_def, json_loads, json_dumps

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
    assert pix_res.to_json() == b'{"type__":"pixel","data":{}}'

    err = BandResponceError('Wrong way')
    assert err.to_json() == b'{"type__":"error","statusCode":500,"errorMessage":"Wrong way","data":{}}'


def test_create_response():

    pix = '{"type__":"pixel","data":{"mydata":"123"}}'
    resp = create_response(json_loads(pix))

    assert not isinstance(resp, BandResponceData)
    assert resp.mydata == '123'

    err = BandResponceError('Wrong way')
    assert err.to_json() == b'{"type__":"error","statusCode":500,"errorMessage":"Wrong way","data":{}}'

    err_restored = create_response(json_loads(err.to_json()))
    assert isinstance(err_restored, BandResponceError)
    # array

    resp = [1,2,4]
    resp = create_response(resp)

    assert resp == [1,2,4]

    # raw
    resp = '<html></html>'
    resp = create_response(resp)

    assert resp == '<html></html>'

    # none
    resp = None
    resp = create_response(resp)

    assert resp == None

    

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
    err = create_response(json_loads(js))

    assert err.error_message == 'Wrong way'
    assert isinstance(err, BandResponceError)

