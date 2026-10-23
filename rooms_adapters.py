from datetime import datetime, timedelta
from domain.rooms import BookingEvent
from domain.exceptions import DomainError

class InMemoryEmployeeMessages:
    def __init__(self):
        self.messages: list[tuple[int, BookingEvent]] = []

    def send(self, employee_id: int, event: BookingEvent) -> None:
        self.messages.append((employee_id, event))

class ClockMovedBack(DomainError):
    pass

class ShiftedClock:
    def __init__(self):
        self._offset = timedelta(0)

    def now(self) -> datetime:
        return datetime.now() + self._offset

    def move_to(self, moment: datetime) -> None:
        system_now = datetime.now()
        if moment < system_now + self._offset:
            raise ClockMovedBack("Перевод часов назад запрещён")
        self._offset = moment - system_now