import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("inventory.db")

# Create a cursor
cursor = conn.cursor()

# Create the inventory table
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    aisle_location TEXT NOT NULL,
    stock_count INTEGER NOT NULL,
    base_price REAL NOT NULL,
    expiration_days INTEGER NOT NULL
)
""")

# Insert supermarket inventory
products = [
    ("Milk 500ml", "Aisle 1", 40, 70.00, 5),
    ("Milk 1L", "Aisle 1", 30, 120.00, 6),
    ("Bread", "Aisle 2", 25, 65.00, 3),
    ("White Bread", "Aisle 2", 20, 70.00, 4),
    ("Avocado", "Aisle 3", 50, 30.00, 2),
    ("Bananas", "Aisle 3", 60, 15.00, 3),
    ("Apples", "Aisle 3", 45, 25.00, 7),
    ("Rice 2kg", "Aisle 4", 35, 350.00, 180),
    ("Sugar 2kg", "Aisle 4", 40, 320.00, 200),
    ("Cooking Oil 1L", "Aisle 5", 30, 280.00, 365),
    ("Maize Flour 2kg", "Aisle 6", 50, 180.00, 120),
    ("Biscuits", "Aisle 7", 55, 100.00, 90),
    ("Soda 500ml", "Aisle 8", 70, 80.00, 120),
    ("Orange Juice 1L", "Aisle 8", 25, 220.00, 20),
    ("Yoghurt 500ml", "Aisle 9", 30, 150.00, 10)
]

# Insert the products into the inventory table
cursor.executemany("""
INSERT INTO inventory
(product_name, aisle_location, stock_count, base_price, expiration_days)
VALUES (?, ?, ?, ?, ?)
""", products)

# Save the changes
conn.commit()

# Close the database
conn.close()

print("Inventory database created successfully.")
print("Inventory table created successfully.")
print("Sample supermarket products inserted successfully.")