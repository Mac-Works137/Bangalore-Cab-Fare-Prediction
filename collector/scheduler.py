from datetime import datetime

from zoneinfo import ZoneInfo

from config.collection_schedule import (
    TIME_SLOTS,
    TIMEZONE,
)


class CollectionScheduler:
    """
    Determines the current collection slot and batch timestamp.
    """

    def __init__(self):

        self.timezone = ZoneInfo(TIMEZONE)

    def get_collection_context(self):
        """
        Returns metadata shared by every fare collected
        during the current execution.
        """

        now = datetime.now(self.timezone)

        return {
            "search_timestamp": now,
            "time_slot": self._get_current_slot(now),
            "day_of_week": now.strftime("%A"),
        }

    def _get_current_slot(self, now):
        """
        Returns the collection slot corresponding to the current time.

        Examples
        --------
        00:30 -> 00:00
        08:45 -> 00:00
        09:20 -> 09:00
        12:59 -> 12:00
        18:15 -> 18:00
        23:10 -> 21:00
        """

        current_minutes = now.hour * 60 + now.minute

        slots = []

        for slot in TIME_SLOTS:

            hour, minute = map(int, slot.split(":"))

            slot_minutes = hour * 60 + minute

            slots.append((slot_minutes, slot))

        # Sort chronologically:
        # 00:00, 09:00, 12:00, 15:00, 18:00, 21:00
        slots.sort()

        selected_slot = slots[0][1]

        for slot_minutes, slot in slots:

            if current_minutes >= slot_minutes:
                selected_slot = slot
            else:
                break

        return selected_slot