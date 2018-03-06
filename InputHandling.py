from Messaging import Courier, Message

# Messages

class InputMessage(Message):
    def __init__(self, source):
        Message.__init__(self)
        self.Source = source

class InputActivated(InputMessage):
    def __init__(self, source):
        InputMessage.__init__(self, source)

class InputDeactivated(InputMessage):
    def __init__(self, source):
        InputMessage.__init__(self, source)

class InputUpdated(InputMessage):
    def __init__(self, source):
        InputMessage.__init__(self, source)

# Handlers

class InputHandler:
    def __init__(self, inputMap, valueRange, deadZone = None, courier = None):
        if not isinstance(inputMap, InputMap):
            raise Exception("Input map must be provided")

        if valueRange is None:
            raise Exception("Active value range must be provided")

        if not isinstance(courier, Courier) and courier is not None:
            raise Exception("Courier must be Courier instance or None")

        self.__courier = courier
        self.__name = inputMap.Name
        self.__eventName = inputMap.Code
        self.__valueRange = valueRange

        if deadZone is None:
            self.__deadZone = [0,0]
        else:
            self.__deadZone = deadZone

        self.__lastValue = None
        self.__isActive = False

    @property
    def IsActive(self):
        return self.__isActive

    def Handle(self, inputEvent):
        if inputEvent.code != self.__eventName:
            return False

        self.__lastValue = inputEvent.state

        wasActive = self.__isActive

        self.__isActive = (self.__lastValue >= self.__valueRange[0] and
                           self.__lastValue <= self.__valueRange[1] and
                           (self.__lastValue < self.__deadZone[0] or
                            self.__lastValue > self.__deadZone[1]))

        if self.__courier is not None:
            if wasActive != self.__isActive:
                if self.__isActive:
                    self.__courier.Send(InputActivated(self))
                else:
                    self.__courier.Send(InputDeactivated(self))

            self.__courier.Send(InputUpdated(self))

        return True

    def RawValue(self):
        return self.__lastValue

    def PercentValue(self):
        adjustedRange = self.__valueRange[1] - self.__deadZone[1] - (self.__valueRange[0] + self.__deadZone[0])
        rawValue = self.RawValue()

        if adjustedRange == 0:
            adjustedRange = 1

        if self.IsActive and rawValue is not None:
            adjustedValue = rawValue
        else:
            adjustedValue = 0

        adjustedValue -= self.__valueRange[0]

        percentage = (int(adjustedValue / adjustedRange*100))/100

        return percentage

    def __str__(self):
        return self.__name

class ButtonHandler(InputHandler):
    def __init__(self, inputMap, courier = None):
        InputHandler.__init__(self, inputMap, [0, 1], [0,0], courier)

class AnalogHandler(InputHandler):
    def __init__(self, inputMap, valueRange, deadZone = None, courier = None):
        InputHandler.__init__(self, inputMap, valueRange, deadZone, courier)

class TriggerHandler(AnalogHandler):
    def __init__(self, inputMap, courier = None):
        AnalogHandler.__init__(self, inputMap, [0, 255], [0,0], courier)

class StickHandler(AnalogHandler):
    def __init__(self, inputMap, courier = None):
        AnalogHandler.__init__(self, inputMap, [-32768, 32767], [-5000, 5000], courier)

# Maps

class InputMap:
    def __init__(self, name, code):
        self.Name = name
        self.Code = code

class XboxControllerInputs:
    X = InputMap("X", "BTN_WEST")
    Y = InputMap("Y", "BTN_NORTH")
    A = InputMap("A", "BTN_SOUTH")
    B = InputMap("B", "BTN_EAST")
    Start = InputMap("Start", "BTN_SELECT") # Start/Select inversion is intentional
    Select = InputMap("Select", "BTN_START")
    LeftShoulder = InputMap("Left Shoulder", "BTN_TL")
    RightShoulder = InputMap("Right Shoulder", "BTN_TR")
    DPadLeft = InputMap("D-Pad Left", "ABS_HAT0X") # -1
    DPadRight = InputMap("D-Pad Right", "ABS_HAT0X") # 1
    DPadUp = InputMap("D-Pad Up", "ABS_HAT0Y") # -1
    DPadDown = InputMap("D-Pad Down", "ABS_HAT0Y") # 1
    LeftTrigger = InputMap("Left Trigger", "ABS_Z")
    RightTrigger = InputMap("Right Trigger", "ABS_RZ")
    LeftStickXAxis = InputMap("Left Stick X-Axis", "ABS_X")
    LeftStickYAxis = InputMap("Left Stick Y-Axis", "ABS_Y")
    RightStickXAxis = InputMap("Right Stick X-Axis", "ABS_RX")
    RightStickYAxis = InputMap("Right Stick Y-Axis", "ABS_RY")

    # buttons = [
    #     ButtonHandler(courier, XboxControllerInputs.X),
    #     ButtonHandler(courier, XboxControllerInputs.Y),
    #     ButtonHandler(courier, XboxControllerInputs.A),
    #     ButtonHandler(courier, XboxControllerInputs.B),
    #     ButtonHandler(courier, XboxControllerInputs.Start),
    #     ButtonHandler(courier, XboxControllerInputs.Select),
    #     ButtonHandler(courier, XboxControllerInputs.LeftShoulder),
    #     ButtonHandler(courier, XboxControllerInputs.RightShoulder),
    #     AnalogHandler(courier, XboxControllerInputs.DPadLeft, [[-1, -1]]),
    #     AnalogHandler(courier, XboxControllerInputs.DPadRight, [[1, 1]]),
    #     AnalogHandler(courier, XboxControllerInputs.DPadUp, [[-1, -1]]),
    #     AnalogHandler(courier, XboxControllerInputs.DPadDown, [[1, 1]]),
    #     TriggerHandler(courier, XboxControllerInputs.LeftTrigger),
    #     TriggerHandler(courier, XboxControllerInputs.RightTrigger),
    #     StickHandler(courier, XboxControllerInputs.LeftStickXAxis),
    #     StickHandler(courier, XboxControllerInputs.LeftStickYAxis),
    #     StickHandler(courier, XboxControllerInputs.RightStickXAxis),
    #     StickHandler(courier, XboxControllerInputs.RightStickYAxis)
    # ]
