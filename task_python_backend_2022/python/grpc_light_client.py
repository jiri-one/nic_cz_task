import grpc
import service_file_pb2_grpc as pb2_grpc
import service_file_pb2 as pb2
from datetime import datetime


channel = grpc.insecure_channel('localhost:50051')
client = pb2_grpc.FileStub(channel)
req = pb2.StatRequest(uuid=pb2.Uuid(value="10fe4a26-e33d-4856-917d-32e7e703c97b"))
try:
    response = resp = client.stat(request=req)
except grpc.RpcError as rpc_error:
    if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
        print(1)
    elif rpc_error.code() == grpc.StatusCode.FAILED_PRECONDITION:
        print(2)
    elif rpc_error.code() == grpc.StatusCode.NOT_FOUND:
        print(3)
    else:
        print(f"Received unknown RPC error: code={rpc_error.code()} message={rpc_error.details()}")
print(datetime.fromtimestamp(resp.data.create_datetime.seconds).isoformat(" ", "seconds"))
