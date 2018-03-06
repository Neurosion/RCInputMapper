

from inputs import devices, UnpluggedError
from InputHandling import StickHandler, TriggerHandler, ButtonHandler, XboxControllerInputs
from PPM import PPMGenerator
from Visualization import Plotter

def main(showVisualizer = False, playAudio = True):
    if len(devices.gamepads) == 0:
        print("A gamepad is required but was not found.")
        raise SystemExit()

    gamepad = devices.gamepads[0]

    ChannelCount = 8

    # Setup inputs per channel
    channelInputs = [None] * ChannelCount
    channelInputs[0] = StickHandler(XboxControllerInputs.LeftStickXAxis)
    channelInputs[1] = StickHandler(XboxControllerInputs.LeftStickYAxis)
    channelInputs[2] = StickHandler(XboxControllerInputs.RightStickXAxis)
    channelInputs[3] = StickHandler(XboxControllerInputs.RightStickYAxis)
    channelInputs[4] = TriggerHandler(XboxControllerInputs.RightTrigger)
    channelInputs[5] = ButtonHandler(XboxControllerInputs.LeftShoulder)
    channelInputs[6] = ButtonHandler(XboxControllerInputs.RightShoulder)

    # Input to trigger exit
    exitInput = ButtonHandler(XboxControllerInputs.Start)

    # Display channel input configuration
    for index in range(0, ChannelCount):
        print("Channel " + str(index+1) + ": " + str(channelInputs[index]))

    print("Exit: " + str(exitInput))

    generator = PPMGenerator(ChannelCount, muteAudio = not playAudio)
    generator.Start()

    visualizer = Plotter() if showVisualizer else None

    if visualizer is not None:
        visualizer.Start()

    frame = [0] * ChannelCount

    while not exitInput.IsActive:
        try:
            for event in gamepad.forceRead():
                for currentInput in channelInputs:
                    if currentInput is not None:
                        currentInput.Handle(event)
                exitInput.Handle(event)
        except UnpluggedError:
            pass

        for index in range(0, ChannelCount):
            if channelInputs[index] is not None:
                frame[index] = channelInputs[index].PercentValue()

        generator.Update(frame)

        if visualizer is not None:
            visualizer.Update(generator.Buffer())

    generator.Stop()

    if visualizer is not None:
        visualizer.Stop()

    raise SystemExit

if __name__ == "__main__":
    main()
