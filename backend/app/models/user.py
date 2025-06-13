from datetime import datetime

class User:
    def __init__(self, name, email, hashed_password, role):
        self.name = name
        self.email = email
        self.hashed_password = hashed_password
        self.role = role
        self.created = datetime.utcnow()
        self.updated = datetime.utcnow()

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "hashed_password": self.hashed_password,
            "role": self.role,
            "created": self.created,
            "updated": self.updated
        }
