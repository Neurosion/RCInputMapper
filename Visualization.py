import time
import numpy
from matplotlib import pyplot, ticker
from Component import Component

class Plotter(Component):
    def __init__(self, updateFrequency = 2):
        Component.__init__(self, "PPM Signal Visualizer")
        self.__updateFrequency = updateFrequency
        self.__isStarted = False
        self.__lastUpdateTime = None
        self.__axisStart = 0

    def __convertData(self, data):
        if data is None:
            return

        if isinstance(data, str):
            return [ord(x) for x in data]

        return data

    def Update(self, data):
        now = time.clock()

        if self.__lastUpdateTime is not None:
            if now - self.__lastUpdateTime < self.__updateFrequency:
                return

        convertedData = self.__convertData(data)
        dataLength = len(convertedData)
        axisEnd = self.__axisStart + dataLength
        x = numpy.arange(self.__axisStart, axisEnd)

        pyplot.xlim(self.__axisStart, axisEnd)
        pyplot.plot(x, convertedData, color='green')
        pyplot.pause(0.05)

        self.__axisStart += dataLength
        self.__lastUpdateTime = now

    def Start(self):
        if self.__isStarted:
            return

        Component.Start(self)

        figure = pyplot.figure()
        figure.canvas.set_window_title("PPM Signal - Updated every " + str(self.__updateFrequency) + " seconds")
        pyplot.ion()

        axes = pyplot.gca()
        axes.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: "{0:g}".format(x/100)))
        pyplot.title("PPM Snapshot")
        pyplot.xlabel("milliseconds")
        axes.set_yticks([])

        self.__isStarted = True

    def Stop(self):
        if not self.__isStarted:
            return

        Component.Stop(self)
        pyplot.close()

        self.__isStarted = False
