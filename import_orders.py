import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'app'))
import openpyxl
from database import Database

def import_orders():
    # Читаем файл
    wb = openpyxl.load_workbook("docs-import/Orders_import.xlsx")
    sheet = wb.active
    
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Словарь для отслеживания созданных заказов (чтобы не дублировать)
    created_orders = {}
    
    print("Начинаю импорт заказов...")
    
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]: continue
        
        order_num = row[0]
        order_date = row[1]
        fio = row[2]
        
        # Ищем ID клиента по ФИО (склеиваем Фамилию Имя Отчество)
        cursor.execute("SELECT id FROM users WHERE last_name || ' ' || first_name || ' ' || middle_name = %s", (fio,))
        user_res = cursor.fetchone()
        user_id = user_res[0] if user_res else 1 # Если не нашли, ставим первого
        
        # Если заказа еще нет в базе, создаем его
        if order_num not in created_orders:
            cursor.execute("INSERT INTO orders (order_date, user_id) VALUES (%s, %s) RETURNING order_id", (order_date, user_id))
            real_order_id = cursor.fetchone()[0]
            created_orders[order_num] = real_order_id
            
        real_order_id = created_orders[order_num]
        
        # Данные для состава заказа
        product_name = row[4]
        quantity = row[7]
        price = row[8]
        
        # Ищем ID товара по названию
        cursor.execute("SELECT id FROM products WHERE name = %s LIMIT 1", (product_name,))
        prod_res = cursor.fetchone()
        
        if prod_res:
            product_id = prod_res[0]
            # Добавляем строку в состав заказа
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price) 
                VALUES (%s, %s, %s, %s)
            """, (real_order_id, product_id, quantity, price))
        else:
            print(f"Товар не найден: {product_name}")

    conn.commit()
    cursor.close()
    db.release_connection(conn)
    print(f"ГОТОВО! Создано уникальных заказов: {len(created_orders)}")

if __name__ == "__main__":
    import_orders()