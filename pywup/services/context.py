from pywup.services import conf


class Context:

    def __init__(self):
        self.reload()

    
    def reload(self):
        try:
            self.name = conf.get("wup.env_name", scope="global")
            self.filepath = conf.get("wup.env_filepath", scope="global")

            if self.filepath:
                self.variables, self.templates, self.bashrc = parse_env(self.filepath)
                self.cont_name = get_container_name(self.name)
                self.img_name = get_image_name(self.name)
            
        except:
            self.name = ""
            self.filepath = ""
            self.cont_name = None
            self.img_name = None
            self.variables, self.templates, self.bashrc = None, None, None
