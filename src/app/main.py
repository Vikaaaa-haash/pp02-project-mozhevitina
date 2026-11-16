# Изменения для ветки feature/new-design
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'logic')) 
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QMessageBox, QComboBox, QLineEdit
)
from PySide6.QtWidgets import QDialog, QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtCore import QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'logic'))
from discount import calculate_price
# Константы для расчетов
DISCOUNT_RATE = 0.75 # Ставка скидки (25%)

# Настройка логирования
logging.basicConfig(
    filename='app.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def create_card(product, main_window):
    p_id = product[0]
    category = product[1]
    subcategory = product[2]
    image_name = product[3]
    name = product[4]
    production = product[5]
    description = product[6]
    composition = product[7]
    price = product[8]
    
    # Остаток
    try:
        stock = int(product[9]) if len(product) > 9 and product[9] is not None else 0
    except (ValueError, TypeError):
        stock = 0

    # Скидка из базы
    try:
        discount_percent = int(product[10]) if len(product) > 10 and product[10] is not None else 0
    except (ValueError, TypeError):
        discount_percent = 0

    # Считаем новую цену на основе скидки из БД 
    old_price = float(price)
    if discount_percent > 0:
        new_price = old_price - (old_price * discount_percent / 100)
    else:
        new_price = old_price

    # Картинка
    if image_name and str(image_name).strip() != "":
        image_path = f"resources/{image_name}"
    else:
        image_path = None

    if image_path and os.path.exists(image_path):
        pixmap = QPixmap(image_path)
    else:
        if image_name:
            logging.warning(f"Файл не найден: {image_name}. Использована заглушка.")
        pixmap = QPixmap("resources/picture.png")

        # ПАРА 40 
    try:
        stock_val = int(stock)
    except (ValueError, TypeError):
        stock_val = 0

    # 1. Если товара нет на складе (stock == 0) -> голубой
    if stock_val == 0:
        bg_color = "#ADD8E6" 
    # 2. Иначе, если остаток меньше 3 -> красный
    elif stock_val < 3:
        bg_color = "#FF8080"
    # 3. Иначе -> белый
    else:
        bg_color = "#FFFFFF"

    # Создание карточки
    card = QWidget()
    card = QWidget()
    card.setStyleSheet(f"""
        QWidget {{
            background-color: {bg_color};
            border: 1px solid #70B2AF;
            border-radius: 5px;
        }}
    """)
    card.setMinimumHeight(120) 
    main_layout = QHBoxLayout()
    main_layout.setContentsMargins(15, 15, 15, 15)
    
    # Картинка
    image_label = QLabel()
    image_label.setFixedSize(100, 100)
    image_label.setAlignment(Qt.AlignCenter)
    if not pixmap.isNull():
        image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    else:
        image_label.setText("[НЕТ ФОТО]")
    main_layout.addWidget(image_label)
    
    # Текстовая часть
    text_layout = QVBoxLayout()
    text_layout.setAlignment(Qt.AlignTop) # Прижимаем текст к верху, чтобы он не расползался
    text_layout.setSpacing(5)
    
    title = QLabel(f"{production} | {name}")
    title.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000; border: none;")
    text_layout.addWidget(title)
    
    cat_label = QLabel(f"Категория: {category}")
    cat_label.setStyleSheet("color: #555555; border: none;")
    text_layout.addWidget(cat_label)
    
    comp_label = QLabel(f"Состав: {composition}")
    comp_label.setStyleSheet("color: #555555; border: none;")
    text_layout.addWidget(comp_label)
    
    stock_label = QLabel(f"В наличии: {stock} шт.")
    text_color = "#8B0000" if stock_val < 3 else "#555555"
    stock_label.setStyleSheet(f"color: {text_color}; font-weight: bold; border: none;")
    text_layout.addWidget(stock_label)
    
    main_layout.addLayout(text_layout)
    
    # БЛОК С ЦЕНАМИ (ПАРА 40)
    price_layout = QVBoxLayout()
    price_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

    # 1. СТАРАЯ ЦЕНА (Перечеркнутая и красная)
    old_price_label = QLabel(f"<s>{int(old_price)} ₽</s>")
    old_price_label.setStyleSheet("color: red; font-size: 14px; border: none;")
    old_price_label.setAlignment(Qt.AlignRight)
    price_layout.addWidget(old_price_label)

    # 2. Скрываем старую цену, если скидки нет
    if discount_percent > 0 and stock_val > 0:
        old_price_label.show()
    else:
        old_price_label.hide()

    # 3. ИТОГОВАЯ ЦЕНА
    if discount_percent > 0:
        new_price_label = QLabel(f"<nobr>{int(new_price)} ₽ <span style='color: #2E8B57; font-size: 14px;'>(-{discount_percent}%)</span></nobr>")
    else:
        new_price_label = QLabel(f"{int(new_price)} ₽")
        
    if stock_val == 0:
        # Если нет на складе — серая цена (игнорируем скидку)
        new_price_label.setStyleSheet("color: #888888; font-weight: bold; font-size: 18px; border: none;")
    elif discount_percent > 15:
        # Если есть на складе и скидка > 15% — зеленая цена
        new_price_label.setStyleSheet("color: #2E8B57; font-weight: bold; font-size: 18px; border: none;")
    else:
        # Иначе — черная цена
        new_price_label.setStyleSheet("color: black; font-weight: bold; font-size: 18px; border: none;")
        
    new_price_label.setAlignment(Qt.AlignRight)
    price_layout.addWidget(new_price_label)

    main_layout.addLayout(price_layout)
    card.setLayout(main_layout)

    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    effect = QGraphicsOpacityEffect(card)
    card.setGraphicsEffect(effect)
    
    card.anim = QPropertyAnimation(effect, b"opacity")
    card.anim.setDuration(200)
    
    def enter_event(event):
        card.anim.setStartValue(1.0)
        card.anim.setEndValue(0.9) # Делаем прозрачность чуть меньше, чтобы не было резко
        card.anim.start()
        QWidget.enterEvent(card, event)
        
    def leave_event(event):
        card.anim.setStartValue(0.9)
        card.anim.setEndValue(1.0)
        card.anim.start()
        QWidget.leaveEvent(card, event)

    card.enterEvent = enter_event
    card.leaveEvent = leave_event

    # --- ДОМАШНЕЕ ЗАДАНИЕ: БЛОКИРОВКА ---
    # Если товара нет на складе, делаем карточку полупрозрачной (визуальная блокировка)
    if stock_val == 0:
        card.setEnabled(False)
        card.setStyleSheet(card.styleSheet() + " opacity: 0.7;") 

    # Клик по карточке открывает диалог
    card.mousePressEvent = lambda event: main_window.open_product_dialog(product)

    return card


class ProductDialog(QDialog):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle(f"Карточка товара — {product[4]}")
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # Информация о товаре
        layout.addWidget(QLabel(f"<b>{product[4]}</b>"))
        layout.addWidget(QLabel(f"Категория: {product[1]}"))
        layout.addWidget(QLabel(f"Состав: {product[7]}"))
        layout.addWidget(QLabel(f"Цена: {product[8]} ₽"))
        layout.addWidget(QLabel(f"В наличии: {product[9]} шт."))
        
        # Выбор количества
        layout.addWidget(QLabel("Количество:"))
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, int(product[9]) if product[9] > 0 else 1)
        layout.addWidget(self.qty_spin)
        
        # Кнопка "Добавить в корзину"
        self.add_btn = QPushButton("Добавить в корзину")
        self.add_btn.clicked.connect(self.accept)
        layout.addWidget(self.add_btn)
        
        self.setLayout(layout)

    def get_data(self):
        return self.qty_spin.value()

