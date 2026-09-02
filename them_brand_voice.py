#!/usr/bin/env python3
"""
Script thêm nội dung mới vào bảng brand_voice.
Chạy: double-click file này (hoặc python3 them_brand_voice.py)
"""
import sqlite3
from datetime import datetime

DB_PATH = "/Users/macbook/Desktop/my-brain/brain.db"
PROMPT_PATH = "/Users/macbook/Desktop/my-brain/brand_voice_prompt.txt"

# ============================================================
# ✏️  ĐIỀN VÀO ĐÂY RỒI CHẠY
TITLE   = "Ví dụ đúng giọng — Tên bài ở đây"
CONTENT = """
Nội dung bài viết hoặc ghi chú tone mới ở đây.
Có thể nhiều dòng.
"""
# ============================================================

def add_to_db():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO brand_voice (title, content, created_at) VALUES (?, ?, ?)",
        (TITLE, CONTENT.strip(), now)
    )
    conn.commit()
    print(f"✅ Đã thêm vào DB: {TITLE}")
    conn.close()

def rebuild_prompt():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, content FROM brand_voice")
    rows = cursor.fetchall()
    conn.close()

    lines = []
    lines.append("=" * 60)
    lines.append("BRAND VOICE CỦA THƯƠNG — dùng làm context cho AI")
    lines.append("Paste đoạn này vào ĐẦU cuộc chat trước khi yêu cầu AI viết bài.")
    lines.append("=" * 60)
    lines.append("")
    for title, content in rows:
        lines.append(f"### {title}")
        lines.append(content)
        lines.append("")
    lines.append("=" * 60)
    lines.append("YÊU CẦU AI:")
    lines.append("Dựa vào brand voice trên, hãy viết [loại bài] về chủ đề [chủ đề].")
    lines.append("Giữ đúng tone: gần gũi, thẳng thắn, hài hước sâu cay.")
    lines.append("Dùng các từ đặc trưng khi phù hợp: Đây là Thương, thôi xin, quý dị, mô, mấy bà...")
    lines.append("KHÔNG dùng từ hoa mỹ, corporate, văn chương.")
    lines.append("=" * 60)

    with open(PROMPT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✅ Đã cập nhật lại brand_voice_prompt.txt")

if __name__ == "__main__":
    add_to_db()
    rebuild_prompt()
    print("\n🎉 Xong! Mở brand_voice_prompt.txt để dùng.")
    input("\nBấm Enter để đóng...")
