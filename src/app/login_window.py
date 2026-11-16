from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt

class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        
        self.setWindowTitle("Авторизация — Ювелирный")
        self.resize(350, 200)
        from PySide6.QtGui import QIcon
        self.setWindowIcon(QIcon("resources/icon.ico"))
        
        layout = QVBoxLayout()
        
        # Логин
        layout.addWidget(QLabel("Логин:"))
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        layout.addWidget(self.login_input)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Войти")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #70B2AF;
                color: white;
                font-family: Calibri;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        self.login_button.clicked.connect(self.check_login)
        btn_layout.addWidget(self.login_button)
        
        # Кнопка ГОСТЬ 
        self.cancel_button = QPushButton("Войти как гость")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #70B2AF;
                color: white;
                font-family: Calibri;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a9c99;
            }
        """)
        self.cancel_button.clicked.connect(self.login_as_guest)
        btn_layout.addWidget(self.cancel_button)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def check_login(self):
        login = self.login_input.text().strip()
        
        # Проверка на пустоту
        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин (пробелы не считаются)")
            return
            
        # Проверка длины (минимум 3 символа)
        if len(login) < 3:
            QMessageBox.warning(self, "Ошибка", "Логин должен содержать минимум 3 символа")
            return

        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, role, last_name, first_name, middle_name 
                FROM users WHERE login = %s
            """, (login,))
            result = cursor.fetchone()
            cursor.close()
            self.db.release_connection(conn)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка запроса: {e}")
            return

        if result is None:
            QMessageBox.critical(self, "Ошибка", "Пользователь не найден")
        else:
            self.user_id = result[0]
            self.role_id = result[1] 
            
            # Формируем ФИО
            last_name = result[2] if result[2] else ""
            first_name = result[3] if result[3] else ""
            middle_name = result[4] if result[4] else ""
            
            self.full_name = f"{last_name} {first_name} {middle_name}".strip()
            
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {self.full_name}!")
            
            from main import MainWindow
            self.main_window = MainWindow(role_id=self.role_id, full_name=self.full_name)
            self.main_window.show()
            self.close()


    def login_as_guest(self):
        from main import MainWindow
        self.main_window = MainWindow(role_id=None, full_name=None)
        self.main_window.show()
        self.close()