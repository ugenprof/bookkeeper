"""
Тесты для бюджета
"""
from datetime import datetime, timedelta
import pytest

from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense
from bookkeeper.repository.memory_repository import MemoryRepository


@pytest.fixture
def repo():
    return MemoryRepository()


def test_create_object():
    b = Budget(1000, "day")
    assert b.limitation == 1000
    assert b.pk == 0
    assert b.period == "day"
    assert b.spent == 0

    b = Budget(limitation=1000, period="week", spent=100)
    assert b.limitation == 1000
    assert b.pk == 0
    assert b.period == "week"
    assert b.spent == 100

    with pytest.raises(ValueError):
        b = Budget(limitation=1000, period="century")


def test_can_add_to_repo(repo):
    b = Budget(100, "day")
    pk = repo.add(b)
    assert b.pk == pk


def test_update_spent_day(repo):
    b = Budget(100, "day")
    for i in range(3):
        e = Expense(100, 1)
        repo.add(e)
    b.update_spent(repo)
    assert b.spent == 300


def test_update_spent_month(repo):
    b = Budget(100, "month")
    date = datetime.now().isoformat()[:8]
    for i in range(3):
        e = Expense(100, 1, expense_date=date+f"{i*5+1}")
        repo.add(e)
    e = Expense(100, 1, expense_date=date[:5]+"13-01")
    repo.add(e)
    b.update_spent(repo)
    assert b.spent == 300


def test_update_spent_week(repo):
    b = Budget(100, "week")
    date = datetime.now().isoformat()[:10]
    weekday_now = datetime.now().weekday()
    day_now = datetime.fromisoformat(date)
    first_week_day = day_now - timedelta(days=weekday_now)
    for i in range(9):
        day = first_week_day + timedelta(days=i-1)
        e = Expense(100, 1, expense_date=day.isoformat(
            sep='\t', timespec='minutes'))
        repo.add(e)
    b.update_spent(repo)
    assert b.spent == 700