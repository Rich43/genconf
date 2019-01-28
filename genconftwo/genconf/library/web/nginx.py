from genconf.library.librarybase import LibraryBase
class Nginx(LibraryBase):
    """
    Generate the nginx configation files.
    """
    def generate_sites(self):
        """
        Generate the websites, return as a list of tuples.
        """
        result = []
        template = self.env.get_template('web/nginx.jinja2')
        for user_data in self.database['users'].values():
            template_output = template.render(domain=user_data['domain'], 
                              php=user_data.get('php'),
                              wsgi=user_data.get('wsgi'),
                              proxy=user_data.get('proxy'),
                              wsgi_dir=user_data.get('wsgi_dir'),
                              wsgi_module=user_data.get('wsgi_module'),
                              proxy_port=user_data.get('proxy_port'),
                              listen=self.config.getboolean("web", 
                                                "nginx_add_listen_line"),
                              php_fpm_path=self.config.get("web", 
                                                "php_fpm_path"))
            template_output = template_output.replace("    \n", "\n")
            template_output = template_output.replace("\n\n", "\n")
            result.append((user_data['domain'], template_output))
        return result