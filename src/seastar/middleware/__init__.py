

class Middleware:

    def __init__(self, cls, **options):
        self.cls = cls
        self.options = options
    
    def __iter__(self):
        return iter((self.cls, self.options))
