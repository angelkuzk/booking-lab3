class DomainError(Exception):
    """Базовая ошибка предметной области"""
    pass

class InvalidValueObject(DomainError):
    """Ошибка некорректного объекта значения"""
    pass

class DomainInvariantViolation(DomainError):
    """Ошибка нарушения бизнес-правила"""
    pass

class EntityNotFound(DomainError):
    """Ошибка: агрегат не найден в репозитории"""
    pass

class GatewayUnresolved(DomainError):
    """Ошибка: ни одно условие шлюза не выполнено"""
    pass

class TransitionNotAllowed(DomainError):
    """Ошибка: событие недопустимо в текущем состоянии"""
    def __init__(self, state: str, event: str):
        self.state = state
        self.event = event
        super().__init__(f"Событие {event} недопустимо в состоянии «{state}»")