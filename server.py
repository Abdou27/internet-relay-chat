import json
import re
import socket
import sys
import threading
import time
from exceptions import NameAlreadyTaken, UserExited

servername = sys.argv[1]
servers = sys.argv[2:]  # don't know what to do with this x)

HOST = "127.0.0.1"
PORT = int(servername)
LOGGING = True
HELP = """
/away "{message}"                   Signale son absence quand on nous envoie un message en privé
                                    (une réponse au message peut être envoyé).
                                    Une nouvelle commande /away réactive l’utilisateur.
/help                               Affiche la liste des commandes disponibles.
/invite "{nick}"                    Invite un utilisateur sur le canal o`u on se trouve
/join "{canal}" "{clé}"             Permet de rejoindre un canal (protégé éventuellement par une clé).
                                    Le canal est créé s’il n’existe pas.
/list                               Affiche la liste des canaux sur IRC.
/msg "{canal|nick}" "{message}"     Pour envoyer un message à un utilisateur ou sur un canal (où on est
                                    présent ou pas). Les arguments canal ou nick sont optionnels.
/names "{canal}"                    Affiche les utilisateurs connectés à un canal. Si le canal n’est pas spécifié,
                                    affiche tous les utilisateurs de tous les canaux.
/exit                               Pour quitter le serveur IRC proprement.
"""
channels = {}
users = {}


def handle_cmd(cmd, name):
    user = users[name]
    conn = user["conn"]
    exit_cmd = re.match(r"^/exit\b\s*$", cmd)
    help_cmd = re.match(r"^\s*/help\s*$", cmd)
    away_cmd = re.match(r"^\s*/away\b\s+\"((?:[^\"\\]|\\.)*)\"\s*$", cmd)
    invite_cmd = re.match(r"^\s*/invite\b\s+\"((?:[^\"\\]|\\.)*)\"\s*$", cmd)
    msg_cmd = re.match(r"^\s*/msg\b(?:\s+\"((?:[^\"\\]|\\.)*)\")?\s+\"((?:[^\"\\]|\\.)*)\"\s*$", cmd)
    if exit_cmd:
        raise UserExited(name)
    elif help_cmd:
        conn.send(HELP.encode())
    elif away_cmd:
        message = away_cmd.group(1)
        user["away"] = not user["away"]
        if user["away"]:
            user["away_msg"] = message if not re.match(r"^\s*$", message) else "Cet utilisateur est absent."
            away_message = f" Votre message d'absence est:\n{user['away_msg']}"
        else:
            user["away_msg"] = None
            away_message = ""
        status = "absent" if user["away"] else "présent"
        conn.send(f"Vous êtes désormais marqué comme {status}.{away_message}".encode())
    elif invite_cmd:
        invited_user = invite_cmd.group(1)
        invite_channel = user["channel"]
        key = channels[invite_channel]["key"] if "key" in channels[invite_channel].keys() else None
        key_msg = f" Clé : {key}" if key else ""
        message = f"{name} vous a invité au canal {invite_channel}.{key_msg}"
        with users[invited_user]["conn"] as invited_user_conn:
            invited_user_conn.send(message.encode())
    elif msg_cmd:
        nick_or_channel = invite_cmd.group(1)
        message = invite_cmd.group(2)
        pass


def handle_conn(conn, addr):
    try:
        with conn:
            conn.send(f"Connecté à {servername}".encode())
            name = conn.recv(1024).decode()
            if name in users.keys():
                conn.send("/__NameAlreadyTaken".encode())
                raise NameAlreadyTaken(name, addr)
            users[name] = {
                "addr": addr,
                "conn": conn,
                "away": False,
                "away_msg": None,
                "channel": None,
            }
            print(f"\r{name} a connecté depuis {addr}.")
            while True:
                data = conn.recv(1024)
                data = data.decode()
                if LOGGING:
                    print(f"Données reçues depuis {name} :\t{data}")
                handle_cmd(data, name)
    except ConnectionResetError:
        identifier = name if name else addr
        print(f"\rConnexion perdue avec {identifier}")
    except NameAlreadyTaken as e:
        message = json.dumps({
            "type": "NameAlreadyTaken",
            "name": e.name,
            "addr": e.addr,
        })
        with conn:
            conn.send(message.encode())
        print(e.get_server_message())
    except UserExited as e:
        print(e.get_server_message())


def accept_connections(s):
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_conn, args=(conn, addr), daemon=True).start()


try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1024)
        print("Le serveur est opérationnel et à l'écoute !")
        threading.Thread(target=accept_connections, args=(s,), daemon=True).start()
        should_exit = input("Sortir ? [y|N] : ")
        while should_exit.lower() != "y":
            should_exit = input("Sortir ? [y|N] : ")
        print("Le serveur a été arrêté.")
except KeyboardInterrupt:
    print("Le serveur a été arrêté.")
