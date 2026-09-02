import json
import sqlite3
import os

desktop_path = os.path.expanduser("~/Desktop")
db_path = os.path.join(desktop_path, "my-brain", "brain.db")
waitlist_path = os.path.join(desktop_path, "my-brain", "waitlist.json")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('physical', 'digital', 'service')) NOT NULL,
    price REAL NOT NULL,
    description TEXT,
    stock INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    zalo TEXT,
    registration_date TEXT,
    UNIQUE(phone),
    UNIQUE(zalo)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    product_id INTEGER,
    amount REAL NOT NULL,
    status TEXT NOT NULL,
    purchase_date TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
)
""")

if os.path.exists(waitlist_path):
    with open(waitlist_path, "r", encoding="utf-8") as f:
        waitlist_data = json.load(f)
        for item in waitlist_data:
            name = item.get("name")
            phone = item.get("phone")
            zalo = item.get("zalo")
            reg_date = item.get("registration_date") or item.get("date")
            cursor.execute("""
                INSERT OR IGNORE INTO customers (name, phone, zalo, registration_date)
                VALUES (?, ?, ?, ?)
            """, (name, phone, zalo, reg_date))

conn.commit()
conn.close()
print("Đã tạo thành công 3 bảng và import dữ liệu!")
