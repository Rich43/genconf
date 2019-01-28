from genconf.library.librarybase import LibraryBase
from genconf.library.helper import sub_domain_to_domain
class Postfix(LibraryBase):
    def __init__(self, ini_file, json_file):
        LibraryBase.__init__(self, ini_file, json_file)
        self.ssl_cert_path = self.config.get("mail", "ssl_cert_path")
        self.ssl_key_path = self.config.get("mail", "ssl_key_path")
        self.ssl_pem_path = self.config.get("mail", "ssl_pem_path")
        self.hostname = self.config.get("mail", "hostname")
        self.postfix_virtual_path = self.config.get("mail", 
                                                    "postfix_virtual_path")
        self.postfix_sasl_path = self.config.get("mail", 
                                                    "postfix_sasl_path")
        self.postfix_sasl_type = self.config.get("mail", 
                                                    "postfix_sasl_type")
        self.smtp_banner = self.config.get("mail", "smtp_banner")
        
    def generate_main(self):
        domains = ""
        for domain in self.database['domains'].keys():
            domains += "%s, " % domain
        domains = domains[:-2]
        template = self.env.get_template('mail/postfix_main.jinja2')
        template_output = template.render(ssl_cert_path=self.ssl_cert_path,
                          ssl_key_path=self.ssl_key_path,
                          ssl_pem_path=self.ssl_pem_path,
                          hostname=self.hostname,
                          postfix_virtual_path=self.postfix_virtual_path,
                          postfix_sasl_type=self.postfix_sasl_type,
                          postfix_sasl_path=self.postfix_sasl_path,
                          smtp_banner=self.smtp_banner,
                          domains=domains)
        return template_output
        
    def generate_virtual(self):
        virtual = ""
        for user in self.database['users'].keys():
            sub_domain = True
            
            # Convert subdomain to its root domain.
            orig_domain = self.database['users'][user]['domain']
            domain = sub_domain_to_domain(self.database['domains'],
                                          orig_domain)
            
            if not domain:
                # The domain is a root domain.
                domain = orig_domain
                sub_domain = False
                
            # Add alias for root domain
            email = "%s@%s" % (user, domain)
            virtual += "%s     %s\n" % (email, user)
            
            if sub_domain:
                # Add an alias for the subdomain also.
                email = "%s@%s" % (user, orig_domain)
                virtual += "%s     %s\n" % (email, user)
                
        return virtual[:-1]