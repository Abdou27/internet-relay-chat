import socket
import sys
import threading
import time

servername = sys.argv[1]
servers = sys.argv[2:]  # don't know what to do with this x)

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = int(servername)  # Port to listen on (non-privileged ports are > 1023)
HELP = """
/away [message]  Signale son absence quand on nous envoie un message en privé
                 (en réponse un message peut être envoyé).
                 Une nouvelle commande /away réactive l’utilisateur.
/help  Affiche la liste des commandes disponibles.
/invite <nick>  Invite un utilisateur sur le canal où on se trouve.
/join <canal> [clé]  Permet de rejoindre un canal (protégé éventuellement par une clé).
                     Le canal est créé s’il n’existe pas.
/list  Affiche la liste des canaux sur IRC.
/msg [canal|nick] message  Pour envoyer un message à un utilisateur ou sur un canal (où on est
                           présent ou pas). Les arguments canal ou nick sont optionnels.
/names [channel]  Affiche les utilisateurs connectés à un canal. Si le canal n’est pas spécifié,
                  affiche tous les utilisateurs de tous les canaux.
/exit  Pour quitter le serveur IRC proprement.
""".encode('utf-8')
groups = {}
individual_conns = {}
individual_names = {}


def handle_conn(conn, addr):
    individual_conns[addr] = conn
    with conn:
        conn.send("BATATA".encode())
        individual_names[addr] = conn.recv(1024).decode()
        print(f"{individual_names[addr]} connected from {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            data = data.decode()
            for ind_addr, ind_conn in individual_conns.items():
                if addr == ind_addr:
                    continue
                message = individual_names[addr] + " : " + data
                ind_conn.send(message.encode())


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print("Server launched and listening !")
    while True:
        conn, addr = s.accept()
        # threading.Thread(target=handle_conn, args=(conn, addr)).start()
        individual_conns[addr] = conn
        with conn:
            conn.send("BATATA".encode())
            individual_names[addr] = conn.recv(1024).decode()
            print(f"{individual_names[addr]} connected from {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                data = data.decode()
                for ind_addr, ind_conn in individual_conns.items():
                    if addr == ind_addr:
                        continue
                    message = individual_names[addr] + " : " + data
                    ind_conn.send(message.encode())
