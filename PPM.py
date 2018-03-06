# "RC PPM signal"

# Sync    1       2     3     4        5    6    7   8   Sync...
# ---+ +----+ +------+ +-+ +-------+ +--+ +--+ +--+ +-+ +----...
#    | |    | |      | | | |       | |  | |  | |  | | | |
#    | |    | |      | | | |       | |  | |  | |  | | | |
#    | |    | |      | | | |       | |  | |  | |  | | | |
#    +-+    +-+      +-+ +-+       +-+  +-+  +-+  +-+ +-+
#     *      *        *   *         *    *    *    *   *

#  * - low separator pulse, always 0.5 ms
#  1-8 - high "RC PWM pulse" for channels 1-8      0.5 – 1.5 ms
#  Sync: high frame separator pulse, typically 5 ms or longer.
# Value: 0%   = min channel duration (.5 ms)
#        100% = max channel duration (1.5 ms)

import pyaudio
from Component import Component

class PPMGenerator(Component):
    def __init__(self, channelCount, muteAudio = False):
        Component.__init__(self, "PPM Audio Signal Generator")
        self.SamplesPerMillisecond = 100 # min channel duration is .5ms, max is 1.5ms, usable duration is 1ms, 100% in 1ms = 100 samples
        self.BitRate = self.SamplesPerMillisecond * 1000
        self.LowValue = chr(0)
        self.HighValue = chr(127)
        self.FrameLength = 22.5 # ms
        self.FrameSamples = self.SamplesPerMillisecond * self.FrameLength
        self.MaximumChannelLength = self.SamplesPerMillisecond * 1.7
        self.MinimumChannelLength = self.SamplesPerMillisecond * .53 # slightly more than min, input seems to swap empty channels if I don't do this
        self.ChannelValueMilliseconds = self.MaximumChannelLength - self.MinimumChannelLength
        self.ChannelSeparatorLength = self.SamplesPerMillisecond * .4
        self.ChannelSeparatorBlock = self.LowValue * int(self.ChannelSeparatorLength)
        self.__channelCount = channelCount
        self.__audio = None

        if not muteAudio:
            self.__audio = pyaudio.PyAudio()

        self.__stream = None
        self.__isStarted = False
        self.__buffer = self.LowValue * int(self.FrameSamples) # prime buffer with nothing, prevent stream starvation

    def Buffer(self):
        return self.__buffer

    def __buildChannel(self, value):
        channelSize = self.MinimumChannelLength + value * self.ChannelValueMilliseconds
        channelBlock = self.HighValue * int(channelSize)

        channel = self.ChannelSeparatorBlock + channelBlock

        return channel

    def __buildFrame(self, channelValues):
        frame = ""

        for value in channelValues:
            frame += self.__buildChannel(value)

        # # separate sync block from last channel
        frame += self.ChannelSeparatorBlock
        # write high values for the remainder of the frame as sync block
        frame += self.HighValue * int((self.FrameSamples - len(frame)))

        return frame

    def Update(self, channelValues):
        if len(channelValues) != self.__channelCount:
            raise Exception("Provided " + str(len(channelValues)) + " values but require " + str(self.__channelCount))

        frame = self.__buildFrame(channelValues)
        self.__buffer = frame # swapping buffer's data, buffer is never depleted, just last values reused

    def Start(self):
        if self.__isStarted:
            return

        Component.Start(self)

        self.__isStarted = True

        if self.__audio is None:
            return

        loadFromBuffer = lambda in_data, frame_count, time_info, status: (self.__buffer, pyaudio.paContinue)

        self.__stream = self.__audio.open(format = self.__audio.get_format_from_width(1, True),
                                          channels = 1,
                                          rate = self.BitRate,
                                          output = True,
                                          frames_per_buffer = int(self.FrameSamples),
                                          stream_callback=loadFromBuffer)

    def Stop(self):
        if not self.__isStarted:
            return

        Component.Stop(self)

        self.__isStarted = False

        if self.__audio is None:
            return

        self.__stream.stop_stream()
        self.__stream.close()
        self.__audio.terminate()
