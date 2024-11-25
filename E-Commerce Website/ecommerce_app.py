
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class EcommerceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("E-commerce Management System")

        # Connect to database
        self.conn = self.create_connection()
        self.cursor = self.conn.cursor()

        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # User ID for logged-in user
        self.user_id = None

        # Create widgets
        self.create_widgets()

    def create_connection(self):
        conn = sqlite3.connect('ecommerce.db')
        return conn

    def create_widgets(self):
        # Add login/register buttons
        self.login_button = ttk.Button(self.main_frame, text="Login", command=self.login)
        self.login_button.grid(row=0, column=0, padx=10, pady=10)

        self.register_button = ttk.Button(self.main_frame, text="Register", command=self.register)
        self.register_button.grid(row=0, column=1, padx=10, pady=10)

        # Add product catalog button
        self.catalog_button = ttk.Button(self.main_frame, text="Product Catalog", command=self.view_catalog)
        self.catalog_button.grid(row=0, column=2, padx=10, pady=10)

        # Add view cart button
        self.view_cart_button = ttk.Button(self.main_frame, text="View Cart", command=self.view_cart)
        self.view_cart_button.grid(row=0, column=3, padx=10, pady=10)

    def login(self):
        # Create login window
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")

        ttk.Label(self.login_window, text="Username").grid(row=0, column=0, padx=10, pady=10)
        self.username_entry = ttk.Entry(self.login_window)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.login_window, text="Password").grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = ttk.Entry(self.login_window, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.login_submit_button = ttk.Button(self.login_window, text="Login", command=self.check_login)
        self.login_submit_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        query = "SELECT UserID FROM Users WHERE Username = ? AND Password = ?"
        self.cursor.execute(query, (username, password))
        user = self.cursor.fetchone()

        if user:
            self.user_id = user[0]
            messagebox.showinfo("Login Success", "Welcome, {}".format(username))
            self.login_window.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def register(self):
        # Create register window
        self.register_window = tk.Toplevel(self.root)
        self.register_window.title("Register")

        ttk.Label(self.register_window, text="Username").grid(row=0, column=0, padx=10, pady=10)
        self.new_username_entry = ttk.Entry(self.register_window)
        self.new_username_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.register_window, text="Password").grid(row=1, column=0, padx=10, pady=10)
        self.new_password_entry = ttk.Entry(self.register_window, show="*")
        self.new_password_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.register_window, text="Email").grid(row=2, column=0, padx=10, pady=10)
        self.email_entry = ttk.Entry(self.register_window)
        self.email_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self.register_window, text="Address").grid(row=3, column=0, padx=10, pady=10)
        self.address_entry = ttk.Entry(self.register_window)
        self.address_entry.grid(row=3, column=1, padx=10, pady=10)

        self.register_submit_button = ttk.Button(self.register_window, text="Register", command=self.create_user)
        self.register_submit_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def create_user(self):
        username = self.new_username_entry.get()
        password = self.new_password_entry.get()
        email = self.email_entry.get()
        address = self.address_entry.get()

        query = "INSERT INTO Users (Username, Password, Email, Address) VALUES (?, ?, ?, ?)"
        self.cursor.execute(query, (username, password, email, address))
        self.conn.commit()

        messagebox.showinfo("Registration Success", "User registered successfully")
        self.register_window.destroy()

    def view_catalog(self):
        # Create catalog window
        self.catalog_window = tk.Toplevel(self.root)
        self.catalog_window.title("Product Catalog")

        query = "SELECT * FROM Products"
        self.cursor.execute(query)
        products = self.cursor.fetchall()

        for index, product in enumerate(products):
            ttk.Label(self.catalog_window, text=product[1]).grid(row=index, column=0, padx=10, pady=10)
            ttk.Label(self.catalog_window, text="${:.2f}".format(product[3])).grid(row=index, column=1, padx=10, pady=10)
            add_to_cart_button = ttk.Button(self.catalog_window, text="Add to Cart", command=lambda p=product: self.add_to_cart(p))
            add_to_cart_button.grid(row=index, column=2, padx=10, pady=10)

    def add_to_cart(self, product):
        if self.user_id is None:
            messagebox.showerror("Error", "You must be logged in to add products to your cart.")
            return

        product_id, _, _, price, _ = product
        query = "INSERT INTO Cart (UserID, ProductID, Quantity) VALUES (?, ?, 1)"
        self.cursor.execute(query, (self.user_id, product_id))
        self.conn.commit()
        messagebox.showinfo("Success", "Product added to cart.")

    def view_cart(self):
        if self.user_id is None:
            messagebox.showerror("Error", "You must be logged in to view your cart.")
            return

        # Create cart window
        self.cart_window = tk.Toplevel(self.root)
        self.cart_window.title("Cart")

        query = '''
        SELECT Products.Name, Products.Price, Cart.Quantity, Cart.CartID
        FROM Cart
        JOIN Products ON Cart.ProductID = Products.ProductID
        WHERE Cart.UserID = ?
        '''
        self.cursor.execute(query, (self.user_id,))
        cart_items = self.cursor.fetchall()

        total_amount = 0

        for index, item in enumerate(cart_items):
            name, price, quantity, cart_id = item
            total_price = price * quantity
            total_amount += total_price

            ttk.Label(self.cart_window, text=name).grid(row=index, column=0, padx=10, pady=10)
            ttk.Label(self.cart_window, text="${:.2f}".format(price)).grid(row=index, column=1, padx=10, pady=10)
            ttk.Label(self.cart_window, text=quantity).grid(row=index, column=2, padx=10, pady=10)
            ttk.Label(self.cart_window, text="${:.2f}".format(total_price)).grid(row=index, column=3, padx=10, pady=10)
            remove_button = ttk.Button(self.cart_window, text="Remove", command=lambda cid=cart_id: self.remove_from_cart(cid))
            remove_button.grid(row=index, column=4, padx=10, pady=10)

        ttk.Label(self.cart_window, text="Total Amount: ${:.2f}".format(total_amount)).grid(row=len(cart_items), column=0, columnspan=4, padx=10, pady=10)
        checkout_button = ttk.Button(self.cart_window, text="Checkout", command=self.checkout)
        checkout_button.grid(row=len(cart_items)+1, column=0, columnspan=4, padx=10, pady=10)

    def remove_from_cart(self, cart_id):
        query = "DELETE FROM Cart WHERE CartID = ?"
        self.cursor.execute(query, (cart_id,))
        self.conn.commit()
        messagebox.showinfo("Success", "Item removed from cart.")
        self.cart_window.destroy()
        self.view_cart()

    def checkout(self):
        if self.user_id is None:
            messagebox.showerror("Error", "You must be logged in to checkout.")
            return

        query = '''
        SELECT Products.ProductID, Products.Price, Cart.Quantity
        FROM Cart
        JOIN Products ON Cart.ProductID = Products.ProductID
        WHERE Cart.UserID = ?
        '''
        self.cursor.execute(query, (self.user_id,))
        cart_items = self.cursor.fetchall()

        if not cart_items:
            messagebox.showinfo("Empty Cart", "Your cart is empty.")
            return

        total_amount = sum(item[1] * item[2] for item in cart_items)
        order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.cursor.execute("INSERT INTO Orders (UserID, TotalAmount, OrderDate) VALUES (?, ?, ?)", (self.user_id, total_amount, order_date))
        order_id = self.cursor.lastrowid

        for item in cart_items:
            product_id, price, quantity = item
            self.cursor.execute("INSERT INTO OrderDetails (OrderID, ProductID, Quantity, Price) VALUES (?, ?, ?, ?)", (order_id, product_id, quantity, price))

        self.cursor.execute("DELETE FROM Cart WHERE UserID = ?", (self.user_id,))
        self.conn.commit()

        messagebox.showinfo("Success", "Order placed successfully.")
        self.cart_window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EcommerceApp(root)
    root.mainloop()
