import sqlite3

def create_connection():
    conn = sqlite3.connect('ecommerce.db')
    return conn

def create_tables(conn):
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT NOT NULL,
        Password TEXT NOT NULL,
        Email TEXT,
        Address TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Description TEXT,
        Price REAL NOT NULL,
        Stock INTEGER NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER,
        TotalAmount REAL,
        OrderDate TEXT,
        FOREIGN KEY (UserID) REFERENCES Users(UserID)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OrderDetails (
        OrderDetailID INTEGER PRIMARY KEY AUTOINCREMENT,
        OrderID INTEGER,
        ProductID INTEGER,
        Quantity INTEGER,
        Price REAL,
        FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
        FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Cart (
        CartID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER,
        ProductID INTEGER,
        Quantity INTEGER,
        FOREIGN KEY (UserID) REFERENCES Users(UserID),
        FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
    )''')

    conn.commit()

def add_initial_products(conn):
    cursor = conn.cursor()
    products = [
        ('Laptop', 'A high performance laptop', 999.99, 10),
        ('Smartphone', 'Latest model smartphone', 699.99, 20),
        ('Headphones', 'Noise-cancelling headphones', 199.99, 15),
        ('Monitor', '27-inch 4K monitor', 299.99, 8),
        ('Keyboard', 'Mechanical keyboard', 89.99, 25),
    ]

    cursor.executemany('''
    INSERT INTO Products (Name, Description, Price, Stock) VALUES (?, ?, ?, ?)
    ''', products)

    conn.commit()

def setup_database():
    conn = create_connection()
    create_tables(conn)
    add_initial_products(conn)
    conn.close()

if __name__ == '__main__':
    setup_database()
