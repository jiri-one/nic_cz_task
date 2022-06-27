import pytest
from file_client import read_grpc, stat_grpc
from service_file_pb2 import StatRequest, ReadRequest, Uuid
from filecmp import cmp as compare_files
import grpc
# end of imports


@pytest.fixture(scope='module')
def grpc_add_to_server():
    from service_file_pb2_grpc import add_FileServicer_to_server
    return add_FileServicer_to_server


@pytest.fixture(scope='module')
def grpc_servicer():
    from grpc_server import FileService
    return FileService()


@pytest.fixture(scope='module')
def grpc_stub_cls(grpc_channel):
    from service_file_pb2_grpc import FileStub
    return FileStub


def test_StatRequest(grpc_stub):
    req = StatRequest(
        uuid=Uuid(value="10fe4a26-e33d-4856-917d-32e7e703c97b"))  # file flag_cze.svg
    resp = grpc_stub.stat(req)
    assert resp.data.create_datetime.seconds == 1655787647
    assert resp.data.size == 605
    assert resp.data.mimetype == "image/svg+xml"
    assert resp.data.name == "flag_cze.svg"


def test_ReadRequest(grpc_stub, tmp_path):
    output_file = tmp_path / "output_file_for_test"
    req = ReadRequest(
        uuid=Uuid(value="10fe4a26-e33d-4856-917d-32e7e703c97b"), size=2048)  # file flag_cze.svg
    resp = grpc_stub.read(req)
    with open(output_file, 'wb') as f:
        for chunk in resp:
            f.write(chunk.data.data)
    assert compare_files(output_file, "files/flag_cze.svg")


def test_stat_grpc_for_normal_result(grpc_channel, monkeypatch):
    def mockchanel(nothing):
        return grpc_channel
    monkeypatch.setattr(grpc, "insecure_channel", mockchanel)
    result = stat_grpc("fake_server", "10fe4a26-e33d-4856-917d-32e7e703c97b") # file flag_cze.svg
    assert result == f"""
            Information about file:
            File name is: flag_cze.svg
            File size in bytes is: 605
            File mimetype is: image/svg+xml
            File was created at (different on every OS): 2022-06-21 07:00:47\n
            """


def test_stat_grpc_for_invalid_uuid(grpc_channel, monkeypatch):
    def mockchanel(nothing):
        return grpc_channel
    monkeypatch.setattr(grpc, "insecure_channel", mockchanel)
    result = stat_grpc("fake_server", "fake_uuid")
    assert result == "UUID is invalid"


def test_stat_grpc_for_non_existed_uuid(grpc_channel, monkeypatch):
    def mockchanel(nothing):
        return grpc_channel
    monkeypatch.setattr(grpc, "insecure_channel", mockchanel)
    result = stat_grpc("fake_server", "10fe4a26-e33d-4856-917d-32e7e703c97c") # non existed UUID
    assert result == "UUID not found"


def test_stat_grpc_for_non_existed_file(grpc_channel, monkeypatch):
    def mockchanel(nothing):
        return grpc_channel
    monkeypatch.setattr(grpc, "insecure_channel", mockchanel)
    with monkeypatch.context() as m:
        import rest_server
        from uuid import UUID
        m.setitem(rest_server.files_db, UUID("8a3e5be1-f600-11ec-b82c-e4e7492bca65"), "non_existed_file") # fake UUID with non existed file
        result = stat_grpc("fake_server", "8a3e5be1-f600-11ec-b82c-e4e7492bca65") # same fake UUID
        assert result == "File not found"
