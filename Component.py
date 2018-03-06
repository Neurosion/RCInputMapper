class Component:
    def __init__(self, name):
        self.__name = name

    def Update(self, data):
        pass
    def Start(self):
        print(self.__name + " Started")

    def Stop(self):
        print(self.__name + " Stopped")
