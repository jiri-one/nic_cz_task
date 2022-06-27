from os import write
from shutil import which
import requests
import click
import grpc
from service_file_pb2 import StatRequest, ReadRequest, Uuid
from service_file_pb2_grpc import FileStub
from datetime import datetime
import json


def stat_rest(server, uuid_arg):
    try:
        resp = requests.get(f"http://{server}/file/{uuid_arg}/stat/")
    except requests.ConnectionError:
        return print("Connection error")
    if resp.status_code == 200: 
        try:
            data = resp.json()
            return f"""
            Information about file:
            File name is: {data["name"]}
            File size in bytes is: {data["size"]}
            File mimetype is: {data["mimetype"]}
            File was created at (different on every OS): {data["create_datetime"]}\n
            """
        except KeyError as e:
            e.message = "Some data from server are missing, check it in some client to analyze data"
            raise
        # I can handle here more exceptions and work with KeyError little more in detail ...
    else:
        return json.loads(resp.text)["title"]


def read_rest(server, uuid_arg):
    """I left this function really simple, but the main bug is, that you can download content from whole internet :-) and reading and writing is better with chunks, but chunks I have used in grpc version, so I am showing another (not so good ...) way too."""
    try:
        resp = requests.get(f"http://{server}/file/{uuid_arg}/read/")
    except requests.ConnectionError:
        return print("Connection error")
    if resp.status_code == 200:
        return resp.content
    else:
        return json.loads(resp.text)["title"]

def stat_grpc(server, uuid_arg):
    channel = grpc.insecure_channel(server)
    client = FileStub(channel)
    req = StatRequest(uuid=Uuid(value=uuid_arg))
    try:
        resp = client.stat(request=req)
    except grpc.RpcError as rpc_error:
        if (rpc_error.code() == grpc.StatusCode.UNAVAILABLE
            or rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT
            or rpc_error.code() == grpc.StatusCode.FAILED_PRECONDITION
            or rpc_error.code() == grpc.StatusCode.NOT_FOUND):
            return rpc_error.details()
        else:
            return f"Received unknown RPC error: code={rpc_error.code()} message={rpc_error.details()}"
    return f"""
            Information about file:
            File name is: {resp.data.name}
            File size in bytes is: {resp.data.size}
            File mimetype is: {resp.data.mimetype}
            File was created at (different on every OS): {datetime.fromtimestamp(
            resp.data.create_datetime.seconds).isoformat(" ", "seconds")}\n
            """


def read_grpc(server, uuid_arg):
    channel = grpc.insecure_channel(server)
    client = FileStub(channel)
    req = ReadRequest(uuid=Uuid(value=uuid_arg), size=512) # size is here hardcoded, because user settings was not demanded
    return client.read(request=req)

@click.command(no_args_is_help=True)
@click.argument('method', type=click.Choice(['stat', 'read']))
@click.argument('UUID')
@click.option('--backend', "backend", help="Set a backend to be used, choices are grpc and rest. Default is grpc.", type=click.Choice(['grpc', 'rest']), default = "grpc")
@click.option('--grpc-server', "grpc_server", help="Set a host and port of the gRPC server. Default is localhost:50051.", default="localhost:50051")
@click.option('--base-url', "base_url", help="Set a base URL for a REST server. Default is localhost:8000", default="localhost:8000")
@click.option('--output', "output", help="Set the file where to store the output. Default is -, i.e. the stdout.", type=click.File('wb'), default="-")
def cli(backend, grpc_server, base_url, output, method, uuid):
    if backend == "rest": # if I will do it in production, I will care more about exeptions messages here, but grpc backend has it nicer ;)
        if method == "stat":
            print(stat_rest(base_url, uuid))
        elif method == "read":
            file = read_rest(base_url, uuid)
            if isinstance(file, bytes):
                output.write(file)
            else:
                print(file)
    elif backend == "grpc": # I don't like just else here
        if method == "stat":
            print(stat_grpc(grpc_server, uuid))
        elif method == "read":
            try:
                for chunk in read_grpc(grpc_server, uuid):
                    if not chunk.data.data:
                        break
                    output.write(chunk.data.data)
            # because of generator on other side and because of click.File ReadBuffer is for me easier to handle exceptions here
            except grpc.RpcError as rpc_error:
                if (rpc_error.code() == grpc.StatusCode.UNAVAILABLE
                or rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT
                or rpc_error.code() == grpc.StatusCode.FAILED_PRECONDITION
                or rpc_error.code() == grpc.StatusCode.NOT_FOUND):
                    print(rpc_error.details())
                else:
                    print(f"Received unknown RPC error: code={rpc_error.code()} message={rpc_error.details()}")
