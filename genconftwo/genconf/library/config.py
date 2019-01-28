from genconf.library.librarybase import LibraryBase

class UserNotFound(Exception):
    pass

class UserFound(Exception):
    pass

class DomainNotFound(Exception):
    pass

class DomainFound(Exception):
    pass

class SubDomainNotFound(Exception):
    pass

class SubDomainFound(Exception):
    pass

class InvalidPort(Exception):
    pass

def find_user_and_save(f):
    def wrapped_f(*args):
        if not args[1] in args[0].database['users']:
            raise UserNotFound
        f(*args)
        args[0].save_database()
    return wrapped_f

class Config(LibraryBase):

    def add_user(self, username, domain):
        if username in self.database['users']:
            raise UserFound
        user = {"fullname": "New User",
                  "domain": domain,
                  "email": "new@user.com",
                  "php": False,
                  "wsgi": False,
                  "wsgi_dir": "",
                  "wsgi_module": "",
                  "proxy": False,
                  "proxy_port": "8080"}
        self.database['users'][username] = user
        self.save_database()
    
    @find_user_and_save
    def delete_user(self, username):
        del(self.database['users'][username])
    
    def get_user_config(self, username):
        if not username in self.database['users']:
            raise UserNotFound
        return self.database['users'][username]
    
    @find_user_and_save
    def update_fullname(self, username, name):
        self.database['users'][username]['fullname'] = name
        
    @find_user_and_save
    def update_domain(self, username, name):
        self.database['users'][username]['domain'] = name
        
    @find_user_and_save
    def update_email(self, username, name):
        self.database['users'][username]['email'] = name
        
    @find_user_and_save
    def update_wsgi_dir(self, username, name):
        self.database['users'][username]['wsgi_dir'] = name
        
    @find_user_and_save
    def update_wsgi_module(self, username, name):
        self.database['users'][username]['wsgi_module'] = name
        
    @find_user_and_save
    def update_proxy_port(self, username, name):
        try:
            int(name)
        except ValueError:
            raise InvalidPort
        self.database['users'][username]['proxy_port'] = int(name)
        
    @find_user_and_save
    def enable_php(self, username):
        self.database['users'][username]['php'] = True
        
    @find_user_and_save
    def disable_php(self, username):
        self.database['users'][username]['php'] = False
        
    @find_user_and_save
    def enable_wsgi(self, username):
        self.database['users'][username]['wsgi'] = True
        
    @find_user_and_save
    def disable_wsgi(self, username):
        self.database['users'][username]['wsgi'] = False
        
    @find_user_and_save
    def enable_proxy(self, username):
        self.database['users'][username]['proxy'] = True
        
    @find_user_and_save
    def disable_proxy(self, username):
        self.database['users'][username]['proxy'] = False
        
    def list_users(self):
        return self.database['users'].keys()
        
    def list_domains(self):
        return self.database['domains'].keys()
        
    def list_sub_domains(self, domain):
        if not domain in self.database['domains']:
            raise DomainNotFound
        return self.database['domains'][domain]
        
    def add_domain(self, domain):
        if domain in self.database['domains']:
            raise DomainFound
        self.database['domains'][domain] = []
        self.save_database()
        
    def delete_domain(self, domain):
        if not domain in self.database['domains']:
            raise DomainNotFound
        del(self.database['domains'][domain])
        self.save_database()
        
    def add_sub_domain(self, domain, sub_domain):
        if not domain in self.database['domains']:
            raise DomainNotFound
        if sub_domain in self.database['domains'][domain]:
            raise SubDomainFound
        self.database['domains'][domain].append(sub_domain)
        self.save_database()
        
    def delete_sub_domain(self, domain, sub_domain):
        if not domain in self.database['domains']:
            raise DomainNotFound
        if not sub_domain in self.database['domains'][domain]:
            raise SubDomainNotFound
        index = self.database['domains'][domain].index(sub_domain)
        del(self.database['domains'][domain][index])
        self.save_database()