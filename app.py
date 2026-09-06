from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import json
from urllib.request import Request, urlopen
import resend

resend.api_key = "re_Mare_KysvCdu3_NwKfUhPdWkPVLWFon1kdznk"

def send_welcome_email(customer_email, customer_name):
    try:
        params = {
            "from": "TR Concept <hi@trconcept.co>",
            "to": [customer_email],
            "subject": "Welcome to AI for Real Work!",
            "html": f"""
                <p>Hi {customer_name},</p>
                <p>Welcome to AI for Real Work — I’m so glad to have you joining us!</p>
                <p>This program is not about learning AI tricks or simply chatting with ChatGPT. It’s about learning how to leverage AI to do real work — helping you save time, improve the way you work, and turn AI into a practical assistant for your day-to-day business.</p>
                <p>I’ve received your registration and will personally get in touch with you within the next 24 hours with the next steps and everything you need to get started.</p>
                <p>In the meantime, there’s nothing you need to prepare. Just come with a real task, challenge or piece of work you’d like AI to help you with — that’s where the most valuable learning happens.</p>
                <p>I’m looking forward to working with you and helping you get more out of AI, in a way that actually fits your work and your business.</p>
                <p>See you soon!</p>
                <p>Warmly,<br><b>Thuong Rejeehan</b></p>
            """,
        }
        response = resend.Emails.send(params)
        print("Email sent successfully:", response)
    except Exception as e:
        print("Error sending email:", e)
app = Flask(__name__)
app.secret_key = "super-secret-key-admin"
@app.route('/')
def index():
    return redirect('/admin')
DB_PATH = 'brain.db'

def get_remote_registrations():
    api_url = os.environ.get('WEBSITE_API_URL', 'https://api.trconcept.co').rstrip('/')
    try:
        request = Request(f'{api_url}/api/registrations?limit=500&since_days=3650')
        with urlopen(request, timeout=10) as response:
            payload = json.load(response)
        return payload.get('registrations', []) if payload.get('success') else []
    except Exception as error:
        print(f'Error loading remote registrations: {error}')
        return []

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/admin')
def admin_panel():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    customers = conn.execute("SELECT * FROM customers").fetchall()
    orders = conn.execute("""
        SELECT o.*, c.name as customer_name, p.name as product_name 
        FROM orders o 
        LEFT JOIN customers c ON o.customer_id = c.id 
        LEFT JOIN products p ON o.product_id = p.id
    """).fetchall()
    conn.close()
    registrations = get_remote_registrations()
    return render_template('admin.html', products=products, customers=customers, orders=orders, registrations=registrations)

@app.route('/product/save', methods=['POST'])
def save_product():
    p_id = request.form.get('id')
    name = request.form.get('name')
    ptype = request.form.get('type')
    price = request.form.get('price')
    stock = request.form.get('stock')
    stock_val = int(stock) if stock and stock.strip() != '' else None
    desc = request.form.get('description')

    conn = get_db_connection()
    if p_id:
        conn.execute("UPDATE products SET name=?, type=?, price=?, description=?, stock=? WHERE id=?",
                     (name, ptype, float(price), desc, stock_val, p_id))
        flash("Đã cập nhật sản phẩm thành công!", "success")
    else:
        conn.execute("INSERT INTO products (name, type, price, description, stock) VALUES (?, ?, ?, ?, ?)",
                     (name, ptype, float(price), desc, stock_val))
        flash("Đã thêm sản phẩm mới thành công!", "success")
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/product/delete/<int:id>')
def delete_product(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Đã xóa sản phẩm!", "success")
    return redirect(url_for('admin_panel'))

@app.route('/customer/save', methods=['POST'])
def save_customer():
    c_id = request.form.get('id')
    name = request.form.get('name')
    phone = request.form.get('phone') or None
    zalo = request.form.get('zalo') or None
    reg_date = request.form.get('registration_date') or None

    conn = get_db_connection()
    if c_id:
        conn.execute("UPDATE customers SET name=?, phone=?, zalo=?, registration_date=? WHERE id=?",
                     (name, phone, zalo, reg_date, c_id))
        flash("Đã cập nhật khách hàng thành công!", "success")
    else:
        try:
            conn.execute("INSERT INTO customers (name, phone, zalo, registration_date) VALUES (?, ?, ?, ?)",
                         (name, phone, zalo, reg_date))
            flash("Đã thêm khách hàng mới thành công!", "success")
        except sqlite3.IntegrityError:
            flash("Lỗi: Số điện thoại hoặc Zalo này đã tồn tại trong hệ thống!", "error")
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/customer/delete/<int:id>')
def delete_customer(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM customers WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Đã xóa khách hàng!", "success")
    return redirect(url_for('admin_panel'))

@app.route('/order/save', methods=['POST'])
def save_order():
    customer_id = request.form.get('customer_id')
    product_id = request.form.get('product_id')
    amount = request.form.get('amount')
    status = request.form.get('status')
    purchase_date = request.form.get('purchase_date') or None

    conn = get_db_connection()
    product = conn.execute("SELECT type, stock FROM products WHERE id=?", (product_id,)).fetchone()
    
    if product:
        p_type = product['type']
        current_stock = product['stock']
        if p_type == 'physical':
            if current_stock is not None and current_stock > 0:
                new_stock = current_stock - 1
                conn.execute("UPDATE products SET stock=? WHERE id=?", (new_stock, product_id))
            elif current_stock is not None and current_stock <= 0:
                flash("Cảnh báo: Sản phẩm vật lý này đã hết hàng trong kho!", "error")

    conn.execute("INSERT INTO orders (customer_id, product_id, amount, status, purchase_date) VALUES (?, ?, ?, ?, ?)",
                 (customer_id, product_id, float(amount), status, purchase_date))
    conn.commit()
    conn.close()
    flash("Đã tạo đơn hàng thành công và tự động cập nhật tồn kho!", "success")
    return redirect(url_for('admin_panel'))

@app.route('/order/delete/<int:id>')
def delete_order(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM orders WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Đã xóa đơn hàng!", "success")
    return redirect(url_for('admin_panel'))
@app.route('/order/complete/<int:order_id>', methods=['POST'])
def complete_order(order_id):
    conn = get_db_connection()
    
    # 1. Cập nhật trạng thái đơn hàng trong database (brain.db) sang 'completed'
    conn.execute("UPDATE orders SET status = 'completed' WHERE id = ?", (order_id,))
    conn.commit()
    
    # 2. Lấy thông tin email và tên của khách hàng từ đơn hàng vừa cập nhật
    order_info = conn.execute("""
        SELECT o.*, c.name as customer_name, c.email as customer_email 
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.id = ?
    """, (order_id,)).fetchone()
    
    conn.close()
    
    # 3. Nếu tìm thấy thông tin khách hàng, tiến hành gọi hàm gửi email chào mừng
    if order_info and order_info['customer_email']:
        send_welcome_email(order_info['customer_email'], order_info['customer_name'])
    
    # Quay lại trang admin sau khi hoàn tất
    return redirect(url_for('admin_panel'))
if __name__ == '__main__':
    app.run(debug=True, port=5000)