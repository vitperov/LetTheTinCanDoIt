import hashlib
import os
from pathlib import Path
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from enum import Enum

from .dbRecords.DescriptionRecord import DescriptionRecord

class FileStatus(Enum):
    NotIndexed = "NotIndexed"
    Indexed = "Indexed"
    Outdated = "Outdated"

class ProjectMeta:
    def __init__(self, project_path: str, llm_model=None):
        print(f"ProjectMeta: opening project {project_path}")
        self.project_path = project_path
        self.db_path = os.path.join(project_path, '.lttcdi', 'metadata.json')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                f.write('{}')

        self.db = TinyDB(self.db_path, storage=CachingMiddleware(JSONStorage))
        self.llm_model = llm_model
        self.available_models = llm_model.available_models if llm_model else []
        self.index_extensions = ['py']
        self.index_directories = []
        self.indexing_model = None
        self.hide_extensions = []
        self.load_settings()

    def _get_relative_path(self, absolute_path: str) -> str:
        return os.path.relpath(absolute_path, self.project_path)

    def calculate_checksum(self, relative_path: str) -> str:
        file_path = os.path.join(self.project_path, relative_path)
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def getAll_project_files(self) -> list:
        project_files = []
        if not self.index_directories:
            for root, dirs, files in os.walk(self.project_path):
                for file in files:
                    if Path(file).suffix[1:] in self.index_extensions:
                        full_path = os.path.join(root, file)
                        project_files.append(self._get_relative_path(full_path))
        else:
            for rel_dir in self.index_directories:
                abs_dir = os.path.join(self.project_path, rel_dir)
                if os.path.isdir(abs_dir):
                    for root, dirs, files in os.walk(abs_dir):
                        for file in files:
                            if Path(file).suffix[1:] in self.index_extensions:
                                full_path = os.path.join(root, file)
                                project_files.append(self._get_relative_path(full_path))
        return project_files

    def _get_existing_record(self, relative_path: str):
        FileQuery = Query()
        result = self.db.search(FileQuery.file_path == relative_path)
        return DescriptionRecord(**result[0]) if result else None

    def compose_file_description(self, relative_path: str) -> str:
        absolute_path = os.path.join(self.project_path, relative_path)
        with open(absolute_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        prompt = (
        "You are a code summarization assistant. A code file’s full text will be provided; analyze it and output **exactly one concise sentence** that captures the file’s primary responsibility or purpose.\n\n"
        "  - Write in plain English—no JSON, no bullet lists, no quotes.\n"
        "  - Do not explain your reasoning or add extra commentary—just the single sentence.\n"
        "  - Do not mention framework.\n"
        "  - Avoid common introduction phases, like \"This code\", \"This file\" and \"This script\". Straight to the point.\n\n"
        " ----------------- \n"       
        )
        request_text = prompt + file_content
        if not self.llm_model:
            return f"Description for {relative_path}"
        model_name = self.indexing_model or (self.available_models[0] if self.available_models else "gpt-4o-mini")
        response = self.llm_model.generate_simple_response_sync(model_name, request_text, printRequest=False)
        if isinstance(response, tuple):
            description, _ = response
        else:
            description = response
        return description

    def update_descriptions(self):
        files = self.getAll_project_files()
        for rel_path in files:
            current_checksum = self.calculate_checksum(rel_path)
            existing = self._get_existing_record(rel_path)

            if not existing or existing.checksum != current_checksum:
                new_description = self.compose_file_description(rel_path)
                print(f"{rel_path}: {new_description}\n")
                record = DescriptionRecord(rel_path, current_checksum, new_description)
                self.db.upsert(record.to_dict(), Query().file_path == rel_path)
        self.db.storage.flush()

    def force_update_descriptions(self):
        files = self.getAll_project_files()
        for rel_path in files:
            current_checksum = self.calculate_checksum(rel_path)
            new_description = self.compose_file_description(rel_path)
            print(f"{rel_path}: {new_description}\n")
            record = DescriptionRecord(rel_path, current_checksum, new_description)
            self.db.upsert(record.to_dict(), Query().file_path == rel_path)
        self.db.storage.flush()

    def update_description(self, relative_path: str):
        current_checksum = self.calculate_checksum(relative_path)
        new_description = self.compose_file_description(relative_path)
        print(f"{relative_path}: {new_description}\n")
        record = DescriptionRecord(relative_path, current_checksum, new_description)
        self.db.upsert(record.to_dict(), Query().file_path == relative_path)
        self.db.storage.flush()

    def stat_descriptions(self) -> dict:
        files_in_project = set(self.getAll_project_files())
        db_records = {rec['file_path']: rec for rec in self.db.all()}

        stats = {
            'total_files': len(files_in_project),
            'new_files': [],
            'outdated_files': [],
            'up_to_date_files': []
        }

        for rel_path in files_in_project:
            current_checksum = self.calculate_checksum(rel_path)
            db_record = db_records.get(rel_path)

            if not db_record:
                stats['new_files'].append(rel_path)
            elif db_record['checksum'] != current_checksum:
                stats['outdated_files'].append(rel_path)
            else:
                stats['up_to_date_files'].append(rel_path)

        print(f"Project Description Statistics:")
        print(f"Total files: {stats['total_files']}")
        print(f"New files: {len(stats['new_files'])}")
        print(f"Outdated files: {len(stats['outdated_files'])}")
        print(f"Up-to-date files: {len(stats['up_to_date_files'])}")

        return stats

    def load_settings(self):
        settings_table = self.db.table('settings')
        settings = settings_table.get(Query().id == "project_settings")
        default_model = self.available_models[0] if self.available_models else None
        if settings:
            self.index_extensions = settings.get("index_extensions", self.index_extensions)
            self.index_directories = settings.get("index_directories", self.index_directories)
            self.indexing_model = settings.get("indexing_model", default_model)
            self.hide_extensions = settings.get("hide_extensions", self.hide_extensions) or []
        else:
            if self.index_directories is None:
                self.index_directories = []
            self.indexing_model = default_model
            self.hide_extensions = []
        return self.index_extensions, self.index_directories

    def save_settings(self, index_extensions, index_directories, indexing_model, hide_extensions):
        self.index_extensions = index_extensions
        self.index_directories = index_directories
        self.indexing_model = indexing_model
        self.hide_extensions = hide_extensions
        settings_table = self.db.table('settings')
        settings_table.upsert(
            {
                "id": "project_settings",
                "index_extensions": index_extensions,
                "index_directories": index_directories,
                "indexing_model": indexing_model,
                "hide_extensions": hide_extensions
            },
            Query().id == "project_settings"
        )
        self.db.storage.flush()

    def getFileDescription(self, relative_path: str):
        existing = self._get_existing_record(relative_path)
        return existing.description if existing else ""

    def getFileStatus(self, relative_path: str) -> FileStatus:
        existing = self._get_existing_record(relative_path)
        if not existing:
            return FileStatus.NotIndexed
        current_checksum = self.calculate_checksum(relative_path)
        if existing.checksum == current_checksum:
            return FileStatus.Indexed
        return FileStatus.Outdated

    def getIndexationParameters(self):
        return self.index_extensions, self.index_directories

    def getHiddenExtensions(self) -> list:
        return self.hide_extensions
