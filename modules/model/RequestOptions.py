class RequestOptions:
    def __init__(self, includeFilesList=False, attachLastCommitDiff=False):
        self.includeFilesList = includeFilesList
        self.attachLastCommitDiff = attachLastCommitDiff
