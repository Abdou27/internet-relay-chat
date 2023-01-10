import threading
import time
from Server import Server
from Client import Client


def server():
    try:
        s = Server(port=65432, lang="en", logging_level=1)
        s.launch()
    except Exception as e:
        print(e)


def client(name):
    try:
        c = Client(nickname=name, server_name="65432", port=65432, lang="en", logging_level=1)
        c.open_connection()
    except Exception as e:
        print(e)


threading.Thread(target=server).start()
time.sleep(1)
threading.Thread(target=client, args=("Rahim",)).start()
time.sleep(1)
threading.Thread(target=client, args=("Maha",)).start()
