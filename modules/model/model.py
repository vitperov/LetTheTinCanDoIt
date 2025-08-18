from PyQt5.QtCore import QObject, pyqtSignal
import os
import json
from modules.model.LLMModel import LLMModel
from modules.model.FileSyntaxCorrector import FileSyntaxCorrector
from modules.model.HistoryModel import HistoryModel
from modules.model.RequestHistoryModel import RequestHistoryModel
from modules.model.robot.robot import RobotModel
from modules.model.ProjectMeta.ProjectMeta import ProjectMeta
from modules.model.DesktopFileInstaller import DesktopFileInstaller

class ProjectGPTModel(QObject):
    response_generated = pyqtSignal(str)
    completed_job_list_updated = pyqtSignal(list, list)
    status_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.project_dir = None
        self.chosen_files = []
        self.completed_batches = []
        self.completed_jobs_descriptions = []
        self.syntax_corrector = FileSyntaxCorrector()
        self.additionalRequests = self.load_additional_requests()
        self.llm_model = LLMModel()
        self.available_models = self.llm_model.available_models
        self.llm_model.response_generated.connect(self.response_generated.emit)
        self.llm_model.completed_job_list_updated.connect(self.completed_job_list_updated.emit)
        self.llm_model.status_changed.connect(self.status_changed.emit)

        self.historyModel = HistoryModel()
        self.requestHistoryModel = RequestHistoryModel()

        last_project_directory = self.historyModel.get_last_project_directory()
        self.project_meta = ProjectMeta(last_project_directory, llm_model=self.llm_model)

        self.robotModel = RobotModel(self.llm_model, self.project_meta)
        self.desktop_installer = DesktopFileInstaller()

    def set_project_dir(self, project_dir):
        self.llm_model.set_project_dir(project_dir)
        self.project_meta.set_project_path(project_dir)
        self.robotModel.project_meta = self.project_meta
        self.project_dir = project_dir

    def set_project_files(self, chosen_files):
        self.llm_model.set_project_files(chosen_files)
        self.chosen_files = chosen_files

    def load_additional_requests(self):
        additional_requests_path = os.path.join('additionalRequests.json')
        if os.path.exists(additional_requests_path):
            with open(additional_requests_path, 'r') as f:
                data = json.load(f)
            return data.get('requests', [])
        return []

    def get_additional_requests(self):
        return self.additionalRequests

    def install_desktop_file(self):
        """
        Trigger installation of the .desktop file via the DesktopFileInstaller.
        """
        self.desktop_installer.install()
