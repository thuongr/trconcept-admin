from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "super-secret-key-admin"

DB_PATH = 'brain.db'
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
    return render_template('admin.html', products=products, customers=customers, orders=orders)

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)