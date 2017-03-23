try:
    import Adafruit_BMP.BMP085 as BMP085
except ImportError:
    pass


class TemperatureProvider:
    def __init__(self):
        pass

    def temp(self):
        raise NotImplementedError("Should have implemented this")

    @staticmethod
    def get(config):
        key = config["metrics"]["provider"]

        if key == "dummy":
            return DummyProvider()

        if key == "bmp085":
            return BMP085Provider()

        raise IndexError("Unknown key provider key %s given.")


class DummyProvider(TemperatureProvider):
    def temp(self):
        return 370


class BMP085Provider(TemperatureProvider):
    def __init__(self):
        TemperatureProvider.__init__(self)

        self.sensor = BMP085.BMP085()

    def temp(self):
        return round(self.sensor.read_temperature() * 10)
