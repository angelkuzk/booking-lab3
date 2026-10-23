from datetime import datetime, time, timedelta
from application.rooms_process import BookingProcess
from infrastructure.rooms_repository import InMemoryRoomRepository, InMemoryBookingRepository, InMemoryEmployeeRepository
from infrastructure.rooms_adapters import ShiftedClock, InMemoryEmployeeMessages
from domain.rooms import RoomId, BookingId, TimeSlot, ParticipantCount, MeetingRoom, Employee

def main():
    # 1. инициализируем инфраструктуру
    rooms = InMemoryRoomRepository()
    bookings = InMemoryBookingRepository()
    employees = InMemoryEmployeeRepository()
    clock = ShiftedClock()
    messages = InMemoryEmployeeMessages()

    # создаем комнаты (рабочие часы 09:00 - 18:00)
    rooms.save(MeetingRoom(RoomId(1), "Малая переговорная", 6, time(9), time(18)))
    rooms.save(MeetingRoom(RoomId(2), "Большая переговорная", 12, time(9), time(18)))
    employees.save(Employee(1))

    process = BookingProcess(
        rooms=rooms, 
        bookings=bookings, 
        employees=employees, 
        clock=clock, 
        messages=messages
    )

    # устанавливаем время 
    now_dt = datetime.now()
    start_time = (now_dt + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    clock.move_to(start_time)

    print("=== ТЕСТ: Подача заявки на большую комнату ===")
    
    # время встречи: через 3 дня, ровно в 10:00 утра (внутри рабочих часов)
    meeting_start = start_time + timedelta(days=3)
    meeting_start = meeting_start.replace(hour=10, minute=0)
    
    booking_slot = TimeSlot(
        start=meeting_start, 
        end=meeting_start + timedelta(hours=2) # Закончится в 12:00
    )
    
    # подаем заявку (на 12 человек, нужно согласование)
    booking = process.submit_booking(
        booking_id=BookingId(101),
        room_id=RoomId(2),
        slot=booking_slot,
        participants=ParticipantCount(12),
        employee_id=1
    )
    
    print(f"Статус после подачи: {booking.status}")
    print(f"Допустимые события: {booking.allowed_events}")
    
    print("\n=== ТЕСТ: Согласование руководителем ===")
    # сдвигаем время на 1 час вперед
    clock.move_to(start_time + timedelta(hours=1))
    process.review_manager_application(BookingId(101), approved=True)
    
    booking = bookings.get(BookingId(101))
    print(f"Статус после согласования: {booking.status}")
    print(f"Допустимые события: {booking.allowed_events}")

    print("\n=== ТЕСТ: Отмена ===")
    clock.move_to(start_time + timedelta(hours=2))
    process.cancel_booking(BookingId(101))
    
    booking = bookings.get(BookingId(101))
    print(f"Статус после отмены: {booking.status}")

    print("\n=== СООБЩЕНИЯ ===")
    for emp_id, event in messages.messages:
        print(f"Сотруднику {emp_id} отправлено: {event.name}")

if __name__ == "__main__":
    main()