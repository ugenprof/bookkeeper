"""
Простой тестовый скрипт для терминала
"""

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.utils import read_tree

cat_repo = SQLiteRepository[Category](db_file="database/simple-client-sql.db",  # type: ignore
                                      cls=Category)
exp_repo = SQLiteRepository[Expense](db_file="database/simple-client-sql.db",  # type: ignore
                                     cls=Expense)
budget_repo = SQLiteRepository[Budget](db_file="database/simple-client-sql.db",  # type: ignore
                                       cls=Budget)

# pylint: disable=duplicate-code
if len(cat_repo.get_all()) == 0:
    cats = '''
    продукты
        мясо
            сырое мясо
            мясные продукты
        сладости
    книги
    одежда
    '''.splitlines()

    Category.create_from_tree(read_tree(cats), cat_repo)

if len(budget_repo.get_all(where={"period": "day"})) == 0:
    budget = Budget(period="day", limitation=1000, spent=0)
    budget_repo.add(budget)
if len(budget_repo.get_all(where={"period": "week"})) == 0:
    budget = Budget(period="week", limitation=7000, spent=0)
    budget_repo.add(budget)
if len(budget_repo.get_all(where={"period": "month"})) == 0:
    budget = Budget(period="month", limitation=30000, spent=0)
    budget_repo.add(budget)

for budget in budget_repo.get_all():
    budget.update_spent(exp_repo)
    budget_repo.update(budget)

# flake8: noqa
while True:
    try:
        cmd = input('$> ')
    except EOFError:
        break
    if not cmd:
        continue
    if cmd == 'категории':
        print(*cat_repo.get_all(), sep='\n')
    elif cmd == 'бюджет':
        print(*budget_repo.get_all(), sep='\n')
    elif cmd == 'расходы':
        print(*exp_repo.get_all(), sep='\n')
    elif cmd[0].isdecimal():
        amount, name = cmd.split(maxsplit=1)
        try:
            cat = cat_repo.get_all({'name': name})[0]
        except IndexError:
            print(f'категория {name} не найдена')
            continue
        exp = Expense(int(amount), cat.pk)
        exp_repo.add(exp)
        for budget in budget_repo.get_all():
            budget.update_spent(exp_repo)
            budget_repo.update(budget)
