
class Space:
    def __init__(self, **kwargs):
        self._dimensions = None
        self._entities = {}
        self._scaling_factor = 1

    def set_dimensions(self, dimensions):
        """
        Assumes a rectangular representation for now
        :return:
        """
        self._dimensions = dimensions

    def set_scaling_factor(self, scaling_factor):
        """
        set the scaling factor, real world to gui representation
        :param scaling_factor: float or int
        :return: None
        """
        self._scaling_factor = scaling_factor

    def add_robot_to_space(self, *args):
        """
        Adds a robot to the space
        :param robot: Robot object
        :return: None
        """
        for robot in args:
            self._entities[robot.uri] = robot

    def add_network_to_space(self, *args):
        """
        Adds a network to the space
        :param network: Network Object
        :return: None
        """
        for network in args:
            self._entities[network.id] = network

    def add_object_to_space(self, *args):
        """
        Adds an object to the space
        :param _object: object representing object
        :return: None
        """
        for _object in args:
            self._entities[_object.id] = _object

    @property
    def entities(self):
        return self._entities


