class AuthException(Exception):
    def __init__(self, detail: str, redirect_to_login: bool = False):
        self.detail = detail
        self.redirect_to_login = redirect_to_login
