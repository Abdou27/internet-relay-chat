class NameAlreadyTaken(Exception):
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        super(NameAlreadyTaken, self).__init__()

    def get_server_message(self):
        return f"Un autre utilisateur ({self.name}) a essayé de se connecter avec le nom {self.addr}, la connexion a " \
               f"été refusée."

    def get_client_message(self):
        return f"Le nom ({self.name}) est déjà pris, la connexion a été refusée."
