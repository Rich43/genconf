#!/usr/bin/python3
from gettext import ngettext
import argparse
argparse.ngettext = ngettext
import shutil
import json
from os.path import join, exists, dirname
from os import makedirs, remove
from pprint import pprint
from genconf.library.dns.zonefile import ZoneFile
from genconf.library.web.nginx import Nginx
from genconf.library.ssl.mail_ssl import MailSSL
from genconf.library.mail.postfix import Postfix
from genconf.library.commands.accounts import Accounts
from genconf.library.database.mysql import Mysql
from genconf.library.database.postgres import Postgres
from genconf.library.config import Config
from genconf.library.python.paster import Paster

class Functions:
    def __init__(self, output_folder, conf_file, json_file, parser):
        self.str_output_folder = output_folder
        self.str_conf_file = conf_file
        self.str_json_file = json_file
        self.function_ran = False
        self.exceptions = ['conf_file', 'json_file', 'output_folder']
        self.drivers = {'mysql': Mysql, 'postgres': Postgres}
        self.parser = parser
        self.a = Accounts(self.str_conf_file, self.str_json_file)
        self.c = Config(self.str_conf_file, self.str_json_file)
        
    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if hasattr(attr, '__call__'):
            if not name in self.exceptions:
                self.function_ran = True
            return attr
        else:
            return attr
            
    def make_folder(self, output_folder):
        if exists(output_folder):
            return
        makedirs(output_folder)

    def error(self, message):
        args = {'prog': self.parser.prog, 'message': message}
        self.parser.exit(2, '%(prog)s: error: %(message)s\n' % args)
     
    def validate_driver_and_connect(self, driver):
        if not driver in self.drivers:
            self.error("Invalid driver %s (Try -dl)" % driver)
        else:
            d = self.drivers[driver](self.str_conf_file, self.str_json_file)
            d.connect()
            return d
             
    def conf_file(self, str_conf_file):
        """-c CONF_FILE, --conf-file CONF_FILE
        INI file with various configuration. Defaults to file
        "config.ini" in current directory."""
        self.str_conf_file = str_conf_file
    
    def json_file(self, str_json_file):
        """-j JSON_FILE, --json-file JSON_FILE
        JSON database file with accounts and domains. Defaults
        to file "database.json" in current directory."""
        self.str_json_file = str_json_file
    
    def output_folder(self, str_output_folder):
        """-o OUTPUT_FOLDER, --output-folder OUTPUT_FOLDER
        Folder to output generated files to. The folder will
        be created if missing. Defaults to folder "output" in
        current directory."""
        self.str_output_folder = str_output_folder
    
    def delete_output_folder(self):
        """-d, --delete-output-folder
        Remove all files and folders in output folder first."""
        shutil.rmtree(self.str_output_folder, True)
    
    def generate_paster_virtual_hosts(self):
        """-pv, --generate-paster-virtual-hosts
        PYTHON: Generate a paster virtual host INI file."""
        path = join(self.str_output_folder, "python")
        self.make_folder(path)
        path = join(path, "virtual_host.ini")
        p = Paster(self.str_conf_file, self.str_json_file)
        open(path, "w").write(p.generate_virtual_host_ini())
        
    def generate_zonefiles(self):
        """-z, --generate-zonefiles
        DNS: Generate zone files for bind and nsd."""
        z = ZoneFile(self.str_conf_file, self.str_json_file)
        path = join(self.str_output_folder, "dns", "zonefiles")
        self.make_folder(path)
        for zone in z.generate_zones():
            new_path = join(path, zone[0] + ".zone")
            open(new_path, "w").write(zone[1])

    def generate_nginx(self):
        """-n, --generate-nginx  WEB: Generate virtual hosts and other nginx
        configuration."""
        path = join(self.str_output_folder, "web", "nginx")
        self.make_folder(path)
        n = Nginx(self.str_conf_file, self.str_json_file)
        for site in n.generate_sites():
            new_path = join(path, site[0] + ".conf")
            open(new_path, "w").write(site[1])

    def generate_mail_ssl(self):
        """-sm, --generate-mail-ssl
        SSL: Generate SSL certificates for mail."""
        m_ssl = MailSSL(self.str_conf_file, self.str_json_file)
        
        # Figure out paths and create folder
        m_root = join(self.str_output_folder, "mail", "ssl")
        self.make_folder(m_root)
        m_cfg = join(m_root, "ssl.cfg")
        m_key = join(m_root, "ssl.key")
        m_csr = join(m_root, "ssl.csr")
        m_crt = join(m_root, "ssl.crt")
        m_pem = join(m_root, "ssl.pem")
        
        # Generate ssl files.
        open(m_key, "w").write(m_ssl.generate_key())
        open(m_cfg, "w").write(m_ssl.generate_conf(m_pem + "pvt"))
        open(m_csr, "w").write(m_ssl.generate_csr(m_key, m_cfg))
        open(m_crt, "w").write(m_ssl.generate_crt(m_csr, m_key))
        open(m_key + "dec", "w").write(m_ssl.generate_decrypted_key(m_key))
        open(m_pem, "w").write(m_ssl.generate_pem(m_cfg))
        
        # Remove unused config file
        remove(m_cfg)

    def generate_postfix(self):
        """-p, --generate-postfix
        MAIL: Generate Postfix configuration files."""
        p = Postfix(self.str_conf_file, self.str_json_file)
        path = join(self.str_output_folder, "mail", "postfix")
        self.make_folder(path)
        open(join(path, "main.cf"), "w").write(p.generate_main())
        open(join(path, "virtual"), "w").write(p.generate_virtual())

    def generate_accounts(self):
        """-a, --generate-accounts
        COMMANDS: Generate helpful bash scripts for managing
        accounts."""
        
        path = join(self.str_output_folder, "commands", "accounts")
        self.make_folder(path)
        open(join(path, "add_all_accounts.sh"), 
             "w").write(self.a.generate_add_all_users())
        open(join(path, "del_all_accounts.sh"), 
             "w").write(self.a.generate_del_all_users())
                    
    def add_account(self, username):
        """-aa USERNAME, --add-account USERNAME
        COMMANDS: Add a unix account."""
        self.a.add_user(username)
        
    def delete_account(self, username):
        """-aa USERNAME, --add-account USERNAME
        COMMANDS: Add a unix account."""
        self.a.delete_user(username)

    def config_add_domain(self, domain):
        """-cad DOMAIN, --config-add-domain DOMAIN
        CONFIG: Add a domain to JSON database."""
        self.c.add_domain(domain)

    def config_delete_domain(self, domain):
        """-cdd DOMAIN, --config-delete-domain DOMAIN
        CONFIG: Delete a domain from JSON database."""
        self.c.delete_domain(domain)

    def config_add_sub_domain(self, domain, sub_domain):
        """-as DOMAIN SUBDOMAIN, --config-add-sub-domain DOMAIN SUBDOMAIN
        COMMANDS: Add a unix account."""
        self.c.add_sub_domain(domain, sub_domain)

    def config_delete_sub_domain(self, domain, sub_domain):
        """-ds DOMAIN SUBDOMAIN, --config-delete-sub-domain DOMAIN SUBDOMAIN
        CONFIG: Delete a sub-domain from JSON database."""
        self.c.delete_sub_domain(domain, sub_domain)

    def config_add_user(self, username, domain):
        """-cau USERNAME DOMAIN, --config-add-user USERNAME DOMAIN
        CONFIG: Add a user to JSON database."""
        self.c.add_user(username, domain)

    def config_delete_user(self, username):
        """-cdu USERNAME, --config-delete-user USERNAME
        CONFIG: Delete a user from JSON database."""
        self.c.delete_user(username)

    def config_user_config(self, username):
        """-uc USERNAME, --config-user-config USERNAME
        CONFIG: Get configuration information about a user."""
        pprint(self.c.get_user_config(username))

    def config_update_fullname(self, username, name):
        """-uf USERNAME FULLNAME, --config-update-fullname USERNAME FULLNAME
        CONFIG: Change a users full name."""
        self.c.update_fullname(username, name)

    def config_update_domain(self, username, name):
        """-ud USERNAME DOMAIN, --config-update-domain USERNAME DOMAIN
        CONFIG: Change a users domain."""
        self.c.update_domain(username, name)

    def config_update_email(self, username, name):
        """-ue USERNAME EMAIL, --config-update-email USERNAME EMAIL
        CONFIG: Change a users email."""
        self.c.update_email(username, name)

    def config_update_wsgi_module(self, username, name):
        """-uw USERNAME MODULENAME, --config-update-wsgi-module USERNAME MODULENAME
        CONFIG: Change a users python module name for WSGI."""
        self.c.update_wsgi_module(username, name)

    def config_update_proxy_port(self, username, name):
        """-up USERNAME PORT, --config-update-proxy-port USERNAME PORT
        CONFIG: Change a users proxy port."""
        self.c.update_proxy_port(username, name)

    def config_enable_php(self, username):
        """-ep USERNAME, --config-enable-php USERNAME
        CONFIG: Enable PHP support for a user."""
        self.c.enable_php(username)

    def config_disable_php(self, username):
        """-dp USERNAME, --config-disable-php USERNAME
        CONFIG: Disable PHP support for a user."""
        self.c.disable_php(username)

    def config_enable_proxy(self, username):
        """-ex USERNAME, --config-enable-proxy USERNAME
        CONFIG: Enable Proxy support for a user."""
        self.c.enable_proxy(username)

    def config_disable_proxy(self, username):
        """-dx USERNAME, --config-disable-proxy USERNAME
        CONFIG: Disable Proxy support for a user."""
        self.c.disable_proxy(username)

    def config_enable_wsgi(self, username):
        """-ew USERNAME, --config-enable-wsgi USERNAME
        CONFIG: Enable WSGI support for a user."""
        self.c.enable_wsgi(username)

    def config_disable_wsgi(self, username):
        """-dw USERNAME, --config-disable-wsgi USERNAME
        CONFIG: Disable WSGI support for a user."""
        self.c.disable_wsgi(username)

    def config_list_users(self):
        """-cl, --config-list-users
        CONFIG: List all users in JSON database."""
        print("\n".join(self.c.list_users()))

    def config_list_domains(self):
        """-cd, --config-list-domains
        CONFIG: List all domains in JSON database."""
        print("\n".join(self.c.list_domains()))

    def config_list_sub_domains(self, domain):
        """-cs DOMAIN, --config-list-sub-domains DOMAIN
        CONFIG: List all sub-domains in DOMAIN from JSON
        database."""
        print("\n".join(self.c.list_sub_domains(domain)))

    def database_add_user(self, driver, username):
        """-au DRIVER USERNAME, --database-add-user DRIVER USERNAME
        DATABASE: Add a database user."""
        driver_obj = self.validate_driver_and_connect(driver)
        print(driver_obj.add_user(username))
        
    def database_delete_user(self, driver, username):
        """-du DRIVER USERNAME, --database-delete-user DRIVER USERNAME
        DATABASE: Delete a database user."""
        driver_obj = self.validate_driver_and_connect(driver)
        driver_obj.delete_user(username)
        
    def database_add_database(self, driver, database):
        """-ad DRIVER DATABASE, --database-add-database DRIVER DATABASE
        DATABASE: Add a database user."""
        driver_obj = self.validate_driver_and_connect(driver)
        driver_obj.add_database(database)

    def database_delete_database(self, driver, database):
        """-dd DRIVER DATABASE, --database-delete-database DRIVER DATABASE
        DATABASE: Delete a database user."""
        driver_obj = self.validate_driver_and_connect(driver)
        driver_obj.delete_database(database)

    def database_user_to_database(self, driver, username, database):
        """-dt DRIVER USERNAME DATABASE, --database-user-to-database 
        DRIVER USERNAME DATABASE
        DATABASE: Associate a user with a database."""
        driver_obj = self.validate_driver_and_connect(driver)
        driver_obj.add_user_to_database(username, database)
        
    def database_list_users(self, driver):
        """-lu DRIVER, --database-list-users DRIVER
        DATABASE: List users."""
        driver_obj = self.validate_driver_and_connect(driver)
        print("\n".join(driver_obj.list_users()))
        
    def database_list_databases(self, driver):
        """-ld DRIVER, --database-list-databases DRIVER
        DATABASE: List databases."""
        driver_obj = self.validate_driver_and_connect(driver)
        print("\n".join(driver_obj.list_databases()))
        
    def database_list_drivers(self):
        """dl, --database-list-drivers
        DATABASE: List supported database drivers, pass one of
        these into the database commands."""
        print("\n".join(self.drivers.keys()))
        
