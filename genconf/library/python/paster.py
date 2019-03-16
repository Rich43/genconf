from genconf.library.librarybase import LibraryBase

class Paster(LibraryBase):
    def generate_virtual_host_ini(self):
        template = self.env.get_template('python/virtual_host.jinja2')
        dict_list = []
        for user, settings in self.database['users'].items():
            proxy = "proxy" in settings
            proxy_port = "proxy_port" in settings
            wsgi_module = "wsgi_module" in settings
            if proxy and proxy_port and wsgi_module:
                if settings['proxy']:
                    data_dict = {"user": user,
                                 "domain": settings['domain'],
                                 "port": settings['proxy_port'],
                                 'module': settings['wsgi_module']}
                    dict_list.append(data_dict)
        return template.render(data=dict_list)