class NameAlreadyTaken(Exception):
    def __init__(self, name, addr, translations):
        self.name = name
        self.addr = addr
        self.T = translations
        super().__init__()

    def get_server_message(self):
        return self.T.same_name_connection_refused(self.name, self.addr)

    def get_client_message(self):
        return self.T.name_already_taken_connection_refused(self.name)


class UserExited(Exception):
    def __init__(self, name, translations):
        self.name = name
        self.T = translations
        super().__init__()

    def get_server_message(self):
        return self.T.user_closed_connection(self.name)




