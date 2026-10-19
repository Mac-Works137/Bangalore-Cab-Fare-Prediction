from abc import ABC, abstractmethod


class FareCollector(ABC):
    """
    Base class for every cab provider.
    """

    def __init__(self):

        self.provider_name = None

    @abstractmethod
    def launch(self):
        """
        Launch provider resources.
        """
        pass

    @abstractmethod
    def collect_route(self, route, context):
        """
        Collect fares for a single route.

        Parameters
        ----------
        route : dict

        context : dict

        Returns
        -------
        list[FareEstimate]
        """
        pass

    @abstractmethod
    def close(self):
        """
        Cleanup.
        """
        pass