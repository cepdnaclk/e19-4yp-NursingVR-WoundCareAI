class UserInDB:
    def __init__(self, username: str, full_name: str, email: str, hashed_password: str, disabled: bool = False):
        self.username = username
        self.email = email
        self.full_name = full_name
        self.hashed_password = hashed_password
        self.disabled = disabled 

    def __repr__(self):
        return f"UserinDB(username={self.username}, email={self.email}, is_active={self.is_active})" 