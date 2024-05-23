from bencher.plugins import Base


class PluginA(Base):

    def __init__(self):
        pass

    def start(self):
        print("Plugin A")
