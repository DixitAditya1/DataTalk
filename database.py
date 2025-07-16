import sqlite3
import os
from datetime import datetime, timedelta
import random

def initialize_database():
    """Initialize sample database with predefined tables and data"""
    db_path = "sample_database.db"
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute('''
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            country TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create products table
    cursor.execute('''
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            stock_quantity INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount DECIMAL(10, 2) NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    
    # Create order_items table
    cursor.execute('''
        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (order_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    ''')
    
    # Insert sample customers
    customers_data = [
        ('John', 'Doe', 'john.doe@email.com', '555-0101', 'New York', 'NY', 'USA'),
        ('Jane', 'Smith', 'jane.smith@email.com', '555-0102', 'Los Angeles', 'CA', 'USA'),
        ('Mike', 'Johnson', 'mike.johnson@email.com', '555-0103', 'Chicago', 'IL', 'USA'),
        ('Sarah', 'Brown', 'sarah.brown@email.com', '555-0104', 'Houston', 'TX', 'USA'),
        ('David', 'Wilson', 'david.wilson@email.com', '555-0105', 'Phoenix', 'AZ', 'USA'),
        ('Lisa', 'Davis', 'lisa.davis@email.com', '555-0106', 'Philadelphia', 'PA', 'USA'),
        ('Tom', 'Miller', 'tom.miller@email.com', '555-0107', 'San Antonio', 'TX', 'USA'),
        ('Anna', 'Garcia', 'anna.garcia@email.com', '555-0108', 'San Diego', 'CA', 'USA'),
        ('Chris', 'Martinez', 'chris.martinez@email.com', '555-0109', 'Dallas', 'TX', 'USA'),
        ('Emma', 'Anderson', 'emma.anderson@email.com', '555-0110', 'San Jose', 'CA', 'USA')
    ]
    
    cursor.executemany('''
        INSERT INTO customers (first_name, last_name, email, phone, city, state, country)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', customers_data)
    
    # Insert sample products
    products_data = [
        ('Laptop Computer', 'Electronics', 999.99, 50),
        ('Smartphone', 'Electronics', 699.99, 100),
        ('Tablet', 'Electronics', 399.99, 75),
        ('Headphones', 'Electronics', 199.99, 200),
        ('Smart Watch', 'Electronics', 299.99, 150),
        ('Coffee Maker', 'Appliances', 89.99, 30),
        ('Blender', 'Appliances', 79.99, 25),
        ('Microwave', 'Appliances', 159.99, 40),
        ('Running Shoes', 'Sports', 129.99, 80),
        ('Yoga Mat', 'Sports', 39.99, 60),
        ('Basketball', 'Sports', 29.99, 45),
        ('Tennis Racket', 'Sports', 149.99, 35),
        ('Office Chair', 'Furniture', 249.99, 20),
        ('Desk Lamp', 'Furniture', 59.99, 50),
        ('Bookshelf', 'Furniture', 179.99, 15)
    ]
    
    cursor.executemany('''
        INSERT INTO products (product_name, category, price, stock_quantity)
        VALUES (?, ?, ?, ?)
    ''', products_data)
    
    # Insert sample orders
    orders_data = []
    order_items_data = []
    
    # Generate orders for the last 3 months
    start_date = datetime.now() - timedelta(days=90)
    
    for order_id in range(1, 51):  # 50 orders
        customer_id = random.randint(1, 10)
        order_date = start_date + timedelta(days=random.randint(0, 90))
        status = random.choice(['pending', 'processing', 'shipped', 'delivered', 'cancelled'])
        
        # Generate 1-5 items per order
        num_items = random.randint(1, 5)
        total_amount = 0
        
        for _ in range(num_items):
            product_id = random.randint(1, 15)
            quantity = random.randint(1, 3)
            
            # Get product price
            cursor.execute('SELECT price FROM products WHERE product_id = ?', (product_id,))
            unit_price = cursor.fetchone()[0]
            
            order_items_data.append((order_id, product_id, quantity, unit_price))
            total_amount += quantity * unit_price
        
        orders_data.append((order_id, customer_id, order_date, total_amount, status))
    
    cursor.executemany('''
        INSERT INTO orders (order_id, customer_id, order_date, total_amount, status)
        VALUES (?, ?, ?, ?, ?)
    ''', orders_data)
    
    cursor.executemany('''
        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
        VALUES (?, ?, ?, ?)
    ''', order_items_data)
    
    conn.commit()
    conn.close()
    
    return db_path

def get_database_metadata(db_path):
    """Get database schema information"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    metadata = {}
    
    # Get table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        metadata[table_name] = {}
        
        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        metadata[table_name]['columns'] = {}
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            is_nullable = not col[3]
            default_value = col[4]
            is_pk = col[5]
            
            metadata[table_name]['columns'][col_name] = {
                'type': col_type,
                'nullable': is_nullable,
                'default': default_value,
                'primary_key': bool(is_pk)
            }
        
        # Get sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        sample_data = cursor.fetchall()
        metadata[table_name]['sample_data'] = sample_data
    
    conn.close()
    return metadata
