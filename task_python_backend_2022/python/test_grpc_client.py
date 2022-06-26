import pytest
from file_client import read_grpc, stat_grpc
from service_file_pb2 import StatRequest, ReadRequest, Uuid
from filecmp import cmp as compare_files
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
    print(resp.data)
    assert resp.data.create_datetime.seconds == 1649957732
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
