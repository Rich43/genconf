from genconf.library.librarybase import LibraryBase
import genconf.library.drivers.pymysql as pymysql
from genconf.library.drivers.pymysql.err import \
    InternalError, ProgrammingError
from genconf.library.helper import make_password, escape_string

class UserFound(Exception):
    pass

class UserNotFound(Exception):
    pass

class DatabaseNotFound(Exception):
    pass

class DatabaseFound(Exception):
    pass

class Mysql(LibraryBase):
    """
    Add/remove users and databases.
    """
    
    def __init__(self, ini_file, json_file):
        LibraryBase.__init__(self, ini_file, json_file)
        self.host = self.config.get("database", "mysql_host")
        self.username = self.config.get("database", "mysql_username")
        self.password = self.config.get("database", "mysql_password")
        self.password_length = self.config.getint("database", 
                                                  "password_length")
        self.user_hostname = self.config.get("database", 
                                             "mysql_new_user_hostname")
        self.connection = None
        
    def connect(self):
        if not self.connection:
            self.connection = pymysql.connect(host=self.host, 
                                              user=self.username, 
                                              passwd=self.password)
            
    def close(self):
        self.connection.close()
    
    def add_user(self, username):
        password = make_password(self.password_length)
        c = self.connection.cursor()
        try:
            c.execute("CREATE USER %s@%s IDENTIFIED BY %s", 
                  [username, self.user_hostname, password])
        except InternalError:
            raise UserFound
        return password
    
    def add_database(self, database_name):
        c = self.connection.cursor()
        try:
            c.execute("CREATE DATABASE `%s`" % escape_string(database_name))
        except ProgrammingError:
            raise DatabaseFound
    
    def add_user_to_database(self, username, database_name):
        c = self.connection.cursor()
        sql = "GRANT ALL PRIVILEGES ON `%s` . * TO '%s'@'%s'" % (
                    escape_string(database_name), 
                    escape_string(username), 
                    escape_string(self.user_hostname))
        c.execute(sql)
        
    def delete_user(self, username):
        c = self.connection.cursor()
        try:
            c.execute("DROP USER %s@%s", [username, self.user_hostname])
        except InternalError:
            raise UserNotFound
        
    def delete_database(self, database_name):
        c = self.connection.cursor()
        try:
            c.execute("DROP DATABASE `%s`" % escape_string(database_name))
        except InternalError:
            raise DatabaseNotFound
        
    def list_databases(self):
        c = self.connection.cursor()
        c.execute("SHOW DATABASES")
        return set([x[0] for x in c])
    
    def list_users(self):
        c = self.connection.cursor()
        c.execute("select User from mysql.user")
        return set([x[0].decode("utf8") for x in c])