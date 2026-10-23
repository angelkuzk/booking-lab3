from dataclasses import dataclass
from datetime import time
from uuid import UUID

from .exceptions import InvalidValueObject


@dataclass(frozen=True)
class OfficeId:
    value: UUID

    def __post_init__(self):
        if not isinstance(self.value, UUID):
            raise InvalidValueObject("OfficeId должен быть UUID")


@dataclass(frozen=True)
class RoomId:
    value: UUID

    def __post_init__(self):
        if not isinstance(self.value, UUID):
            raise InvalidValueObject("RoomId должен быть UUID")


@dataclass(frozen=True)
class EmployeeId:
    value: UUID

    def __post_init__(self):
        if not isinstance(self.value, UUID):
            raise InvalidValueObject("EmployeeId должен быть UUID")


@dataclass(frozen=True)
class BookingId:
    value: UUID

    def __post_init__(self):
        if not isinstance(self.value, UUID):
            raise InvalidValueObject("BookingId должен быть UUID")


@dataclass(frozen=True)
class ParticipantCount:
    value: int

    def __post_init__(self):
        if not isinstance(self.value, int):
            raise InvalidValueObject("Число участников должно быть целым числом")
        if self.value <= 0:
            raise InvalidValueObject(
                f"Число участников должно быть положительным, получено: {self.value}"
            )


@dataclass(frozen=True)
class WorkHours:
    """Часы работы офиса в течение дня."""

    open_time: time
    close_time: time

    def __post_init__(self):
        if self.open_time >= self.close_time:
            raise InvalidValueObject(
                "Время открытия должно быть раньше времени закрытия"
            )

    def contains(self, period: "BookingPeriod") -> bool:
        start = period.start.time()
        end = period.end.time()
        return self.open_time <= start and end <= self.close_time


@dataclass(frozen=True)
class BookingPeriod:
    start: "datetime"
    end: "datetime"

    def __post_init__(self):
        from datetime import datetime
        if not isinstance(self.start, datetime) or not isinstance(self.end, datetime):
            raise InvalidValueObject("BookingPeriod требует datetime")
        if self.end <= self.start:
            raise InvalidValueObject(
                "Время окончания брони должно быть позже времени начала"
            )

    def overlaps(self, other: "BookingPeriod") -> bool:
        return self.start < other.end and other.start < self.end