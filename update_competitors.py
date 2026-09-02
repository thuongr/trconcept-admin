import sqlite3

# 1. Đọc nội dung file doi-thu.md
with open("doi-thu.md", "r", encoding="utf-8") as f:
    content = f.read()

# 2. Kết nối tới file brain.db
conn = sqlite3.connect("brain.db")
cursor = conn.cursor()

# 3. Tạo bảng competitors nếu chưa có
cursor.execute("""
    CREATE TABLE IF NOT EXISTS competitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        created_at TEXT
    )
""")

# 4. Thêm dữ liệu vào bảng
cursor.execute(
    "INSERT INTO competitors (title, content, created_at) VALUES (?, ?, datetime('now', 'localtime'))",
    ("Danh sách đối thủ khóa học AI thực chiến (Chuẩn link)", content)
)

conn.commit()
conn.close()

print("🎉 Thành công! Đã cập nhật bảng competitors vào brain.db.")
