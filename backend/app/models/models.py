class Content:
    def __init__(self, title, file_path, user_id):
        self.title = title
        self.file_path = file_path
        self.user_id = user_id

    def to_dict(self):
        return {
            "title": self.title,
            "file_path": self.file_path,
            "user_id": self.user_id
        }
