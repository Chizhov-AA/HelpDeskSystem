import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit, QComboBox,
    QTextEdit, QMessageBox, QFormLayout, QSpinBox
)
from PyQt5.QtCore import Qt

import database as db


class HelpDeskWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HelpDeskSystem — учет заявок технической поддержки")
        self.setMinimumSize(1050, 650)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.users_table = QTableWidget()
        self.engineers_table = QTableWidget()
        self.requests_table = QTableWidget()
        self.assignments_table = QTableWidget()
        self.stats_table = QTableWidget()

        self.search_input = QLineEdit()
        self.status_filter = QComboBox()

        self.new_title = QLineEdit()
        self.new_description = QTextEdit()
        self.new_priority = QComboBox()
        self.new_user = QComboBox()

        self.assign_request = QSpinBox()
        self.assign_engineer = QComboBox()
        self.assign_comment = QLineEdit()

        self.status_request_id = QSpinBox()
        self.status_value = QComboBox()

        self.create_tabs()
        self.refresh_all()

    def create_tabs(self):
        self.tabs.addTab(self.create_home_tab(), "Главная")
        self.tabs.addTab(self.create_users_tab(), "Пользователи")
        self.tabs.addTab(self.create_engineers_tab(), "Инженеры")
        self.tabs.addTab(self.create_requests_tab(), "Заявки")
        self.tabs.addTab(self.create_new_request_tab(), "Новая заявка")
        self.tabs.addTab(self.create_assignment_tab(), "Назначения")
        self.tabs.addTab(self.create_status_tab(), "Статус")
        self.tabs.addTab(self.create_statistics_tab(), "Статистика")

    def create_home_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Информационная система учета заявок службы технической поддержки")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 20px;")

        description = QLabel(
            "Система предназначена для регистрации заявок пользователей, "
            "назначения инженеров, контроля статусов и анализа загрузки службы поддержки."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)

        refresh_button = QPushButton("Обновить данные")
        refresh_button.clicked.connect(self.refresh_all)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(refresh_button)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def create_users_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Список пользователей предприятия"))
        layout.addWidget(self.users_table)
        widget.setLayout(layout)
        return widget

    def create_engineers_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Список сотрудников службы технической поддержки"))
        layout.addWidget(self.engineers_table)
        widget.setLayout(layout)
        return widget

    def create_requests_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        filter_layout = QHBoxLayout()
        self.search_input.setPlaceholderText("Поиск по теме, описанию или ФИО пользователя")
        self.status_filter.addItems(["Все", "Новая", "В работе", "Закрыта"])
        search_button = QPushButton("Найти")
        search_button.clicked.connect(self.load_requests)

        filter_layout.addWidget(QLabel("Статус:"))
        filter_layout.addWidget(self.status_filter)
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(search_button)

        layout.addLayout(filter_layout)
        layout.addWidget(self.requests_table)

        widget.setLayout(layout)
        return widget

    def create_new_request_tab(self):
        widget = QWidget()
        layout = QFormLayout()

        self.new_priority.addItems(["Низкий", "Средний", "Высокий"])

        save_button = QPushButton("Создать заявку")
        save_button.clicked.connect(self.create_request)

        layout.addRow("Тема:", self.new_title)
        layout.addRow("Описание:", self.new_description)
        layout.addRow("Приоритет:", self.new_priority)
        layout.addRow("Пользователь:", self.new_user)
        layout.addRow(save_button)

        widget.setLayout(layout)
        return widget

    def create_assignment_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        form = QFormLayout()

        self.assign_request.setMinimum(1)
        self.assign_request.setMaximum(999999)

        assign_button = QPushButton("Назначить инженера")
        assign_button.clicked.connect(self.create_assignment)

        form.addRow("ID заявки:", self.assign_request)
        form.addRow("Инженер:", self.assign_engineer)
        form.addRow("Комментарий:", self.assign_comment)
        form.addRow(assign_button)

        layout.addLayout(form)
        layout.addWidget(QLabel("История назначений"))
        layout.addWidget(self.assignments_table)

        widget.setLayout(layout)
        return widget

    def create_status_tab(self):
        widget = QWidget()
        layout = QFormLayout()

        self.status_request_id.setMinimum(1)
        self.status_request_id.setMaximum(999999)
        self.status_value.addItems(["Новая", "В работе", "Закрыта"])

        update_button = QPushButton("Изменить статус")
        update_button.clicked.connect(self.change_status)

        layout.addRow("ID заявки:", self.status_request_id)
        layout.addRow("Новый статус:", self.status_value)
        layout.addRow(update_button)

        widget.setLayout(layout)
        return widget

    def create_statistics_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        refresh_button = QPushButton("Обновить статистику")
        refresh_button.clicked.connect(self.load_statistics)

        layout.addWidget(QLabel("Количество заявок по статусам"))
        layout.addWidget(refresh_button)
        layout.addWidget(self.stats_table)

        widget.setLayout(layout)
        return widget

    def fill_table(self, table, rows, headers):
        table.clear()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            for col_index, key in enumerate(headers.keys()):
                value = str(row[key])
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                table.setItem(row_index, col_index, item)

        table.resizeColumnsToContents()

    def refresh_all(self):
        self.load_users()
        self.load_engineers()
        self.load_requests()
        self.load_assignments()
        self.load_statistics()
        self.load_combo_values()

    def load_users(self):
        self.fill_table(
            self.users_table,
            db.get_users(),
            {
                "id": "ID",
                "full_name": "ФИО",
                "department": "Отдел",
                "phone": "Телефон",
                "email": "Email",
            },
        )

    def load_engineers(self):
        self.fill_table(
            self.engineers_table,
            db.get_engineers(),
            {
                "id": "ID",
                "full_name": "ФИО",
                "position": "Должность",
                "phone": "Телефон",
                "email": "Email",
            },
        )

    def load_requests(self):
        status = self.status_filter.currentText()
        search_text = self.search_input.text().strip()
        self.fill_table(
            self.requests_table,
            db.get_requests(status=status, search_text=search_text),
            {
                "id": "ID",
                "title": "Тема",
                "priority": "Приоритет",
                "status": "Статус",
                "created_at": "Дата",
                "user_name": "Пользователь",
                "department": "Отдел",
            },
        )

    def load_assignments(self):
        self.fill_table(
            self.assignments_table,
            db.get_assignments(),
            {
                "id": "ID",
                "request_title": "Заявка",
                "engineer_name": "Инженер",
                "assign_date": "Дата назначения",
                "comment": "Комментарий",
            },
        )

    def load_statistics(self):
        self.fill_table(
            self.stats_table,
            db.get_statistics(),
            {
                "status": "Статус",
                "count": "Количество",
            },
        )

    def load_combo_values(self):
        self.new_user.clear()
        for user in db.get_users():
            self.new_user.addItem(f"{user['id']} — {user['full_name']}", user["id"])

        self.assign_engineer.clear()
        for engineer in db.get_engineers():
            self.assign_engineer.addItem(
                f"{engineer['id']} — {engineer['full_name']}", engineer["id"]
            )

    def create_request(self):
        title = self.new_title.text().strip()
        description = self.new_description.toPlainText().strip()
        priority = self.new_priority.currentText()
        user_id = self.new_user.currentData()

        if not title or not description:
            QMessageBox.warning(self, "Проверка данных", "Заполните тему и описание заявки.")
            return

        db.add_request(title, description, priority, user_id)

        self.new_title.clear()
        self.new_description.clear()
        self.refresh_all()
        QMessageBox.information(self, "Готово", "Заявка успешно создана.")

    def create_assignment(self):
        request_id = self.assign_request.value()
        engineer_id = self.assign_engineer.currentData()
        comment = self.assign_comment.text().strip()

        db.assign_engineer(request_id, engineer_id, comment)
        self.assign_comment.clear()
        self.refresh_all()
        QMessageBox.information(self, "Готово", "Инженер назначен на заявку.")

    def change_status(self):
        request_id = self.status_request_id.value()
        status = self.status_value.currentText()

        db.update_request_status(request_id, status)
        self.refresh_all()
        QMessageBox.information(self, "Готово", "Статус заявки изменен.")


def main():
    app = QApplication(sys.argv)
    window = HelpDeskWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
