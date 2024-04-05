from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import urllib.parse
import mimetypes
import socket

BASE_DIR = Path()
# UDP_IP = "127.0.0.1"  - якщо стартують на різних компах, вказати реальні ІР
UDP_IP=socket.gethostname()
UDP_PORT = 5000


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
        size=self.headers["Content-Length"] # розмір вхідного повідомлення (скільки читати) 
        data = self.rfile.read(int(size)) # читаємо вхідний повідомлення
        # ----------------- відправка повідомлення в сокет -----------------
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # создаємо сокет
        server = UDP_IP, UDP_PORT # підднуємось до серверу
        sock.sendto(data, server) # надсилаємо дані в сокет
        sock.close() # закриваємо сокет
        # ----------------- декодування повідомлення на сервері -----------------
        # data_parse = urllib.parse.unquote_plus(data.decode())
        # print(data_parse)
        # data_dict = {key: value for key, value in [el.split("=") for el in data_parse.split("&")]}
        # print(data_dict)
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


def run_server():
    adress = ("localhost", 3000)
    http_server = HTTPServer(adress, MyFirstServer)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()


if __name__ == "__main__":
    run_server()
