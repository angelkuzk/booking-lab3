from typing import Protocol

from .employee import Employee
from .office import Office
from .rooms import Room
from .value_objects import EmployeeId, OfficeId, RoomId


class OfficeRepository(Protocol):
    def get(self, office_id: OfficeId) -> Office: ...
    def save(self, office: Office) -> None: ...


class RoomRepository(Protocol):
    def get(self, room_id: RoomId) -> Room: ...
    def save(self, room: Room) -> None: ...


class EmployeeRepository(Protocol):
    def get(self, employee_id: EmployeeId) -> Employee: ...
    def save(self, employee: Employee) -> None: ...