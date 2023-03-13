""" Модуль описывает главное окно """
# pylint: disable=no-name-in-module
# pylint: disable=c-extension-no-member
# mypy: disable-error-code="attr-defined,union-attr"
from typing import Any
from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QEvent

from bookkeeper.view.budget import BudgetTableGroup
from bookkeeper.view.new_expense import NewExpenseGroup
from bookkeeper.view.expenses import ExpensesTableGroup
from bookkeeper.view.group_widgets import LabeledCheckBox
from bookkeeper.view.palette_mode import PaletteMode


class MainWindow(QtWidgets.QWidget):
    """ Главное окно приложения """

    def __init__(self,
                 budget_table: BudgetTableGroup,
                 new_expense: NewExpenseGroup,
                 expenses_table: ExpensesTableGroup,
                 *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.is_dark_mode: bool = True
        self.vbox = QtWidgets.QVBoxLayout()
        self.setWindowTitle("Bookkeeper")
        self.theme = LabeledCheckBox("Темная тема",
                                     init_state=Qt.Checked,
                                     chstate_func=self.change_theme)
        self.vbox.addWidget(self.theme, alignment=Qt.AlignRight)
        # Бюджет
        self.budget_table = budget_table
        self.vbox.addWidget(self.budget_table, stretch=3)
        # Новая трата
        self.new_expense = new_expense
        self.vbox.addWidget(self.new_expense, stretch=1)
        # Расходы
        self.expenses_table = expenses_table
        self.vbox.addWidget(self.expenses_table, stretch=6)
        self.setLayout(self.vbox)

    # pylint: disable=unused-argument
    def change_theme(self, status: Qt.CheckState) -> None:
        """ Изменяет тему (светлая или темная) """
        app = QtWidgets.QApplication.instance()
        if self.theme.check_box.isChecked():
            self.is_dark_mode = True
            app.setPalette(PaletteMode(is_dark_mode=True))
        else:
            self.is_dark_mode = False
            app.setPalette(PaletteMode(is_dark_mode=False))

    # pylint: disable=invalid-name
    def closeEvent(self, event: QEvent) -> None:
        """ Диалоговое окно при закрытии приложения """
        reply = QtWidgets.QMessageBox.question(
            self,
            'Закрыть приложение',
            "Вы уверены?\n"
            + "Все несохраненные данные будут потеряны.")
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            app = QtWidgets.QApplication.instance()
            app.closeAllWindows()
        else:
            event.ignore()