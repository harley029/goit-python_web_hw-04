from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import urllib.parse
import mimetypes
import socket
import json
import logging
from threading import Thread
from datetime import datetime

BASE_DIR = Path()
BUFFER_SIZE = 1024
HTTP_HOST = "0.0.0.0" # для Докер контейнера
HTTP_PORT = 3000
SOCKET_HOST_UDP = socket.gethostname()
SOCKET_PORT_UDP = 5000


class MyFirstServer(BaseHTTPRequestHandler):

    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        # print(route.path) - перевірка шляхив
        match route.path:
            case "/":
                self.sent_HTML("index.html")
            case "/message":
                self.sent_HTML("message.html")
            case _:
                file = BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.sent_static(file)
                else:
                    self.sent_HTML(file_name="error.html", status_code=404)

    def do_POST(self):
        size = self.headers["Content-Length"]
        data = self.rfile.read(int(size))

        # ----------------- відправка повідомлення в сокет -----------------
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SOCKET_HOST_UDP, SOCKET_PORT_UDP)) 
        client_socket.close()
       
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def sent_HTML(self, file_name, status_code=200):
        self.send_response(status_code)
        self.send_header(keyword="Content-type", value="text/html")
        self.end_headers()
        with open(file_name, "rb") as file:
            self.wfile.write(file.read())

    def sent_static(self, file_name, status_code=200):
        self.send_response(status_code)
        mime_type = mimetypes.guess_type(file_name)[0]
        if mime_type:
            self.send_header(keyword="Content-type", value=mime_type)
        else:
            self.send_header(keyword="Content-type", value="twxt/plain")
        self.end_headers()
        with open(file_name, "rb") as file:
            self.wfile.write(file.read())

def save_data_from_socket(data):
    data_parse = urllib.parse.unquote_plus(data.decode())
    data_dict = {key: value for key, value in [el.split("=") for el in data_parse.split("&")]}
    # -------------- зчитування файлу data.json та допис повідомлення ---------------
    with open('storage/data.json', 'r', encoding='utf-8') as file:
        current_data=json.load(file)
        current_data[str(datetime.now())]=data_dict
    # -------------- записування в файл data.json ---------------
    with open('storage/data.json', 'w', encoding='utf-8') as file:
        json.dump(current_data, file, ensure_ascii=False, indent=4)


def run_socket_server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = host, port
    sock.bind(server)
    logging.info(f"Socket Server is running on {host}:{port}")
    try:
        while True:
            data, address = sock.recvfrom(BUFFER_SIZE)
            save_data_from_socket(data)
    except KeyboardInterrupt:
        logging.info(f"Socket server is stopped")
    finally:
        sock.close()

def run_HTTP_server(host, port):
    adress = (host, port)
    http_server = HTTPServer(adress, MyFirstServer)
    logging.info(f"HTTP Server is running on {host}:{port}")
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

    server = Thread(target=run_HTTP_server, args=(HTTP_HOST, HTTP_PORT))
    server.start()

    socket_server=Thread(target=run_socket_server, args=(SOCKET_HOST_UDP, SOCKET_PORT_UDP))
    socket_server.start()
