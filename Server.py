import json
import re
import socket
import sys
import threading
import time
from exceptions import NameAlreadyTaken, UserExited
from Translations import Translations


class Server:
    def __init__(self, **options):
        self.channels = {}
        self.users = {}
        self.lock = threading.Lock()
        self.max_listens = options.get("max_listens", 1024)
        self.host = options.get("host", "127.0.0.1")
        self.port = options.get("port", 65432)
        self.server_name = options.get("server_name", str(self.port))
        self.lang = options.get("lang", "en")
        self.T = Translations(lang=self.lang)
        self.logging_level = options.get("logging_level", 2)

    def launch(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, self.port))
                s.listen(self.max_listens)
                threading.Thread(target=self.accept_connections, args=(s,), daemon=True).start()
                self.wait()
        except KeyboardInterrupt:
            print(self.T.get("server_has_been_stopped"))

    def wait(self):
        while True:
            pass

    def accept_connections(self, s):
        if self.logging_level >= 1:
            print(self.T.get("server_is_listening"))
        while True:
            conn, addr = s.accept()
            threading.Thread(target=self.handle_conn, args=(conn, addr), daemon=True).start()

    def handle_conn(self, conn, addr):
        try:
            with conn:
                conn.send(self.T.connected_to(self.server_name).encode())
                name = conn.recv(1024).decode()
                with self.lock:
                    if name in self.users or name in self.channels:
                        raise NameAlreadyTaken(name, addr)
                    self.users[name] = {
                        "addr": addr,
                        "conn": conn,
                        "away": False,
                        "away_msg": None,
                        "channel": None,
                    }
                if self.logging_level >= 1:
                    print(self.T.user_connected_from(name, addr))
                while True:
                    data = conn.recv(1024)
                    data = data.decode()
                    if self.logging_level >= 2:
                        print(self.T.data_received_from(name, data))
                    threading.Thread(target=self.handle_cmd, args=(data, name)).start()
        except ConnectionResetError:
            identifier = name if name else addr
            if self.logging_level >= 0:
                print(self.T.connection_lost(identifier))
        except NameAlreadyTaken as e:
            message = json.dumps({
                "type": "NameAlreadyTaken",
                "name": e.name,
                "addr": e.addr,
            })
            with conn:
                conn.send(message.encode())
            if self.logging_level >= 0:
                print(e.get_server_message())
        except UserExited as e:
            if self.logging_level >= 0:
                print(e.get_server_message())
        finally:
            with self.lock:
                if name in self.users:
                    del self.users[name]

    def handle_cmd(self, cmd, name):
        user = self.users[name]
        conn = user["conn"]
        if exit_cmd := re.match(r"^/exit\b\s*$", cmd):
            raise UserExited(name)
        elif help_cmd := re.match(r"^\s*/help\s*$", cmd):
            conn.send(self.T.get("help_msg").encode())
        elif list_cmd := re.match(r"^\s*/list\s*$", cmd):
            channels = list(self.channels.keys())
            conn.send(self.T.list_cmd_response(channels).encode())
        elif away_cmd := re.match(r"^\s*/away\b\s+\"((?:[^\"\\]|\\.)*)\"\s*$", cmd):
            self.handle_away_cmd(away_cmd, conn, user, name)
        elif invite_cmd := re.match(r"^\s*/invite\b\s+\"((?:[^\"\\]|\\.)*)\"\s*$", cmd):
            self.handle_invite_cmd(invite_cmd, conn, user, name)
        elif names_cmd := re.match(r"^\s*/names\b(?:\s+\"((?:[^\"\\]|\\.)*)\")?\s*$", cmd):
            self.handle_names_cmd(names_cmd, conn, user, name)
        elif msg_cmd := re.match(r"^\s*/msg\b(?:\s+\"((?:[^\"\\]|\\.)*)\")?\s+\"((?:[^\"\\]|\\.)*)\"\s*$", cmd):
            self.handle_msg_cmd(msg_cmd, conn, user, name)
        elif join_cmd := re.match(r"^\s*/join\b\s+\"((?:[^\"\\]|\\.)*)\"(?:\s+\"((?:[^\"\\]|\\.)*)\")?\s*$", cmd):
            self.handle_join_cmd(join_cmd, conn, user, name)

    def handle_away_cmd(self, away_cmd, conn, user, name):
        message = away_cmd.group(1)
        user["away"] = not user["away"]
        user["away_msg"] = None
        if user["away"]:
            user["away_msg"] = message if not re.match(r"^\s*$", message) else self.T.get("user_absent")
        conn.send(self.T.away_cmd_response(user["away"], user["away_msg"]).encode())

    def handle_invite_cmd(self, invite_cmd, conn, user, name):
        invited_user = invite_cmd.group(1)
        with self.lock:
            if invited_user not in self.users:
                conn.send(self.T.get("user_does_not_exist").encode())
                return
            invite_channel = user["channel"]
            key = self.channels[invite_channel].get("key")
            with self.users[invited_user]["conn"] as invited_user_conn:
                invited_user_conn.send(self.T.invite_cmd_response(name, invite_channel, key).encode())

    def handle_names_cmd(self, names_cmd, conn, user, name):
        channel_name = names_cmd.group(1)
        found_users = []
        with self.lock:
            if channel_name is not None:
                if channel_name not in self.channels:
                    conn.send(self.T.get("channel_does_not_exist").encode())
                    return
                for user_name, user in self.users.items():
                    if user['channel'] == channel_name:
                        found_users.append(user_name)
            else:
                for user_name, user in self.users.items():
                    found_users.append(user_name)
        conn.send(self.T.names_cmd_response(channel_name, found_users).encode())

    def handle_msg_cmd(self, msg_cmd, conn, user, name):
        nick_or_channel = msg_cmd.group(1)
        message = msg_cmd.group(2)
        with self.lock:
            if nick_or_channel != "" and nick_or_channel not in self.channels and nick_or_channel not in self.users:
                conn.send(self.T.get("user_or_channel_does_not_exist").encode())
                return
            if nick_or_channel == "":
                nick_or_channel = user["channel"]
            is_channel = nick_or_channel in self.channels
            if is_channel:
                for user in self.users.values():
                    if user["channel"] != nick_or_channel:
                        continue
                    with user["conn"] as recipient_conn:
                        recipient_conn.send(self.T.msg_cmd(name, message).encode())
            else:
                with self.users[nick_or_channel]["conn"] as recipient_conn:
                    recipient_conn.send(self.T.msg_cmd(name, message).encode())

    def handle_join_cmd(self, join_cmd, conn, user, name):
        channel_name = join_cmd.group(1)
        key = join_cmd.group(2)
        with self.lock:
            if channel_name in self.channels:
                channel = self.channels[channel_name]
                channel_key = channel.get("key")
                if channel_key is not None and channel_key != key:
                    conn.send(self.T.get("incorrect_key").encode())
                    return
            else:
                self.channels[channel_name] = {
                    "key": key,
                }
            user["channel"] = channel_name


if __name__ == "__main__":
    servername = sys.argv[1]
    servers = sys.argv[2:]  # don't know what to do with this x)
    port = int(servername)
    server = Server(port=port, lang="en", logging_level=1)
    server.launch()
