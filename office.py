from .exceptions import DomainInvariantViolation
from .value_objects import OfficeId, RoomId, WorkHours


class Office:
    def __init__(self, office_id: OfficeId, name: str, work_hours: WorkHours):
        if not name.strip():
            raise DomainInvariantViolation("Название офиса не может быть пустым")
        self._id = office_id
        self._name = name
        self._work_hours = work_hours
        self._room_ids: list[RoomId] = []

    @property
    def id(self) -> OfficeId:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def work_hours(self) -> WorkHours:
        return self._work_hours

    @property
    def room_ids(self) -> tuple[RoomId, ...]:
        return tuple(self._room_ids)

    def add_room(self, room_id: RoomId) -> None:
        self._room_ids.append(room_id)

    def remove_room(self, room_id: RoomId) -> None:
        self._room_ids.remove(room_id)

    def change_work_hours(self, work_hours: WorkHours) -> None:
        self._work_hours = work_hours