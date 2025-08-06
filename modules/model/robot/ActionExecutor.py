import os
import re

class ActionExecutor:
    def __init__(self, project_meta):
        self.project_meta = project_meta
        self.project_path = project_meta.project_path

    def execute(self, action_str):
        tokens = action_str.strip().split(maxsplit=1)
        if not tokens:
            return "ERROR: No action provided."
        command = tokens[0].upper()
        if command == "LS":
            return self.ls()
        elif command == "READ":
            if len(tokens) < 2:
                return "ERROR: No filename provided for READ."
            filename = tokens[1].strip()
            return self.read(filename)
        elif command == "WRITE":
            return self.write(action_str)
        else:
            return f"ERROR: Unknown action: {command}"

    def ls(self):
        files = self.project_meta.getAll_project_files()
        return "\n".join(files)

    def read(self, filename):
        file_path = os.path.join(self.project_path, filename)
        if not os.path.isfile(file_path):
            return f"ERROR: File not found: {filename}"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"ERROR: Could not read file {filename}: {e}"

    def write(self, action_str):
        tokens = action_str.strip().split(maxsplit=2)
        if len(tokens) < 3:
            return "ERROR: No filename or content provided for WRITE."
        filename = tokens[1]
        content = tokens[2]
        file_path = os.path.join(self.project_path, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"File {filename} written successfully."
        except Exception as e:
            return f"ERROR: Could not write file {filename}: {e}"
