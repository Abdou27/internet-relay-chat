import re
import tkinter as tk
import json
import os
import socket
import threading
import time
import sys

from translations import Translations
from exceptions import NameAlreadyTaken

MAX_WIDTH = 800
MAX_HEIGHT = 800


class Client(tk.Tk):
    def __init__(self, **options):
        # Client setup
        self.socket = None
        self.max_recv_size = options.get("max_recv_size", 1024)
        self.nickname = options.get("nickname", "John Doe")
        self.host = options.get("host", "127.0.0.1")
        self.port = options.get("port", 65432)
        self.server_name = options.get("server_name", str(self.port))
        self.lang = options.get("lang", "en")
        self.T = Translations(lang=self.lang)
        self.logging_level = options.get("logging_level", 2)
        # GUI Setup
        super().__init__()
        self.set_window_properties(options)
        self.input_content = tk.StringVar()
        self.input_box, self.text_box_frame, self.text_box, self.scrollbar = (None,) * 4
        self.init_input_box()
        self.init_text_box()

    def set_window_properties(self, options):
        self.title(options.get("title", f"{self.nickname} - {self.server_name}"))
        self.protocol("WM_DELETE_WINDOW", self.close_connection)
        self.set_geometry()

    def set_geometry(self):
        width = int(self.winfo_screenwidth() - 200)
        width = MAX_WIDTH if width > MAX_WIDTH else width
        height = int(self.winfo_screenheight() - 200)
        height = MAX_HEIGHT if height > MAX_HEIGHT else height
        self.geometry(f"{width}x{height}+100+100")

    def init_input_box(self):
        self.input_box = tk.Entry(self, textvariable=self.input_content)
        self.input_box.bind("<Return>", self.submit_message)
        self.input_box.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.input_box.focus_set()
        self.bind("<1>", lambda x: self.input_box.focus_set())

    def init_text_box(self):
        self.text_box_frame = tk.Frame(self)
        self.text_box_frame.pack(fill=tk.BOTH, expand=True)
        self.text_box_frame.pack_propagate(False)
        self.text_box = tk.Text(self.text_box_frame, background="black", foreground="white", state=tk.NORMAL)
        self.text_box.delete("0.0", tk.END)
        self.scrollbar = tk.Scrollbar(self.text_box_frame, command=self.text_box.yview, orient=tk.VERTICAL)
        self.text_box['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_box.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

    def open_connection(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.connect((self.host, self.port))
            threading.Thread(target=self.handle_conn, daemon=True).start()
            self.mainloop()
        except KeyboardInterrupt:
            print(self.T.get("closing_connection_to_server"))
            self.close_connection()

    def handle_conn(self):
        self.socket.send(self.nickname.encode())
        try:
            while True:
                data = self.socket.recv(self.max_recv_size).decode()
                if self.logging_level >= 2:
                    print(self.T.data_received_from(servername, data))
                data = json.loads(data)
                data_type = data.get("type", "ServerMessage")
                if data_type == "NameAlreadyTaken":
                    raise NameAlreadyTaken(data["name"], data["addr"], self.T)
                elif data_type == "ServerMessage":
                    self.add_message(data["msg"])
                elif data_type == "UserMessage":
                    sender = data["sender"]
                    message = data["msg"]
                    self.add_message(f"{sender} : {message}")
        except ConnectionResetError:
            if self.logging_level >= 0:
                print(self.T.connection_lost_with_server(self.server_name))
        except NameAlreadyTaken as e:
            if self.logging_level >= 0:
                print(e.get_client_message())
        finally:
            self.socket.close()
            self.destroy()

    def add_message(self, message):
        self.text_box["state"] = tk.NORMAL
        self.text_box.insert(tk.END, message + "\n")
        self.text_box["state"] = tk.DISABLED
        self.text_box.see(tk.END)

    def submit_message(self, _):
        input_content = self.input_content.get()
        self.input_content.set("")
        self.add_message("> " + input_content)
        self.socket.send(input_content.encode())
        if re.match(r"^\s*/exit\s*$", input_content):
            self.socket.close()
            self.destroy()

    def close_connection(self):
        self.socket.send("/exit".encode())
        self.socket.close()
        self.destroy()


if __name__ == "__main__":
    nickname = sys.argv[1]
    servername = sys.argv[2]
    port = int(servername)
    client = Client(nickname=nickname, server_name=servername, port=port, lang="en", logging_level=2)
    client.open_connection()
