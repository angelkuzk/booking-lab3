from .exceptions import DomainInvariantViolation
from .value_objects import EmployeeId


class Employee:
    """Агрегат Employee. Корень агрегата. Справочник сотрудников."""

    def __init__(self, employee_id: EmployeeId, full_name: str, department: str):
        if not full_name.strip():
            raise DomainInvariantViolation("Имя сотрудника не может быть пустым")
        if not department.strip():
            raise DomainInvariantViolation("Отдел не может быть пустым")
        self._id = employee_id
        self._full_name = full_name
        self._department = department

    @property
    def id(self) -> EmployeeId:
        return self._id

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def department(self) -> str:
        return self._department