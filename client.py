import json
import os
import socket
import threading
import time

from ChatGUI import ChatGUI
import sys

nickname = sys.argv[1]
servername = sys.argv[2]

HOST = "127.0.0.1"
PORT = int(servername)
MAX_RECV_SIZE = 1024**2


def handle_conn(window):
    window.socket.send(nickname.encode())
    try:
        while True:
            data = window.socket.recv(MAX_RECV_SIZE).decode()
            data = json.loads(data)
            if data["type"] == "NameAlreadyTaken":
                print("Ce nom d'utilisateur est déjà pris.")
                window.destroy()
            elif data["type"] == "msg":
                sender = data["sender"]
                window.add_message(f"{sender} : {data}")
    except ConnectionResetError:
        print(f"Connexion perdue avec le serveur {servername}")
        window.destroy()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((HOST, PORT))
    window = ChatGUI(title=f"{nickname} - {servername}", socket=s)
    threading.Thread(target=handle_conn, args=(window,), daemon=True).start()
    window.mainloop()
