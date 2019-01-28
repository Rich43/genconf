from genconf.library.librarybase import LibraryBase
from genconf.library.helper import make_password, escape_string
import genconf.library.drivers.postgresql as postgres
from genconf.library.drivers.postgresql.exceptions import \
    CatalogNameError, UndefinedObjectError, DuplicateDatabaseError, \
    DuplicateObjectError

class UserFound(Exception):
    pass

class UserNotFound(Exception):
    pass

class DatabaseNotFound(Exception):
    pass

class DatabaseFound(Exception):
    pass

class Postgres(LibraryBase):
    """
    Add/remove users and databases.
    """
    
    def __init__(self, ini_file, json_file):
        LibraryBase.__init__(self, ini_file, json_file)
        self.host = self.config.get("database", "postgres_host")
        self.username = self.config.get("database", "postgres_username")
        self.password = self.config.get("database", "postgres_password")
        self.password_length = self.config.getint("database", 
                                                  "password_length")
        self.connection = None
        
    def connect(self):
        if not self.connection:
            self.connection = postgres.open(host=self.host, 
                                               user=self.username, 
                                               password=self.password)
            
    def close(self):
        self.connection.close()
        
    def add_user(self, username):
        password = make_password(self.password_length)
        sql = "CREATE USER %s WITH PASSWORD '%s'" % (
                        escape_string(username), escape_string(password))
        try:
            self.connection.execute(sql)
        except DuplicateObjectError:
            raise UserFound
        return password
    
    def add_database(self, database_name):
        c = self.connection
        try:
            c.execute("CREATE DATABASE %s" % escape_string(database_name))
        except DuplicateDatabaseError:
            raise DatabaseFound
    
    def add_user_to_database(self, username, database_name):
        sql = "ALTER DATABASE %s OWNER TO %s"
        try:
            self.connection.execute(sql % (escape_string(database_name),
                                       escape_string(username)))
        except UndefinedObjectError:
            raise UserNotFound
        except CatalogNameError:
            raise DatabaseNotFound
        
    def delete_user(self, username):
        sql = "DROP ROLE %s" % escape_string(username)
        try:
            self.connection.execute(sql)
        except UndefinedObjectError:
            raise UserNotFound
        
    def delete_database(self, database_name):
        c = self.connection
        try:
            c.execute("DROP DATABASE %s" % escape_string(database_name))
        except CatalogNameError:
            raise DatabaseNotFound
    
    def list_users(self):
        result = self.connection.prepare("SELECT rolname FROM pg_roles")
        return set([x[0] for x in result()])
    
    def list_databases(self):
        result = self.connection.prepare("select datname from pg_database")
        return set([x[0] for x in result()])