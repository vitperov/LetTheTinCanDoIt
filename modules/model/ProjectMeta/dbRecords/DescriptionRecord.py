class DescriptionRecord:
    def __init__(self, file_path: str, checksum: str, description: str):
        self.file_path = file_path
        self.checksum = checksum
        self.description = description

    def to_dict(self):
        return {
            'file_path': self.file_path,
            'checksum': self.checksum,
            'description': self.description
        }
