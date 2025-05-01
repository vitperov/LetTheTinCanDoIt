import hashlib
import os
from pathlib import Path
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from .dbRecords/DescriptionRecord import DescriptionRecord

class ProjectMeta:
    def __init__(self, project_path: str, index_extensions: list = None):
        self.project_path = project_path
        self.db_path = os.path.join(project_path, '.lttcdi', 'metadata.json')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                f.write('{}')
        
        self.db = TinyDB(self.db_path, storage=CachingMiddleware(JSONStorage))
        self.index_extensions = index_extensions if index_extensions else ['py']
        
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
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if Path(file).suffix[1:] in self.index_extensions:
                    full_path = os.path.join(root, file)
                    project_files.append(self._get_relative_path(full_path))
        return project_files

    def _get_existing_record(self, relative_path: str) -> DescriptionRecord:
        FileQuery = Query()
        result = self.db.search(FileQuery.file_path == relative_path)
        return DescriptionRecord(**result[0]) if result else None

    def compose_file_description(self, relative_path: str) -> str:
        return f"Description for {relative_path}"

    def update_descriptions(self):
        files = self.getAll_project_files()
        for rel_path in files:
            current_checksum = self.calculate_checksum(rel_path)
            existing = self._get_existing_record(rel_path)
            
            if not existing or existing.checksum != current_checksum:
                new_description = self.compose_file_description(rel_path)
                record = DescriptionRecord(rel_path, current_checksum, new_description)
                self.db.upsert(record.to_dict(), Query().file_path == rel_path)

    def force_update_descriptions(self):
        files = self.getAll_project_files()
        for rel_path in files:
            current_checksum = self.calculate_checksum(rel_path)
            new_description = self.compose_file_description(rel_path)
            record = DescriptionRecord(rel_path, current_checksum, new_description)
            self.db.upsert(record.to_dict(), Query().file_path == rel_path)

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
