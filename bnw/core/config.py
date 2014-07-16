class Config(dict):
    def __init__(self):
        self._update_handlers = set()
    def __getattr__(self, key):
        return self.__getitem__(key)

    def register_handler(self, handler):
        self._update_handlers.add(handler)


    def compare(self, other, *keys):
        """ Returns True if all values for specified *keys* are equal in this and *other* Config"""
        for key in keys:
            if self.get(key) != other.get(key):
                return False
        return True
    def update_config(self, new_config):
        for handler in self._update_handlers:
            result = handler(self, new_config)
            if result:
                return result
        old_config = dict(self)
        self.update(new_config)
        for key in self.iterkeys():
            if key not in new_config:
                del self[key]

config = Config()
