import json
from collections import Counter
from pathlib import Path

from pydantic import ValidationError

from schema import ExpenseDTO, Expenses, ExpensesReportDTO


class ExpensesManager:
    FILE = Path("expenses.json")

    def __init__(self):
        self._expenses = self._load()
        self._next_id = self._next_id()

    def _save(self) -> None:
        self.FILE.write_text(self._expenses.model_dump_json(indent=2), encoding="utf-8")

    def _load(self) -> Expenses:
        if not self.FILE.exists() or not self.FILE.stat().st_size:
            return Expenses(expenses=[])
        try:
            return Expenses.model_validate_json(self.FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Ошибка загрузки:\n{e!s}")
            return Expenses(expenses=[])

    def _next_id(self) -> int:
        return max((exp.id for exp in self._expenses.expenses), default=0) + 1

    def add(self, data: list[str] | None) -> None:
        if not data or len(data) != 3:
            print("Структура команды ADD <сумма> <категория> <описание>")
            return

        try:
            to_add = ExpenseDTO(
                id=self._next_id,
                amount=data[0],
                category=data[1],
                description=data[2],
            )
        except ValidationError as e:
            print(f"Ошибка валидации.\n{e!s}")
            return

        self._expenses.expenses.append(to_add)
        self._save()
        self._next_id += 1
        print(
            f"Расход №{to_add.id} добавлен: {to_add.amount} {to_add.category} {to_add.description}"
        )

    def list_expenses(self, data: list[str] | None) -> None:
        if not self._expenses.expenses:
            print("Трат пока нет")
            return
        for exp in self._expenses.expenses:
            print(
                f"#{exp.id} [{exp.date.strftime('%Y-%m-%d %H:%M')}] {exp.amount} {exp.category} {exp.description}"
            )
        return

    def delete(self, data: list[str] | None) -> None:
        if not data:
            print("Напишите номер для удаления")
            return
        try:
            exp_id = int(data[0])
        except ValueError:
            print("Напишите номер для удаления")
            return
        for index, exp in enumerate(self._expenses.expenses):
            if exp_id == exp.id:
                self._expenses.expenses.pop(index)
                self._save()
                print(f"Расход №{exp_id} удалён")
                return
        print(f"Расхода с таким {exp_id=} не найдено")

    def find(self, data: list[str] | None) -> None:
        if not data:
            print("Введите категорию для поиска")
            return
        category = data[0]
        count = 0
        for exp in self._expenses.expenses:
            if exp.category == category:
                count += 1
                print(
                    f"#{exp.id} [{exp.date.strftime('%Y-%m-%d %H:%M')}] {exp.amount} {exp.category} {exp.description}"
                )
        if not count:
            print(f"Расходов а категории '{category}' нет")
            return
        print(f"Всего расходов: {count}")

    def report(self, data: list[str] | None) -> None:
        if not data or len(data) < 2:
            print("Введите две даты: report <YYYY-MM-DD> <YYYY-MM-DD>")
            return
        try:
            report_time = ExpensesReportDTO(time_from=data[0], time_to=data[1])
        except ValidationError as e:
            print(f"Ошибка в датах:\n{e!s}")
            return

        if not self._expenses.expenses:
            print("Трат пока нет")
            return

        report = {}
        count = 0
        for exp in self._expenses.expenses:
            if report_time.time_from <= exp.date <= report_time.time_to:
                count += 1
                report[exp.category] = report.get(exp.category, 0) + exp.amount
        print(report)
        if not report:
            print("Трат за этот период нет")
            return
        print(f"Расходов: {count}, на сумму {sum(report.values())}")
        total = sum(report.values())
        for category, amount in sorted(report.items(), key=lambda x: -x[1]):
            pct = amount / total * 100
            print(f"  {category:<12} {amount:>10.2f} ₽  ({pct:.1f}%)")

    def top(self, data: list[str] | None) -> None:
        if not data:
            print("Напишите число для вывода списка топ")
            return
        try:
            n_top = int(data[0])
        except ValueError:
            print("Напишите число для вывода списка топ")
            return
        counter = Counter()
        for exp in self._expenses.expenses:
            counter[exp.category] += exp.amount

        if not counter:
            print("Трат пока нет")
            return

        for num, (category, amount) in enumerate(counter.most_common(n_top), start=1):
            print(f"{num}. {category:<10} -  {amount:.2f}")
