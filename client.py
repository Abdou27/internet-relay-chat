import socket
import threading

from ChatGUI import ChatGUI
import sys

nickname = sys.argv[1]
servername = sys.argv[2]

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


def handle_conn(window):
    window.socket.send(nickname.encode())
    while True:
        data = window.socket.recv(1024).decode()
        window.add_message(data)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((HOST, PORT))
    window = ChatGUI(title=f"{nickname} - {servername}", socket=s)
    # threading.Thread(target=handle_conn, args=(window,)).start()
    window.socket.send(nickname.encode())
    while True:
        data = window.socket.recv(1024).decode()
        window.add_message(data)
    window.mainloop()