class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name=None):
        super().__init__()
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
                font-family: Calibri;
            }
        """)
        self.role_id = role_id
        self.full_name = full_name
        self.db = Database()
        
        self.setWindowTitle("Ювелирный — Каталог")
        self.resize(900, 700)
        self.setWindowIcon(QIcon("resources/icon.ico"))
        
        self.setup_ui()
        self.setup_role_interface()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)
        
        # --- HEADER ---
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #D2F6E7;")
        top_layout = QHBoxLayout(header_widget)
        top_layout.setContentsMargins(10, 5, 10, 5) 
        
        logo = QLabel()
        pixmap = QPixmap("resources/logo.png")
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        top_layout.addWidget(logo)
        
        title = QLabel("Ювелирный магазин")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #70B2AF; margin-left: 10px;")
        top_layout.addWidget(title)
        
        top_layout.addStretch()

        if self.full_name:
            self.icon_label = QLabel()
            icon = self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxInformation)
            self.icon_label.setPixmap(icon.pixmap(24, 24))
            top_layout.addWidget(self.icon_label)

            self.fio_label = QLabel(f"{self.full_name} ({self.role_id})")
            self.fio_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333; margin-right: 15px; margin-left: 5px;")
            top_layout.addWidget(self.fio_label)

        # Кнопки ролей
        self.order_button = QPushButton("Оформить заказ")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")
        
        # Привязка кнопок к действиям
        self.order_button.clicked.connect(lambda: self.switch_page(3))  # Оформить заказ -> Корзина
        self.manager_button.clicked.connect(lambda: self.switch_page(1)) # Заказы -> Страница заказов
        self.admin_button.clicked.connect(lambda: self.switch_page(1))   # Админ-панель -> Туда же

        for btn in [self.order_button, self.manager_button, self.admin_button]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #70B2AF;
                    color: white;
                    font-family: Calibri;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #5a9c99;
                }
            """)

        
        top_layout.addWidget(self.order_button)
        top_layout.addWidget(self.manager_button)
        top_layout.addWidget(self.admin_button)

        # Кнопка Выход
        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet("background-color: #FF8080; color: white; font-weight: bold; padding: 5px 15px;")
        self.logout_button.clicked.connect(self.logout)
        self.back_button = QPushButton("Назад")
        self.back_button.setStyleSheet("background-color: #FFB347; color: white; font-weight: bold; padding: 5px 15px;")
        self.back_button.clicked.connect(self.go_back)
        top_layout.addWidget(self.back_button)
        top_layout.addWidget(self.logout_button)
        
        main_layout.addWidget(header_widget)


        filter_layout = QHBoxLayout()
        
        # 1. Поиск
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию...")
        self.search_input.textChanged.connect(self.load_products)
        filter_layout.addWidget(self.search_input, 2) # 2 - чтобы поиск занимал больше места
        
        # 2. Фильтр по категориям
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все категории")
        categories = self.db.get_categories() 
        self.filter_combo.addItems(categories)
        self.filter_combo.currentIndexChanged.connect(self.load_products)
        filter_layout.addWidget(self.filter_combo, 1)
        
        # 3. Сортировка
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По возрастанию", "По убыванию", "По названию (А-Я)"])
        self.sort_combo.currentIndexChanged.connect(self.load_products)
        filter_layout.addWidget(self.sort_combo, 1)

        # Фильтр по производителю 
        self.prod_combo = QComboBox()
        self.prod_combo.addItem("Все производители")
        productions = self.db.get_productions()
        self.prod_combo.addItems(productions)
        self.prod_combo.currentIndexChanged.connect(self.load_products)
        filter_layout.addWidget(self.prod_combo, 1) 
        
        # Добавляем всю панель в главный слой
        main_layout.addLayout(filter_layout)

        # --- НАВИГАЦИЯ (QStackedWidget) ---
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Страница 0: Каталог
        self.catalog_page = QWidget()
        catalog_page_layout = QVBoxLayout()
        catalog_page_layout.setContentsMargins(0, 0, 0, 0)
        
        #  старый каталог 
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        catalog_container = QWidget()
        self.catalog_layout = QVBoxLayout() 
        self.catalog_layout.setSpacing(10) 
        self.catalog_layout.setAlignment(Qt.AlignTop)
        catalog_container.setLayout(self.catalog_layout) 
        self.scroll.setWidget(catalog_container)
        
        catalog_page_layout.addWidget(self.scroll)
        self.catalog_page.setLayout(catalog_page_layout)
        self.stacked_widget.addWidget(self.catalog_page) # Индекс 0

        # Страница 1: Заказы (таблица)
        self.orders_page = QWidget()
        orders_layout = QVBoxLayout()
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(4)
        self.orders_table.setHorizontalHeaderLabels(["Номер", "Дата", "Клиент", "Сумма"])
        orders_layout.addWidget(self.orders_table)
        self.orders_page.setLayout(orders_layout)
        self.stacked_widget.addWidget(self.orders_page) # Индекс 1


        # Страница 3: Корзина
        self.cart_page = QWidget()
        cart_layout = QVBoxLayout()
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["Товар", "Кол-во", "Цена", "Сумма"])
        cart_layout.addWidget(self.cart_table)
        
        self.checkout_btn = QPushButton("Оформить заказ")
        self.checkout_btn.clicked.connect(self.checkout)
        cart_layout.addWidget(self.checkout_btn)
        
        self.cart_page.setLayout(cart_layout)
        self.stacked_widget.addWidget(self.cart_page) # Индекс 3

        # Добавляем QStackedWidget в главный слой
        main_layout.addWidget(self.stacked_widget)
        
        # Говорим главному слою, что каталог должен занимать всё место
        main_layout.setStretchFactor(self.stacked_widget, 1)

        self.load_products()

        self.load_orders() # Загружаем заказы в таблицу

    def setup_role_interface(self):
        self.order_button.hide()
        self.manager_button.hide()
        self.admin_button.hide()
        
        if self.role_id == "Клиент":
            self.order_button.show()
        elif self.role_id == "Менеджер":
            self.order_button.show()
            self.manager_button.show()
        elif self.role_id == "Администратор":
            self.order_button.show()
            self.manager_button.show()
            self.admin_button.show()

    def load_products(self):
        """
        Загружает товары из базы данных и отрисовывает карточки в каталоге.
        Учитывает текущие значения фильтров, поиска и сортировки.
        """
        # 1. Получаем значения из фильтров
        search_text = self.search_input.text()
        current_category = self.filter_combo.currentText()
        current_prod = self.prod_combo.currentText()
        current_sort = self.sort_combo.currentText()
        
        # 2. Очищаем каталог
        while self.catalog_layout.count():
            item = self.catalog_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        # 3. Получаем все товары из БД
        products = self.db.get_products(search=search_text, category=current_category, production=current_prod, sort_order=current_sort)
        

        unique_products = []
        seen_names = set() 
        
        for product in products:
            name = product[4] 
            if name not in seen_names:
                unique_products.append(product)
                seen_names.add(name)
                
        # 5. Рисуем только уникальные карточки
        for product in unique_products:
            card = create_card(product, self)
            self.catalog_layout.addWidget(card)
            
        self.catalog_layout.addStretch()

    def logout(self):
        reply = QMessageBox.question(
            self, "Выход", "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            from login_window import LoginWindow
            self.login_window = LoginWindow(self.db)
            self.login_window.show()
            self.close()

    def load_orders(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT order_id, order_date, user_id, order_id FROM orders")
            orders = cursor.fetchall()
            self.orders_table.setRowCount(len(orders))
            for row, order in enumerate(orders):
                self.orders_table.setItem(row, 0, QTableWidgetItem(str(order[0])))
                self.orders_table.setItem(row, 1, QTableWidgetItem(str(order[1])))
                self.orders_table.setItem(row, 2, QTableWidgetItem(str(order[2])))
                self.orders_table.setItem(row, 3, QTableWidgetItem(str(order[3])))
            cursor.close()
            self.db.release_connection(conn)
        except Exception as e:
            print(f"Ошибка загрузки заказов: {e}")

    def open_product_dialog(self, product):
            dialog = ProductDialog(product, self)
            if dialog.exec():
              qty = dialog.get_data()
              self.add_to_cart(product, qty)

    def add_to_cart(self, product, qty):
        # Добавляем товар в таблицу корзины
        row = self.cart_table.rowCount()
        self.cart_table.insertRow(row)
        self.cart_table.setItem(row, 0, QTableWidgetItem(product[4]))
        self.cart_table.setItem(row, 1, QTableWidgetItem(str(qty)))
        self.cart_table.setItem(row, 2, QTableWidgetItem(str(product[8])))
        self.cart_table.setItem(row, 3, QTableWidgetItem(str(int(product[8]) * qty)))
        
        # Переключаемся на корзину
        self.switch_page(3)

    def checkout(self):
        if self.cart_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Корзина пуста")
            return
        
        # Сохраняем заказ в БД 
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO orders (order_date, user_id) VALUES (CURRENT_DATE, 1) RETURNING order_id")
            order_id = cursor.fetchone()[0]
            
            for row in range(self.cart_table.rowCount()):
                name = self.cart_table.item(row, 0).text()
                qty = int(self.cart_table.item(row, 1).text())
                price = float(self.cart_table.item(row, 2).text())
                cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, (SELECT id FROM products WHERE name = %s LIMIT 1), %s, %s)", (order_id, name, qty, price))
            
            conn.commit()
            cursor.close()
            self.db.release_connection(conn)
            
            QMessageBox.information(self, "Успех", "Заказ оформлен!")
            self.cart_table.setRowCount(0)
            self.switch_page(0)
            self.load_products()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка оформления: {e}")        

    def go_back(self):
        # Всегда возвращаемся в каталог (индекс 0)
        self.switch_page(0)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        if index == 0:
            self.setWindowTitle("Ювелирный — Каталог")
        elif index == 1:
            self.setWindowTitle("Ювелирный — Заказы")


    def closeEvent(self, event):
        if self.db:
            self.db.close_all()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    from login_window import LoginWindow
    
    db = Database()
    window = LoginWindow(db)
    window.show()
    
    sys.exit(app.exec())