from collector.services.providers.uber_provider import UberProvider
from collector.services.providers.ola_provider import OlaProvider
from collector.services.providers.rapido_provider import RapidoProvider


class ProviderFactory:
    """
    Creates fare provider objects.
    """

    @staticmethod
    def create(provider_name):
        """
        Creates and returns the requested fare provider.
        """

        provider_name = provider_name.lower()

        if provider_name == "uber":
            return UberProvider()

        elif provider_name == "ola":
            return OlaProvider()

        elif provider_name == "rapido":
            return RapidoProvider()

        else:
            raise ValueError(
                f"Unsupported provider: {provider_name}"
            )