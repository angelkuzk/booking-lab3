from uuid import UUID

from domain.employee import Employee
from domain.exceptions import EntityNotFound
from domain.office import Office
from domain.rooms import Room
from domain.value_objects import EmployeeId, OfficeId, RoomId


class InMemoryOfficeRepository:
    def __init__(self):
        self._storage: dict[UUID, Office] = {}

    def get(self, office_id: OfficeId) -> Office:
        try:
            return self._storage[office_id.value]
        except KeyError:
            raise EntityNotFound(f"Office {office_id.value} не найден")

    def save(self, office: Office) -> None:
        self._storage[office.id.value] = office


class InMemoryRoomRepository:
    def __init__(self):
        self._storage: dict[UUID, Room] = {}

    def get(self, room_id: RoomId) -> Room:
        try:
            return self._storage[room_id.value]
        except KeyError:
            raise EntityNotFound(f"Room {room_id.value} не найден")

    def save(self, room: Room) -> None:
        self._storage[room.id.value] = room


class InMemoryEmployeeRepository:
    def __init__(self):
        self._storage: dict[UUID, Employee] = {}

    def get(self, employee_id: EmployeeId) -> Employee:
        try:
            return self._storage[employee_id.value]
        except KeyError:
            raise EntityNotFound(f"Employee {employee_id.value} не найден")

    def save(self, employee: Employee) -> None:
        self._storage[employee.id.value] = employee