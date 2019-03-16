import json
from genconf.library.librarybase import LibraryBase
from genconf.template.commands import add_users, del_users
from subprocess import Popen, PIPE

class UserNotFound(Exception):
    pass

class Accounts(LibraryBase):

    def parse_json(self, path, user, domain):
        json_fp = open(path, "r")
        json_data = json.load(json_fp)
        result = []
        for commandset in json_data:
            command = list(commandset['command'])
            for argument in commandset['args']:
                if argument[1] == "USER":
                    command[argument[0]] += user
                elif argument[1] == "DOMAIN":
                    command[argument[0]] += domain
            result.append(command)
        return result
    
    def generate_json(self, path):
        items = ["#!/bin/bash"]
        for key, value in self.database['users'].items():
            for command in self.parse_json(path, key, value['domain']):
                items.append(" ".join(command))
        return "\n".join(items)
    
    def generate_add_all_users(self):
        return self.generate_json(add_users)
        
    def generate_del_all_users(self):
        return self.generate_json(del_users)

    def add_user(self, username):
        if not username in self.database['users']:
            raise UserNotFound
        user = self.database['users'][username]
        commands = self.parse_json(add_users, username, user['domain'])
        for command in commands:
            Popen(command, stdout=PIPE).communicate()[0]
        
    def delete_user(self, username):
        if not username in self.database['users']:
            raise UserNotFound
        user = self.database['users'][username]
        commands = self.parse_json(del_users, username, user['domain'])
        for command in commands:
            Popen(command, stdout=PIPE).communicate()[0]
