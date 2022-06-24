import grpc
import service_file_pb2_grpc as pb2_grpc
import service_file_pb2 as pb2


channel = grpc.insecure_channel('localhost:50051')
client = pb2_grpc.FileStub(channel)
req = pb2.StatRequest(uuid=pb2.Uuid(value="10fe4a26-e33d-4856-917d-32e7e703c97b"))
response = client.stat(request=req)
print(response)
