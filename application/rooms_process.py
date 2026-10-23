from datetime import datetime, timedelta
from typing import Protocol
from domain.booking_states import TransitionNotAllowed
from domain.rooms import (
    Booking, BookingId, RoomId, TimeSlot, ParticipantCount, BookingEvent,
    BookingRepository, RoomRepository, EmployeeRepository, GatewayUnresolved, DomainInvariantViolation
)

class Clock(Protocol):
    def now(self) -> datetime: ...

class EmployeeMessages(Protocol):
    def send(self, employee_id: int, event: BookingEvent) -> None: ...

# Предикаты
def manager_approved(result) -> bool: return result is True
def manager_rejected(result) -> bool: return result is False
def services_are_required(booking: Booking) -> bool: return booking.services_required
def services_are_not_required(booking: Booking) -> bool: return not booking.services_required
def cancellation_received(action: str) -> bool: return action == "cancel"
def meeting_started(action: str) -> bool: return action == "start"
def restriction_is_required(count: int) -> bool: return count >= 3
def restriction_is_not_required(count: int) -> bool: return count < 3

class BookingProcess:
    def __init__(self, rooms: RoomRepository, bookings: BookingRepository,
                 employees: EmployeeRepository, clock: Clock, messages: EmployeeMessages):
        self._rooms = rooms
        self._bookings = bookings
        self._employees = employees
        self._clock = clock
        self._messages = messages

    def _message(self, booking: Booking, name: str, now: datetime, to_employee: bool = False) -> None:
        event = booking.record_message(name, now)
        if to_employee:
            self._messages.send(booking.employee_id, event)

    def _save(self, booking: Booking) -> None:
        self._bookings.save(booking)

    def _notify_employee(self, booking: Booking) -> None:
        self._messages.send(booking.employee_id, booking.events[-1])

    def submit_booking(self, booking_id: BookingId, room_id: RoomId, slot: TimeSlot,
                       participants: ParticipantCount, employee_id: int, equipment=False, catering=False) -> Booking:
        if any(b.id == booking_id for b in self._bookings.all()):
            raise DomainInvariantViolation("ID бронирования уже существует")
        booking = Booking(booking_id, room_id, slot, participants,
                          submitted_at=self._clock.now(), employee_id=employee_id,
                          equipment=equipment, catering=catering)
        self._employees.get(booking.employee_id)
        available = self.check_room_availability(booking)
        restricted = self.check_employee_restriction(booking)
        booking.review_application(now=self._clock.now(), room_available=available,
                                   room_capacity=self._rooms.get(room_id).capacity,
                                   employee_restricted=restricted)
        if "approve_booking" in booking.allowed_events:
            self._message(booking, "Заявка направлена руководителю", self._clock.now())
        elif not booking.allowed_events:
            self._notify_employee(booking)
        else:
            self._prepare_booking(booking)
        self._save(booking)
        return booking

    def check_room_availability(self, booking: Booking) -> bool:
        room = self._rooms.get(booking.room_id)
        room.check_capacity(booking.participants)
        room.check_office_hours(booking.time_slot)
        return room.is_available(booking.time_slot)

    def check_employee_restriction(self, booking: Booking) -> bool:
        employee = self._employees.get(booking.employee_id)
        return employee.is_restricted(self._clock.now())

    def review_manager_application(self, booking_id: BookingId, approved: bool) -> None:
        booking = self._bookings.get(booking_id)
        now = self._clock.now()
        if "approve_booking" in booking.allowed_events and now >= booking.submitted_at + timedelta(hours=24):
            self.on_approval_timeout(now)
            return
        if manager_approved(approved):
            booking.approve_booking(now)
            self._prepare_booking(booking)
        elif manager_rejected(approved):
            booking.reject_booking(now)
            self._notify_employee(booking)
        else:
            raise GatewayUnresolved("Руководитель согласовал заявку?")
        self._save(booking)

    def _prepare_booking(self, booking: Booking) -> None:
        if services_are_required(booking):
            self.confirm_room(booking)
            requested = []
            if booking.equipment: requested.append("оборудование")
            if booking.catering: requested.append("кейтеринг")
            self._message(booking, "Администратору направлен заказ: " + ", ".join(requested), self._clock.now())
        elif services_are_not_required(booking):
            self.confirm_room(booking)
            self.notify_booking_ready(booking)
        else:
            raise GatewayUnresolved("Нужны оборудование или кейтеринг?")

    def confirm_room(self, booking: Booking) -> None:
        if "confirm_booking" not in booking.allowed_events:
            raise TransitionNotAllowed(booking.status, "confirm_booking")
        room = self._rooms.get(booking.room_id)
        room.reserve(booking.id, booking.participants, booking.time_slot)
        booking.mark_room_confirmed()
        self._rooms.save(room)

    def confirm_services_order(self, booking_id: BookingId, confirmed: bool) -> None:
        booking = self._bookings.get(booking_id)
        booking.mark_order_confirmed(confirmed)
        if confirmed:
            self._message(booking, "Заказ услуг подтверждён", self._clock.now())
            if booking.room_confirmed:
                self.notify_booking_ready(booking)
        self._save(booking)

    def notify_booking_ready(self, booking: Booking) -> None:
        booking.confirm_booking(now=self._clock.now(), room_confirmed=booking.room_confirmed,
                                services_required=booking.services_required,
                                order_confirmed=booking.order_confirmed)
        self._notify_employee(booking)

    def before_meeting(self, booking_id: BookingId, action: str) -> None:
        if cancellation_received(action):
            self.cancel_booking(booking_id)
        elif meeting_started(action):
            booking = self._bookings.get(booking_id)
            now = self._clock.now()
            booking.start_meeting(now)
            self._save(booking)
        else:
            raise GatewayUnresolved("Что произошло до начала встречи?")

    def cancel_booking(self, booking_id: BookingId) -> None:
        booking = self._bookings.get(booking_id)
        now = self._clock.now()
        booking.cancel_booking(now)
        self._free_room(booking)
        self._notify_employee(booking)
        self._save(booking)

    def wait_for_check_in(self, booking_id: BookingId) -> None:
        booking = self._bookings.get(booking_id)
        now = self._clock.now()
        booking.check_in(now)
        self._save(booking)

    def _free_room(self, booking: Booking) -> None:
        room = self._rooms.get(booking.room_id)
        room.release(booking.id)
        self._rooms.save(room)

    def finish_meeting(self, booking_id: BookingId) -> None:
        booking = self._bookings.get(booking_id)
        now = self._clock.now()
        booking.finish_meeting(now)
        self._free_room(booking)
        self._notify_employee(booking)
        self._save(booking)

    def on_approval_timeout(self, now: datetime) -> None:
        for booking in self._bookings.all():
            if ("approval_timeout" in booking.allowed_events
                    and now >= booking.submitted_at + timedelta(hours=24)):
                booking.approval_timeout(now)
                self._notify_employee(booking)
                self._save(booking)

    def on_meeting_started(self, now: datetime) -> None:
        for booking in self._bookings.all():
            if "start_meeting" in booking.allowed_events and now >= booking.time_slot.start:
                booking.start_meeting(now)
                self._save(booking)

    def on_check_in_timeout(self, now: datetime) -> None:
        for booking in self._bookings.all():
            if ("check_in_timeout" in booking.allowed_events
                    and now > booking.time_slot.start + timedelta(minutes=15)):
                booking.check_in_timeout(now)
                self._free_room(booking)
                employee = self._employees.get(booking.employee_id)
                employee.record_no_show(booking.time_slot.start.date())
                count = employee.no_show_count(booking.time_slot.start.date())
                self._notify_employee(booking)
                if restriction_is_required(count):
                    employee.restrict_large_rooms(booking.time_slot.start.date())
                    self._employees.save(employee)
                elif not restriction_is_not_required(count):
                    raise GatewayUnresolved("Это третья неявка за месяц?")
                self._save(booking)

    def on_meeting_finished(self, now: datetime) -> None:
        for booking in self._bookings.all():
            if "finish_meeting" in booking.allowed_events and now >= booking.time_slot.end:
                booking.finish_meeting(now)
                self._free_room(booking)
                self._notify_employee(booking)
                self._save(booking)