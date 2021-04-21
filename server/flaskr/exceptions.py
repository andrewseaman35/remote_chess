class InvalidConfigurationException(Exception):
    """
    Exceptions raised due to invalid configuration files or values.
    """
    pass


class OctoPrintException(Exception):
    pass


class AxisControllerException(Exception):
    pass


class MotorControllerException(Exception):
    pass
