import requests
import pytest
file_client = __import__("file-client") # because we have filename with dash
read = file_client.read
stat = file_client.stat
# end of imports

class MockResponseForReadFunction:
    status_code = 200
    reason = "Not found"

    @staticmethod
    def json():
        return {"name": "flag_cze.svg", # this is file with UUID 10fe4a26-e33d-4856-917d-32e7e703c97b
                "size": "605",
                "mimetype": "image/svg+xml",
                "create_datetime": "2022-06-21 07:00:47", # datetime is problem, it behaves differently on each OS, but for this unit test I can let it be
                }

def test_stat_for_normal_result(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponseForReadFunction()

    monkeypatch.setattr(requests, "get", mock_get)

    result = stat("fakeurl", "fake_uuid") 
    assert result == f"""
            Information about file:
            File name is: flag_cze.svg
            File size in bytes is: 605
            File mimetype is: image/svg+xml
            File was created at (different on every OS): 2022-06-21 07:00:47\n
            """
    
def test_stat_for_status_other_then_200(monkeypatch):
    local_mock = MockResponseForReadFunction()
    local_mock.status_code = 404
    def mock_get(*args, **kwargs):
        return local_mock

    monkeypatch.setattr(requests, "get", mock_get)

    result = stat("fakeurl", "fake_uuid") 
    assert result == "Not found"

def test_stat_for_keyerror(monkeypatch):
    local_mock = MockResponseForReadFunction()
    def another_json_mock():
        return {}
    local_mock.json = another_json_mock

    def mock_get(*args, **kwargs):
        return local_mock
    monkeypatch.setattr(requests, "get", mock_get)
    
    with pytest.raises(KeyError):
        stat("fakeurl", "fake_uuid") 