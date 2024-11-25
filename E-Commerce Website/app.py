from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import datetime 

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('catalog'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Users WHERE Username = ? AND Password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['UserID']
            return redirect(url_for('catalog'))
        else:
            return 'Invalid credentials'
    return render_template('login.html', title="Login")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        address = request.form['address']
        conn = get_db_connection()
        conn.execute('INSERT INTO Users (Username, Password, Email, Address) VALUES (?, ?, ?, ?)', (username, password, email, address))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html', title="Register")

@app.route('/catalog')
def catalog():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM Products').fetchall()
    conn.close()
    return render_template('catalog.html', products=products, title="Catalog")

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('INSERT INTO Cart (UserID, ProductID, Quantity) VALUES (?, ?, 1)', (session['user_id'], product_id))
    conn.commit()
    conn.close()
    return redirect(url_for('catalog'))

@app.route('/view_cart')
def view_cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cart_items = conn.execute('''
        SELECT Products.Name, Products.Price, Cart.Quantity, Cart.CartID
        FROM Cart
        JOIN Products ON Cart.ProductID = Products.ProductID
        WHERE Cart.UserID = ?
    ''', (session['user_id'],)).fetchall()
    total_amount = sum(item['Price'] * item['Quantity'] for item in cart_items)
    conn.close()
    return render_template('cart.html', cart_items=cart_items, total_amount=total_amount, title="Cart")

@app.route('/remove_from_cart/<int:cart_id>')
def remove_from_cart(cart_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM Cart WHERE CartID = ?', (cart_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_cart'))

@app.route('/checkout')
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    
    # Fetch cart items for the user
    cart_items = conn.execute('''
        SELECT Products.ProductID, Products.Price, Cart.Quantity
        FROM Cart
        JOIN Products ON Cart.ProductID = Products.ProductID
        WHERE Cart.UserID = ?
    ''', (user_id,)).fetchall()
    
    if not cart_items:
        return 'Your cart is empty, cannot proceed to checkout.'

    # Calculate total amount
    total_amount = sum(item['Price'] * item['Quantity'] for item in cart_items)
    
    # Insert into Orders table
    order_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute('''
        INSERT INTO Orders (UserID, TotalAmount, OrderDate)
        VALUES (?, ?, ?)
    ''', (user_id, total_amount, order_date))
    
    # Get the last inserted OrderID
    order_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    # Insert each cart item into OrderDetails table
    for item in cart_items:
        conn.execute('''
            INSERT INTO OrderDetails (OrderID, ProductID, Quantity, Price)
            VALUES (?, ?, ?, ?)
        ''', (order_id, item['ProductID'], item['Quantity'], item['Price']))

    # Clear the user's cart after successful order placement
    conn.execute('DELETE FROM Cart WHERE UserID = ?', (user_id,))
    
    conn.commit()
    conn.close()
    
    return 'Checkout Complete! Your order has been placed.'

if __name__ == '__main__':
    app.run(debug=True)
