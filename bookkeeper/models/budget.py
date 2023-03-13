"""
Модель бюджета
"""
from dataclasses import dataclass
from datetime import datetime, timedelta

from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.models.expense import Expense


@dataclass
class Budget:
    """
    Бюджет, атрибуты:
    period - хранит название периода,
    limit - хранит сумму затрат на период
    wastes - хранит уже потраченную за период сумму

    """
    limit: int
    period: str
    wastes: int = 0
    pk: int = 0

    def __init__(self, limit: int, period: str,
                 wastes: int = 0, pk: int = 0):
        if period not in ["day", "week", "month"]:
            raise ValueError(f'unknown period "{period}" for budget'
                             + 'should be "day", "week" or "month"')
        self.limit = limit
        self.period = period
        self.wastes = wastes
        self.pk = pk

    def update_wastes(self, exp_repo: AbstractRepository[Expense]) -> None:  # type: ignore
        """ Обновляет траты за период бюждетов по заданному репозиторию exp_repo """
        date = datetime.now().isoformat()[:10]  # YYYY-MM-DD format
        if self.period.lower() == "day":
            date_mask = f"{date}"
            period_exps = exp_repo.get_all_like(like={"expense_date": date_mask})
        elif self.period.lower() == "week":
            weekday_now = datetime.now().weekday()
            day_now = datetime.fromisoformat(date)
            first_week_day = day_now - timedelta(days=weekday_now)
            period_exps = []
            for i in range(7):
                weekday = first_week_day + timedelta(days=i)
                date_mask = f"{weekday.isoformat()[:10]}"
                period_exps += exp_repo.get_all_like(like={"expense_date": date_mask})
        elif self.period.lower() == "month":
            date_mask = f"{date[:7]}-"
            period_exps = exp_repo.get_all_like(like={"expense_date": date_mask})
        self.wastes = sum(int(exp.amount) for exp in period_exps)