def main():
    parser = argparse.ArgumentParser(
            description='Generate config files, run commands' + \
                        ' and manage databases.')
                        
    command_line = join(dirname(__file__), "command_line.json")
    command_line_data = json.load(open(command_line, "r"))
    
    for item in command_line_data:
        if "metavar" in item[1]:
            # argparse needs a tuple for metavar
            if isinstance(item[1]["metavar"], list):
                item[1]["metavar"] = tuple(item[1]["metavar"])
        parser.add_argument(*item[0], **item[1])
     
    args = parser.parse_args()
    func = Functions(args.output_folder, args.conf_file, 
                        args.json_file, parser)
    
    # Map arguments to methods.
    for argument in command_line_data:
        # Get arguments long name
        long_name = argument[0][1]
        # Strip first 2 characters
        long_name = long_name[2:]
        # Add PEP 8 compliance.
        long_name = long_name.replace("-", "_")
        # Get result of command line argument.
        argument_result = getattr(args, long_name)
        # Run the method in func (if appropriate)
        if argument_result:
            # Raise exception if func is missing a method
            if not hasattr(func, long_name):
                raise Exception("Missing method %s" % long_name)
            # If argparse spits out a string, convert it to a list
            if isinstance(argument_result, str):
                argument_result = [argument_result]
            # If argparse spits out a boolean, output empty list
            if isinstance(argument_result, bool):
                argument_result = []
            # Finally run the method
            getattr(func, long_name)(*argument_result)
            
    if not func.function_ran:
        parser.print_usage()
    
if __name__ == '__main__':
    main()
