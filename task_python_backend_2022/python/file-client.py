import requests
import click

SERVER = "localhost:8000" # adress without http:// and with port if is not 80

def get_file_stats(server, file):    
    try:
        resp = requests.get(f"http://{server}/file/{file}/stat/")
    except requests.ConnectionError:
        print("Connection error")
    data = resp.json()
    return f"""
    Information about file:\n
    File name is: {data["name"]}\n
    File size in bytes is: {data["size"]}\n
    File mimetype is: {data["mimetype"]}\n
    File was created at: {data["create_datetime"]}\n
    """

def get_file_bytes(server, file):
    try:
        resp = requests.get(f"http://{server}/file/{file}/read/")
    except requests.ConnectionError:
        print("Connection error")
    return resp.content



print(get_file_bytes(SERVER, "10fe4a26-e33d-4856-917d-32e7e703c97b"))
