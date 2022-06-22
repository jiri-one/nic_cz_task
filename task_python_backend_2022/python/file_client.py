from os import write
from shutil import which
import requests
import click


def stat(server, UUID):
    try:
        resp = requests.get(f"http://{server}/file/{UUID}/stat/")
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
        return resp.reason


def read(server, UUID):
    """I left this function really simple, but the main bug is, that you can download content from whole internet :-)"""
    try:
        resp = requests.get(f"http://{server}/file/{UUID}/read/")
    except requests.ConnectionError:
        return print("Connection error")
    return resp.content


@click.command(no_args_is_help=True)
@click.argument('method', type=click.Choice(['stat', 'read']))
@click.argument('UUID')
@click.option('--backend', "backend", help="Set a backend to be used, choices are grpc and rest. Default is grpc.", default="grpc")
@click.option('--grpc-server', "grpc_server", help="Set a host and port of the gRPC server. Default is localhost:50051.", default="localhost:50051")
@click.option('--base-url', "base_url", help="Set a base URL for a REST server. Default is localhost:8000", default="localhost:8000")
@click.option('--output', "output", help="Set the file where to store the output. Default is -, i.e. the stdout.", type=click.File('wb'), default="-")
def cli(backend, grpc_server, base_url, output, method, uuid):
    if backend == "rest":
        if method == "stat":
            print(stat(base_url, uuid))
        elif method == "read":
            file = read(base_url, uuid)
            output.write(file)
    else:
        print("grpc backend is not implemented yet, try rest backend.")

if __name__ == '__main__':
    cli()
