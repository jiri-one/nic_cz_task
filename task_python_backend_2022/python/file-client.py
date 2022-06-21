from os import write
from shutil import which
import requests
import click

SERVER = "localhost:8000" # adress without http:// and with port if is not 80

def stat(server, UUID):
    try:
        resp = requests.get(f"http://{server}/file/{UUID}/stat/")
    except requests.ConnectionError:
        print("Connection error")
    if resp.status_code == 200:
        data = resp.json()
        return f"""
        Information about file:
        File name is: {data["name"]}
        File size in bytes is: {data["size"]}
        File mimetype is: {data["mimetype"]}
        File was created at (different on every OS): {data["create_datetime"]}\n
        """
    else:
        print(resp.reason)

def read(server, UUID):
    try:
        resp = requests.get(f"http://{server}/file/{UUID}/read/")
    except requests.ConnectionError:
        print("Connection error")
    return resp.content

@click.command()
@click.argument('method', type=click.Choice(['stat', 'read']))
@click.argument('UUID')
@click.option('--backend', "backend", help="Set a backend to be used, choices are grpc and rest. Default is grpc.", default="grpc")
@click.option('--grpc-server', "grpc_server", help="Set a host and port of the gRPC server. Default is localhost:50051.", default="localhost:50051")
@click.option('--base-url', "base_url", help="Set a base URL for a REST server. Default is localhost:8000", default="localhost:8000")
@click.option('--output', "output", help="Set the file where to store the output. Default is the stdout.", default="stdout")
def cli(backend, grpc_server, base_url, output, method, uuid):
    if backend == "rest":
        if method == "stat":
            print(stat(base_url, uuid))
        elif method == "read":
            if output == "stdout":
                print(read(base_url, uuid))
            else:
                with open(output, "wb") as f:
                    f.write(read(base_url, uuid))
    else:
        print("Not implemented yet")

if __name__ == '__main__':
    cli()
