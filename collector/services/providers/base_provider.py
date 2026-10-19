from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    Base class for all fare providers.
    Every provider must implement these methods.
    """

    @property
    @abstractmethod
    def provider_name(self):
        """
        Returns the provider name.
        Example:
            Uber
            Ola
            Rapido
        """
        pass

    @abstractmethod
    def launch(self):
        """
        Performs any initialization required by the provider.

        Example:
            - Launch browser
            - Open page
            - Create browser context
        """
        pass

    @abstractmethod
    def collect_fares(self, trip):
        """
        Collects fare estimates for a single trip.

        Parameters
        ----------
        trip : pandas.Series
            A single row from routes.csv.

        Returns
        -------
        list
            A list of fare dictionaries.
        """
        pass

    @abstractmethod
    def close(self):
        """
        Releases all resources used by the provider.

        Example:
            - Close browser
            - Stop Playwright
        """
        pass