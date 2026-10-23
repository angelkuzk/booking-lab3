from .exceptions import DomainInvariantViolation
from .repositories import EmployeeRepository, OfficeRepository, RoomRepository
from .value_objects import (
    BookingId,
    BookingPeriod,
    EmployeeId,
    ParticipantCount,
    RoomId,
)


class BookRoomService:
    """
    Доменный сервис: операция «забронировать комнату».
    Требует одновременных данных агрегатов Office и Room:
      - часы работы офиса — из Office;
      - вместимость и текущие брони — из Room.
    """

    def __init__(
        self,
        offices: OfficeRepository,
        rooms: RoomRepository,
        employees: EmployeeRepository,
    ):
        self._offices = offices
        self._rooms = rooms
        self._employees = employees

    def book(
        self,
        room_id: RoomId,
        employee_id: EmployeeId,
        period: BookingPeriod,
        participants: ParticipantCount,
    ) -> BookingId:
        room = self._rooms.get(room_id)
        office = self._offices.get(room.office_id)
        employee = self._employees.get(employee_id)

        # Инвариант 3: бронь в пределах часов работы офиса
        if not office.work_hours.contains(period):
            raise DomainInvariantViolation(
                f"Бронь выходит за пределы часов работы офиса "
                f"({office.work_hours.open_time}–{office.work_hours.close_time})"
            )

        # Инварианты 1 и 2: проверяет сам агрегат Room
        booking_id = room.add_booking(
            period=period,
            employee_id=employee.id,
            participants=participants,
        )

        self._rooms.save(room)
        return booking_id