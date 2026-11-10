import psycopg2

def calculate_price(product_name, base_price):
    if not isinstance(product_name, str):
        print("Ошибка: название товара должно быть строкой")
        return None
    if not isinstance(base_price, (int, float)):
        print("Ошибка: цена должна быть числом")
        return None
    if base_price <= 0:
        print("Ошибка: цена должна быть > 0")
        return None
    conn = None
    cursor = None
    
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, database="practice_db",
            user="postgres", password="123"
        )
        cursor = conn.cursor()
        
        # 2. SQL-запрос (используем product_name, так как в базе нет product_id)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM order_items oi 
            JOIN orders o ON oi.order_id = o.order_id 
            WHERE oi.product_name = %s 
              AND o.order_date >= CURRENT_DATE - INTERVAL '1 month'
        """, (product_name,))
        
        result = cursor.fetchone()

        if result is None:
            print("Ошибка: нет результата")
            return None
            
        orders_count = result[0]
        orders_count = result[0]
        
        if orders_count == 0:
            return base_price * 0.75
        else:
            return base_price
            
    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")
        return None
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    result = calculate_price('Кольцо Линия', 2990)
    print(f"Итоговая цена: {result}")