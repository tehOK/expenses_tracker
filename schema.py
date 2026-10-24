from datetime import datetime

from pydantic import BaseModel, Field, field_validator

CATEGORIES = {"еда", "транспорт", "одежда", "прочее"}


class ExpenseDTO(BaseModel):
    id: int
    amount: float = Field(gt=0, description="Сумма должна быть > 0")
    category: str = Field(min_length=2)
    description: str = Field(min_length=2)
    date: datetime = Field(default_factory=datetime.now)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in CATEGORIES:
            raise ValueError(f"Категория должна быть в списке {CATEGORIES}")
        return v


class Expenses(BaseModel):
    expenses: list[ExpenseDTO]


class ExpensesReportDTO(BaseModel):
    time_from: datetime
    time_to: datetime
