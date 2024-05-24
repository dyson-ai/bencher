from bencher.plugins import Base


class PluginB(Base):

    def __init__(self):
        pass

    def start(self):
        print("Plugin B")
