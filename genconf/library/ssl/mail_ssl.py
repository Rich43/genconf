from genconf.library.librarybase import LibraryBase
from subprocess import Popen, PIPE

class MailSSL(LibraryBase):
    """
    Generate the SSL certificates for mail.
    """
    
    def __init__(self, ini_file, json_file):
        LibraryBase.__init__(self, ini_file, json_file)
        self.openssl_bin = self.config.get("ssl", "openssl_bin")
        self.password = self.config.get("ssl", "password")
        self.country_name = self.config.get("ssl", "country_name")
        self.state_province_name = self.config.get("ssl", 
                                                "state_province_name")
        self.locality_name = self.config.get("ssl", "locality_name")
        self.organisation_name = self.config.get("ssl", "organisation_name")
        self.organisation_unit_name = self.config.get("ssl", 
                                                "organisation_unit_name")
        self.common_name = self.config.get("ssl", "common_name")
        self.email_address = self.config.get("ssl", "email_address")
        
    def generate_conf(self, key_file=''):
        """
        Run this one second.
        """
        template = self.env.get_template('ssl/openssl.jinja2')
        template_output = template.render(password=self.password, 
                          country_name=self.country_name,
                          state_province_name=self.state_province_name,
                          locality_name=self.locality_name,
                          organisation_name=self.organisation_name,
                          organisation_unit_name=self.organisation_unit_name,
                          common_name=self.common_name, 
                          email_address=self.email_address,
                          key_file=key_file)
        return template_output
    
    def generate_csr(self, key_path, conf_path):
        """
        Run this one third.
        """
        command = [self.openssl_bin, "req", "-new", 
                   "-key", key_path,
                   "-config", conf_path,
                   "-passin", "pass:" + self.password]
        output = Popen(command, stdout=PIPE, stderr=PIPE
                       ).communicate()[0].decode("utf-8")
        return output
    
    def generate_crt(self, csr_path, key_path):
        """
        Run this one fourth.
        """
        command = [self.openssl_bin, "x509", "-req", 
                   "-days", "3650",
                   "-in", csr_path,
                   "-signkey", key_path,
                   "-passin", "pass:" + self.password]
        output = Popen(command, stdout=PIPE, stderr=PIPE
                       ).communicate()[0].decode("utf-8")
        return output
    
    def generate_decrypted_key(self, key_path):
        command = [self.openssl_bin, "rsa",
                   "-in", key_path, 
                   "-passin", "pass:" + self.password]
        output = Popen(command, stdout=PIPE, stderr=PIPE
                       ).communicate()[0].decode("utf-8")
        return output
    
    # openssl req -new -x509 -extensions v3_ca -keyout cakey.pem -out cacert.pem -days 3650
    
    def generate_pem(self, cfg_path):
        command = [self.openssl_bin, "req",
                   "-new", "-x509",
                   "-extensions", "v3_ca",
                   "-config", cfg_path,
                   "-days", "3650",
                   "-passout", "pass:" + self.password]
        output = Popen(command, stdout=PIPE, stderr=PIPE
                       ).communicate()[0].decode("utf-8")
        return output
    
    def generate_key(self):
        """
        Run this one first.
        """
        command = [self.openssl_bin, "genrsa", "-des3", "-passout", 
                   "pass:" + self.password, "1024"]
        output = Popen(command, stdout=PIPE, stderr=PIPE
                       ).communicate()[0].decode("utf-8")
        return output