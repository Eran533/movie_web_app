import csv
from .dataManager_Interface import DataManagerInterface

class CSVDataManager(DataManagerInterface):
    def __init__(self, filename):
        self.filename = filename

    def get_all_users(self):
        # Return a list of all users
        pass

    def get_user_movies(self, user_id):
        pass