import json
from .dataManager_Interface import DataManagerInterface

class JSONDataManager(DataManagerInterface):
    """
       JSONDataManager is an implementation of the DataManagerInterface that uses JSON as the data storage format.
       It provides methods to load and save data from a JSON file, as well as retrieve user and movie information.
       """
    def __init__(self, filename):
        """
                Initializes the JSONDataManager with the given filename.

                Args:
                    filename (str): The name of the JSON file to load/save data.
                """
        self.filename = filename

    def load_data(self):
        """
               Loads data from the JSON file.

               Returns:
                   dict: The loaded data.
               """
        with open(self.filename, 'r') as file:
            data = json.load(file)
        return data

    def save_data(self, data):
        """
                Saves the data to the JSON file.

                Args:
                    data (dict): The data to be saved.
                """
        with open(self.filename, 'w') as file:
            json.dump(data, file)

    def get_all_users(self):
        data = self.load_data()
        users_lst = []
        for user in data:
            users_lst.append(user)
        return users_lst

    def get_user_movies(self, user_id):
        data = self.load_data()
        movies = []
        for user in data:
            if user["id"] == user_id:
                for movie in user["movies"]:
                    movies.append(movie)
        return movies

    def get_user(self, user_id):
        data = self.load_data()
        for user in data:
            if user_id == user["id"]:
                return user
