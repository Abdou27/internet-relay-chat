class Translations:
    _texts = {
        "": {
            "fr": "",
            "en": "",
        },
        "server_is_listening": {
            "fr": "Le serveur est opérationnel et à l'écoute !",
            "en": "The server is operational and listening !",
        },
        "user_absent": {
            "fr": "Cet utilisateur est absent.",
            "en": "This user is absent.",
        },
        "user_does_not_exist": {
            "fr": "Cet utilisateur n'existe pas.",
            "en": "This user doesn't exist.",
        },
        "channel_does_not_exist": {
            "fr": "Ce canal n'existe pas.",
            "en": "This channel doesn't exist.",
        },
        "user_or_channel_does_not_exist": {
            "fr": "Cet utilisateur ou canal n'existe pas.",
            "en": "This user or channel doesn't exist.",
        },
        "incorrect_key": {
            "fr": "La clé entrée est incorrecte.",
            "en": "The input key is incorrect.",
        },
        "server_has_been_stopped": {
            "fr": "Le serveur a été arrêté.",
            "en": "The server has been stopped.",
        },
        "help_msg": {
            "fr": """
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
""",
            "en": """
/away "{message}"                   Signals our absence when we are sent a private message
                                    (a reply to the message can be sent).
                                    A new /away command reactivates the user.
/help                               Displays the list of available commands.
/invite "{nick}"                    Invite a user to the current channel
/join "{channel}" "{key}"           Joins a channel (possibly protected by a key).
                                    The channel is created if it does not exist.
/list                               Displays the list of channels on IRC.
/msg "{channel|nick}" "{message}"   To send a message to a user or on a channel 
                                    (whether present in said channel or not). 
                                    The channel or nick arguments are optional.
/names "{channel}"                  Displays users connected to a channel. If the channel is not specified,
                                    displays all users of all channels.
/exit                               To exit the IRC server properly.
""",
        },
    }

    def __init__(self, lang):
        self.lang = lang

    def get(self, text_id: str) -> str:
        if text_id not in self._texts:
            return "UNKNOWN_TEXT_ID"
        text_by_lang = self._texts[text_id]
        if self.lang in text_by_lang:
            text = text_by_lang[self.lang]
        else:
            print(f"{text_id} is not available in {self.lang}, defaulting to another language.")
            text = list(text_by_lang.values())[0]
        return text

    def same_name_connection_refused(self, name: str, addr: tuple) -> str:
        if self.lang == "fr":
            return f"Un autre utilisateur {addr} a essayé de se connecter avec le nom \"{name}\", la connexion a " \
               f"été refusée."
        else:
            return f"Another user {addr} tried to connect with the name \"{name}\", the connection has been refused."

    def name_already_taken_connection_refused(self, name: str) -> str:
        if self.lang == "fr":
            return f"Le nom \"{name}\" est déjà pris, la connexion a été refusée."
        else:
            return f"The name \"{name}\" has already been taken, the connection has been refused."

    def connected_to(self, servername: str) -> str:
        if self.lang == "fr":
            return f"Connecté à \"{servername}\" !"
        else:
            return f"Connected to \"{servername}\" !"

    def user_connected_from(self, name: str, addr: tuple) -> str:
        if self.lang == "fr":
            return f"\"{name}\" a connecté depuis \"{addr[0]}:{addr[1]}\"."
        else:
            return f"\"{name}\" has connected from \"{addr[0]}:{addr[1]}\"."

    def data_received_from(self, name: str, data: str) -> str:
        if self.lang == "fr":
            return f"Données reçues depuis \"{name}\" : \"{data}\"."
        else:
            return f"Data received from \"{name}\" : \"{data}\"."

    def connection_lost(self, identifier: str) -> str:
        if self.lang == "fr":
            return f"Connexion perdue avec \"{identifier}\"."
        else:
            return f"Connection lost with \"{identifier}\"."

    def away_cmd_response(self, away: bool, message: str) -> str:
        if self.lang == "fr":
            status = "absent" if away else "présent"
            away_message = ""
            if away:
                away_message = f" Votre message d'absence est: \"{message}\"."
            return f"Vous êtes désormais marqué comme {status}.{away_message}"
        else:
            status = "away" if away else "present"
            away_message = ""
            if away:
                away_message = f" Your away message is : \"{message}\"."
            return f"You are now marked as {status}.{away_message}"

    def invite_cmd_response(self, name: str, channel: str, key: str) -> str:
        if self.lang == "fr":
            key_msg = f" Clé : \"{key}\"" if key else ""
            return f"\"{name}\" vous a invité au canal \"{channel}\".{key_msg}"
        else:
            key_msg = f" Key : \"{key}\"" if key else ""
            return f"\"{name}\" invited you to the channel \"{channel}\".{key_msg}"

    def msg_cmd(self, name: str, message: str) -> str:
        return f"\"{name}\" : \"{message}\""

    def list_cmd_response(self, channels: list) -> str:
        channels = list(map(lambda x: f"- {x}", channels))
        if self.lang == "fr":
            channels.insert(0, "Liste des canaux :")
        else:
            channels.insert(0, "List of channels :")
        return "\n".join(channels)

    def names_cmd_response(self, channel: str, names: list) -> str:
        names = list(map(lambda x: f"- {x}", names))
        if self.lang == "fr":
            names.insert(0, f"Liste des utilisateur dans le canal \"{channel}\" :")
        else:
            names.insert(0, f"List of users in the channel \"{channel}\" :")
        return "\n".join(names)
