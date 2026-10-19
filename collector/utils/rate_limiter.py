import time


class RateLimiter:
    """
    Ensures that API requests are not sent faster than
    the configured rate.
    """

    def __init__(self, requests_per_second):

        self.minimum_interval = 1.0 / requests_per_second

        self.last_request_time = 0.0

    def wait_if_needed(self):
        """
        Sleeps if the previous request was sent too recently.
        """

        current_time = time.monotonic()

        elapsed = current_time - self.last_request_time

        if elapsed < self.minimum_interval:
            time.sleep(
                self.minimum_interval - elapsed
            )

        self.last_request_time = time.monotonic()