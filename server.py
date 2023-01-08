import json
import re
import socket
import sys
import threading
import time
from exceptions import NameAlreadyTaken

servername = sys.argv[1]
servers = sys.argv[2:]  # don't know what to do with this x)

HOST = "127.0.0.1"
PORT = int(servername)
LOGGING = True
HELP = """
/away [message]  Signale son absence quand on nous envoie un message en privé
                 (une réponse au message peut être envoyé).
                 Une nouvelle commande /away réactive l’utilisateur.
/help  Affiche la liste des commandes disponibles.
/invite <nick> Invite un utilisateur sur le canal o`u on se trouve
/join <canal> [clé]  Permet de rejoindre un canal (protégé éventuellement par une clé).
                     Le canal est créé s’il n’existe pas.
/list  Affiche la liste des canaux sur IRC.
/msg [canal|nick] message  Pour envoyer un message à un utilisateur ou sur un canal (où on est
                           présent ou pas). Les arguments canal ou nick sont optionnels.
/names [channel]  Affiche les utilisateurs connectés à un canal. Si le canal n’est pas spécifié,
                  affiche tous les utilisateurs de tous les canaux.
/exit  Pour quitter le serveur IRC proprement.
""".encode('utf-8')
channels = {}
individual_conns = {}
individual_names = {}
away_list = {}
away_messages = {}
users = {}


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
                "current_channel": None,
            }
            individual_names[addr] = name
            individual_conns[name] = conn
            away_list[name] = False
            away_messages[name] = None
            print(f"\r{name} connecté depuis {addr}")
            while True:
                data = conn.recv(1024)
                data = data.decode()
                if LOGGING:
                    print(f"Données reçues depuis {addr} : {data}")
                exit_cmd = re.match(r"^/exit\b\s*$", data)
                help_cmd = re.match(r"^/help\b\s*$", data)
                away_cmd = re.match(r"^/away\b\s*(\w[\w\s]*)*$", data)
                invite_cmd = re.match(r"^/invite\b\s+(\w[\w\s]*)+$", data)
                msg_cmd = re.match(r"^/msg\b\s*([^\s]*)\s*([^\s]*)", data)
                if exit_cmd:
                    print(f"\r{name} a fermé la connexion.")
                    break
                elif help_cmd:
                    conn.send(HELP)
                elif away_cmd:
                    message = away_cmd.group(1)
                    away_list[addr] = not away_list[addr]
                    if away_list[addr]:
                        away_messages[addr] = message if message != "" else "Cet utilisateur est absent."
                        away_message = f" Votre message d'absence est:\n{away_messages[addr]}"
                    else:
                        away_messages[addr] = None
                        away_message = ""
                    status = "absent" if away_list[addr] else "présent"
                    conn.send(f"Vous êtes désormais marqué comme {status}.{away_message}".encode())
                elif invite_cmd:
                    invited_user = invite_cmd.group(1)
                    invite_channel = users[name]["channel"]
                    key = channels[invite_channel]["key"] if "key" in channels[invite_channel].keys() else None
                    key_msg = f" Clé : {key}" if key else ""
                    message = f"{name} vous a invité au canal {invite_channel}.{key_msg}"
                    conn.send(message.encode())
                else:
                    for ind_addr, ind_conn in individual_conns.items():
                        if addr == ind_addr:
                            continue
                        message = name + " : " + data
                        ind_conn.send(message.encode())
    except ConnectionResetError:
        print(f"\rConnexion perdue avec {individual_names[addr]}")
    except NameAlreadyTaken as inst:
        message = json.dumps({
            "type": "NameAlreadyTaken",
            "name": inst.name,
            "addr": inst.addr,
        })
        with conn:
            conn.send(message.encode())
        print(inst.get_server_message())


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
