import socket
import urllib.parse
import json
from datetime import datetime

# UDP_IP = "127.0.0.1" - якщо стартують на різних компах, вказати реальні ІР
UDP_IP=socket.gethostname()
UDP_PORT = 5000


def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            # ------------- отримання та розкодування повідомлення ---------------
            data = sock.recv(1024)
            data_parse = urllib.parse.unquote_plus(data.decode())
            data_dict = {key: value for key, value in [el.split("=") for el in data_parse.split("&")]}
            # -------------- зчитування файлу data.json та допис повідомлення ---------------
            with open('storage/data.json', 'r', encoding='utf-8') as file:
                current_data=json.load(file)
                current_data[str(datetime.now())]=data_dict
            # -------------- записування в файл data.json ---------------
            with open('storage/data.json', 'w', encoding='utf-8') as file:
                json.dump(current_data, file, ensure_ascii=False, indent=4)
                # json.dump({current_time:data_dict}, file, ensure_ascii=False, indent=4)
    except KeyboardInterrupt:
            print(f"Destroy server")
    finally:
        sock.close()


if __name__ == "__main__":
    run_server(UDP_IP, UDP_PORT)
