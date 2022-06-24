import grpc
from concurrent import futures
import service_file_pb2_grpc as pb2_grpc
import service_file_pb2 as pb2
from rest_server import files_db
from uuid import UUID
from os import stat as os_stat
import mimetypes
from google.protobuf.timestamp_pb2 import Timestamp


class FileService(pb2_grpc.FileServicer):
    def stat(self, request, context):
        try:
            file = UUID(request.uuid.value)
            file_name = files_db[file]
            file_stats = os_stat(f"files/{file_name}")
        except ValueError:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "UUID is invalid")
        except KeyError:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "UUID not found")
        except FileNotFoundError:
            context.abort(grpc.StatusCode.NOT_FOUND, "File not found")
        try:
            mimetype = mimetypes.types_map[f".{file_name.split('.')[-1]}"]
        except KeyError:
            mimetype = "Unknown"
        file_info = {
            "name": file_name,
            "size": file_stats.st_size,
            "mimetype": mimetype,
            "create_datetime": Timestamp(seconds=int(file_stats.st_mtime), nanos=int(file_stats.st_mtime % 1 * 1e9)) # I am not using nanos in client ...
        }
        
        print(request.uuid.value)
        return pb2.StatReply(data=file_info)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_FileServicer_to_server(FileService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
