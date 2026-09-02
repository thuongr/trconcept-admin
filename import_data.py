import json
import sqlite3
import os

# Trỏ trực tiếp tuyệt đối vào đúng thư mục my-brain ngoài Desktop
BASE_DIR = "/Users/macbook/Desktop/my-brain"
DB_PATH = os.path.join(BASE_DIR, "brain.db")
JSON_PATH = os.path.join(BASE_DIR, "waitlist.json")

def import_json_to_db():
    if not os.path.exists(JSON_PATH):
        print(f"LỖI: Không tìm thấy file tại đường dẫn: {JSON_PATH}")
        return

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for item in data:
        # 1. Thêm khách hàng
        cursor.execute("""
            INSERT OR IGNORE INTO customers (name, phone, zalo, registration_date)
            VALUES (?, ?, ?, ?)
        """, (item.get("name"), item.get("phone"), item.get("zalo"), item.get("registration_date")))
        
        cursor.execute("SELECT id FROM customers WHERE phone = ?", (item.get("phone"),))
        cust_row = cursor.fetchone()
        customer_id = cust_row[0] if cust_row else None

        # 2. Thêm sản phẩm (khóa học)
        prod_name = item.get("product_name")
        cursor.execute("SELECT id FROM products WHERE name = ?", (prod_name,))
        prod_row = cursor.fetchone()
        
        if prod_row:
            product_id = prod_row[0]
        else:
            cursor.execute("""
                INSERT INTO products (name, type, price, stock, description)
                VALUES (?, ?, ?, ?, ?)
            """, (
                prod_name,
                item.get("product_type"),
                item.get("price"),
                item.get("stock"),
                "Khóa học AI tại trconcept.co"
            ))
            product_id = cursor.lastrowid

        # 3. Thêm đơn hàng
        if customer_id and product_id:
            cursor.execute("""
                INSERT INTO orders (customer_id, product_id, amount, status, purchase_date)
                VALUES (?, ?, ?, ?, ?)
            """, (
                customer_id,
                product_id,
                item.get("price"),
                item.get("order_status"),
                item.get("registration_date")
            ))

    conn.commit()
    conn.close()
    print("HOÀN TẤT: Đã nạp thành công 7 học viên vào database!")

if __name__ == '__main__':
    import_json_to_db()