import configparser
import json
from jinja2 import Environment, PackageLoader

class LibraryBase:
    """
    A Base Library which all other library's inherit.
    """
    name = None
    
    def __init__(self, ini_file, json_file):
        """
        Load INI file, JSON database and Template engine.
        """
        # Load INI
        config = configparser.SafeConfigParser()
        config.readfp(open(ini_file, "r"))
        self.config = config
        
        # Load JSON
        self.json_file = json_file
        self.load_database()
        
        # Load template engine
        self.env = Environment(loader=PackageLoader('genconf', 'template'))
        
    def load_database(self):
        """
        Reload JSON Database from file.
        """
        self.database = json.load(open(self.json_file, "r"))
        
    def save_database(self):
        """
        Dump JSON Database to file.
        """
        json.dump(self.database, open(self.json_file, "w"))
