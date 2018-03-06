class MessageHandler:
    def __init__(self, messageTypes):
        self.HandledTypes = messageTypes
    def IsHandledMessage(self, message):
        for messageType in self.HandledTypes:
            if isinstance(message, messageType):
                return True

        return False
    def Handle(self, message):
        if self.IsHandledMessage(message):
            return message

class DelgatingMessageHandler(MessageHandler):
    def __init__(self, messageTypes, handlingFunction):
        MessageHandler.__init__(self, messageTypes)
        self.__handlingFunction = handlingFunction

    def Handle(self, message):
        validatedMessage = MessageHandler.Handle(self, message)

        if validatedMessage is None:
            return

        self.__handlingFunction(validatedMessage)

class Message:
    pass

class Courier:
    def __init__(self):
        self.__handlers = {}
    def Send(self, message):
        if not isinstance(message, Message):
            return

        if type(message) not in self.__handlers:
            return

        for handler in self.__handlers[type(message)]:
            handler.Handle(message)
    def AddHandler(self, handler):
        if not isinstance(handler, MessageHandler):
            return

        for messageType in handler.HandledTypes:
            if not messageType in self.__handlers:
                self.__handlers[messageType] = []
            if not handler in self.__handlers[messageType]:
                self.__handlers[messageType].append(handler)
    def RemoveHandler(self, handler):
        if not isinstance(handler, MessageHandler):
            return

        for messageType in handler.HandledTypes:
            if not messageType in self.__handlers:
                continue
            if handler in self.__handlers[messageType]:
                self.__handlers[messageType].remove(handler)
