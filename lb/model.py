class Instance:
    def __init__(self, url):
        self.url = url
        self.is_alive = True

    def __str__(self):
        return f"Instance at {self.url}, is_alive: {self.is_alive}"
