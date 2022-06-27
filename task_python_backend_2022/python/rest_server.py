import falcon
from uuid import UUID
import json
from os import stat
import mimetypes
from datetime import datetime

files_db = {
    # "UUID": "file name"
    UUID('10fe4a26-e33d-4856-917d-32e7e703c97b'): "flag_cze.svg",
    UUID('e80c7f36-fe72-4bf1-a9b0-c4cd6b762af4'): "gish.xpm",
    UUID('65ba8687-9b44-4e10-b334-da9b98abcd20'): "smile.png",
}

mimetypes.init()

class RestResource(object):
    def on_get_stat(self, req, resp, file):
        try:
            file_name = files_db[file]
            file_stats = stat(f"files/{file_name}")
        except KeyError:
            raise falcon.HTTPNotFound(title="UUID not found")
        except FileNotFoundError:
            raise falcon.HTTPNotFound(title="File not found")
        # equivalent of 'grpc.StatusCode.INVALID_ARGUMENT, "UUID is invalid"' is here handled by Falcon and is returned '404 Not Found'
        try:
            mimetype = mimetypes.types_map[f".{file_name.split('.')[-1]}"]
        except KeyError:
            mimetype = "Unknown"
        resp.status = "200 OK"
        resp.set_header('Content-Type', 'application/json')
        file_info = {
            "name": file_name,
            "size": file_stats.st_size,
            "mimetype": mimetype,
            "create_datetime": datetime.fromtimestamp(file_stats.st_mtime).isoformat(" ", "seconds")
        }
        resp.text = json.dumps(file_info)

    def on_get_read(self, req, resp, file):
        try:
            file_name = files_db[file]
            resp.stream = open(f"files/{file_name}", "rb")
        except KeyError:
            raise falcon.HTTPNotFound(title="UUID not found")
        except FileNotFoundError:
            raise falcon.HTTPNotFound(title="File not found")
        # equivalent of 'grpc.StatusCode.INVALID_ARGUMENT, "UUID is invalid"' is here handled by Falcon and is returned '404 Not Found'
        try:
            mimetype = mimetypes.types_map[f".{file_name.split('.')[-1]}"]
        except KeyError:
            mimetype = "Unknown"
        resp.status = "200 OK"
        resp.set_header('Content-Disposition', file_name)
        resp.set_header('Content-Type', mimetype)


app = falcon.App(media_type=falcon.MEDIA_JSON)

rest_resource = RestResource()
app.add_route("/file/{file:uuid}/stat/", rest_resource, suffix="stat")
app.add_route("/file/{file:uuid}/read/", rest_resource, suffix="read")


def local_run():
    from hupper import start_reloader
    from waitress import serve
    reloader = start_reloader("rest_server.local_run")
    serve(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    local_run()
